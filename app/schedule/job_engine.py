#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/20 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : job_engine.py
# @Project : Soybean-backend
"""
定时任务执行引擎：把 scheduler_job 表配置变成 AsyncIOScheduler 里真正会跑的 job。

- 注册：build_trigger 按 period_type/period_interval/first_run_date+time 构造 IntervalTrigger
- 执行：subprocess 拉起脚本（隔离、可采集输出、可超时终止），运行历史写 scheduler_job_run_log
- 启停：start/stop 修改 enabled 并同步注册/注销调度器；stop 会终止正在运行的实例
- 重启恢复：register_all_jobs 在 lifespan 里调用，从 DB 重建全部启用任务
"""
import json
import os
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timedelta

from apscheduler.triggers.interval import IntervalTrigger

from dao.scheduler_job_info import SchedulerJobDao
from dao.scheduler_job_run_log_info import SchedulerJobRunLogDao
from dao.script_info import ScriptInfoDao
from utils.loging_util import logger

SCRIPT_TIMEOUT_SECONDS = 2 * 60 * 60   # 单次运行超时（秒），超时强杀
OUTPUT_SUMMARY_CHARS = 1000            # 运行日志表 output 字段保留的输出尾部字符数
LOG_RETENTION_DAYS = 30                # 运行输出日志文件保留天数
JOB_KEY_PREFIX = "scheduler_job_"

# 运行中的实例：job_id -> Popen（用于 stop 时终止）
_running = {}

_PERIOD_TO_KWARG = {"second": "seconds", "minute": "minutes", "hour": "hours",
                    "day": "days", "week": "weeks", "month": "months",
                    "quarter": "months", "year": "years"}


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _log_root():
    """全量输出日志根目录：temp/job_logs/{yyyyMMdd}/{run_log_id}.log"""
    return os.path.join(_project_root(), "temp", "job_logs")


def run_log_file_path(start_time, run_log_id):
    """按运行记录的开始时间与 id 还原输出文件绝对路径"""
    date_dir = str(start_time)[:10].replace("-", "")
    return os.path.join(_log_root(), date_dir, f"{run_log_id}.log")


def run_log_file_relative(start_time, run_log_id):
    """输出文件的仓库根相对路径（写回 DB output 字段用）"""
    date_dir = str(start_time)[:10].replace("-", "")
    return f"temp/job_logs/{date_dir}/{run_log_id}.log"


def _cleanup_log_files():
    """清理超过保留期的日志目录（目录名为 yyyyMMdd）"""
    root = _log_root()
    if not os.path.isdir(root):
        return
    cutoff = (datetime.now() - timedelta(days=LOG_RETENTION_DAYS)).strftime("%Y%m%d")
    for name in os.listdir(root):
        if len(name) == 8 and name.isdigit() and name < cutoff:
            shutil.rmtree(os.path.join(root, name), ignore_errors=True)
            logger.info(f"job log dir cleaned: {name}")


def _rows(df):
    if df is None or len(df) == 0:
        return []
    return df.to_dict("records")


def _resolve_script_path(script_name):
    """scheduler_job.script_name 存脚本登记名：先查 script_info 拿 script_path（仓库根相对路径）
    再解析为绝对路径；未登记或文件不存在时回退按 script_name 本身当路径解析（兼容旧数据）"""
    info_rows = _rows(ScriptInfoDao().query(
        {ScriptInfoDao().script_name: ("=", script_name)}).get("data"))
    candidates = []
    if info_rows and str(info_rows[0]["script_path"] or "").strip():
        candidates.append(str(info_rows[0]["script_path"]).strip())
    candidates.append(script_name)
    for name in candidates:
        path = name if os.path.isabs(name) else os.path.join(_project_root(), name)
        path = os.path.normpath(path)
        if os.path.isfile(path):
            return path
    # 无一命中：按首个候选返回解析路径，保持原有"脚本不存在"报错行为
    return os.path.normpath(os.path.join(_project_root(), candidates[0].lstrip("/")))


def _first_run_datetime(job_row):
    """first_run_date + first_run_time -> datetime；缺省/非法取当前时间（从现在起按间隔推进）
    first_run_time 列（MySQL TIME）经 pandas 读出为 timedelta，统一取尾部 HH:MM:SS"""
    date_text = str(job_row.get("first_run_date") or "")[:10]
    time_value = job_row.get("first_run_time")
    if isinstance(time_value, timedelta):
        time_text = str(time_value)[-8:]
    else:
        time_text = str(time_value or "")[:8]
    for pattern, value in (("%Y-%m-%d %H:%M:%S", f"{date_text} {time_text}"), ("%Y-%m-%d", date_text)):
        if value.strip():
            try:
                return datetime.strptime(value, pattern)
            except ValueError:
                pass
    return datetime.now()


def build_trigger(job_row):
    """period_type + period_interval + first_run -> IntervalTrigger（过去的 start_date 会自动推进到下一个整点）"""
    period_type = str(job_row.get("period_type") or "day").lower()
    kwarg = _PERIOD_TO_KWARG.get(period_type)
    if kwarg is None:
        raise ValueError(f"不支持的 period_type: {period_type}")
    interval = max(int(job_row.get("period_interval") or 1), 1)
    if period_type == "quarter":
        kwarg, interval = "months", interval * 3   # APScheduler 无 quarter，按 3 个月折算
    return IntervalTrigger(start_date=_first_run_datetime(job_row), timezone="Asia/Shanghai", **{kwarg: interval})


def register_job(scheduler, job_row):
    """注册/刷新单个任务（replace_existing=True，改配置后重注册即生效）"""
    job_id = int(job_row["id"])
    scheduler.add_job(
        run_scheduled_script,
        trigger=build_trigger(job_row),
        id=f"{JOB_KEY_PREFIX}{job_id}",
        args=[job_id],
        name=str(job_row.get("job_name") or job_row.get("script_name") or job_id),
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
        replace_existing=True,
    )
    logger.info(f"job registered: {JOB_KEY_PREFIX}{job_id} script={job_row.get('script_name')}")


def unregister_job(scheduler, job_id):
    job_key = f"{JOB_KEY_PREFIX}{int(job_id)}"
    if scheduler.get_job(job_key) is not None:
        scheduler.remove_job(job_key)
        logger.info(f"job unregistered: {job_key}")


def _reconcile_stale_runs():
    """服务重启后回收遗留的"运行中"记录（子进程已随重启终止，状态永远停在0）"""
    log_dao = SchedulerJobRunLogDao()
    stale = _rows(log_dao.query({log_dao.status: ("=", 0)}).get("data"))
    if not stale:
        return
    now = datetime.now()
    for run in stale:
        log_dao.update_by_id(int(run["id"]), {
            "end_time": now,
            "status": 2,
            "output": f"{run['output'] or ''}\n[服务重启，运行被中断]".strip(),
        })
    logger.info(f"stale running runs reconciled: {len(stale)}")


def register_all_jobs(scheduler):
    """启动时从 scheduler_job 重建全部启用任务（脚本文件不存在的跳过并告警）"""
    _cleanup_log_files()
    _reconcile_stale_runs()
    job_dao = SchedulerJobDao()
    job_rows = _rows(job_dao.query({job_dao.enabled: ("=", 1)}).get("data"))
    registered = 0
    for job_row in job_rows:
        script_path = _resolve_script_path(str(job_row["script_name"]))
        if not os.path.isfile(script_path):
            logger.warning(f"跳过注册，脚本不存在: {job_row['script_name']} (job_id={job_row['id']})")
            continue
        try:
            register_job(scheduler, job_row)
            registered += 1
        except Exception as exc:
            logger.error(f"job register failed: {job_row['script_name']} error={exc}")
    logger.info(f"scheduler jobs registered: {registered}/{len(job_rows)}")


def start_job(scheduler, job_id, user_name=None):
    """启用任务：enabled=1 + 注册调度器"""
    job_dao = SchedulerJobDao()
    job_rows = _rows(job_dao.query_by_id(job_id).get("data"))
    if not job_rows:
        return False, "任务不存在"
    update_fields = {"enabled": 1}
    if user_name:
        update_fields["update_by"] = user_name
    if job_dao.update(update_fields, {job_dao.id: job_id})["code"] != 0:
        return False, "更新启停状态失败"
    register_job(scheduler, job_rows[0])
    return True, None


def stop_job(scheduler, job_id, user_name=None):
    """停用任务：enabled=0 + 注销调度器 + 终止正在运行的实例"""
    job_dao = SchedulerJobDao()
    job_rows = _rows(job_dao.query_by_id(job_id).get("data"))
    if not job_rows:
        return False, "任务不存在"
    update_fields = {"enabled": 0}
    if user_name:
        update_fields["update_by"] = user_name
    if job_dao.update(update_fields, {job_dao.id: job_id})["code"] != 0:
        return False, "更新启停状态失败"
    unregister_job(scheduler, job_id)
    kill_running(job_id)
    return True, None


def kill_running(job_id):
    """终止正在运行的脚本实例（terminate 后由执行线程自行收尾写日志）"""
    proc = _running.pop(int(job_id), None)
    if proc is None:
        return False
    try:
        proc.terminate()
        logger.info(f"job running instance terminated: job_id={job_id} pid={proc.pid}")
    except Exception as exc:
        logger.error(f"terminate failed: job_id={job_id} error={exc}")
    return True


def is_running(job_id):
    proc = _running.get(int(job_id))
    return proc is not None and proc.poll() is None


def run_job_now(job_id):
    """手动立即执行一次（后台线程，不依赖 enabled 状态），返回 (是否提交, 错误信息)"""
    job_dao = SchedulerJobDao()
    job_rows = _rows(job_dao.query_by_id(job_id).get("data"))
    if not job_rows:
        return False, "任务不存在"
    if is_running(job_id):
        return False, "该任务正在运行中"
    threading.Thread(target=_run_script, args=(job_rows[0], "manual"), daemon=True).start()
    return True, None


def run_scheduled_script(job_id):
    """调度器到点入口：按 job_id 取最新配置后执行"""
    job_dao = SchedulerJobDao()
    job_rows = _rows(job_dao.query_by_id(job_id).get("data"))
    if not job_rows:
        logger.warning(f"job gone, skip: {job_id}")
        return
    _run_script(job_rows[0], "scheduled")


def _job_script_args(job_row):
    """scheduler_job.params（JSON {参数名: 值}）-> 命令行参数 [--参数名 值 ...]
    值为 None/空串的跳过（脚本 argparse 走默认值）；解析失败按无参数处理"""
    try:
        job_params = json.loads(job_row.get("params") or "{}") or {}
    except (TypeError, ValueError):
        logger.warning(f"job params 解析失败，按无参数执行: {job_row.get('params')!r}")
        return []
    args = []
    for key, value in job_params.items():
        if value is None or str(value) == "":
            continue
        args += [f"--{key}", str(value)]
    return args


def _run_script(job_row, trigger_type):
    """执行脚本并记录运行历史（阻塞直到脚本结束/超时，运行在调度器线程池或后台线程）"""
    job_id = int(job_row["id"])
    script_name = str(job_row["script_name"])
    script_path = _resolve_script_path(script_name)
    job_dao = SchedulerJobDao()
    log_dao = SchedulerJobRunLogDao()
    start_time = datetime.now()

    if is_running(job_id):
        logger.warning(f"job still running, skip: {job_id} {script_name}")
        return
    if not os.path.isfile(script_path):
        logger.error(f"脚本不存在，跳过执行: {script_path}")
        log_dao.insert({"job_id": job_id, "script_name": script_name, "trigger_type": trigger_type,
                        "status": 2, "start_time": start_time, "end_time": datetime.now(),
                        "output": f"脚本不存在: {script_name}"})
        return

    if log_dao.insert({"job_id": job_id, "script_name": script_name, "trigger_type": trigger_type,
                       "status": 0, "start_time": start_time})["code"] != 0:
        logger.error("运行日志写入失败，放弃执行")
        return
    run_log_id_res = log_dao.query_latest_id(job_id)
    if run_log_id_res["code"] != 0:
        logger.error("运行日志回查失败，放弃执行")
        return
    run_log_id = run_log_id_res["data"]

    logger.info(f"job start: {script_name} trigger={trigger_type} run_log_id={run_log_id}")
    log_file = run_log_file_path(start_time, run_log_id)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    # -u 关闭子进程 stdout 缓冲，保证日志实时写入文件（前端可跟随滚动）
    # 注入 JOB_LOG_LEVEL：脚本内 utils.script_logger 按任务配置的级别输出
    # params 按 --参数名 值 拼入命令行（与 JOB_LOG_LEVEL 注入机制同类，来源为任务配置）
    job_env = {**os.environ, "JOB_LOG_LEVEL": str(job_row.get("log_level") or "INFO").upper()}
    proc = subprocess.Popen([sys.executable, "-u", script_path] + _job_script_args(job_row),
                            cwd=_project_root(),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=job_env)
    _running[job_id] = proc
    log_dao.update_by_id(run_log_id, {"pid": proc.pid})
    status = 2
    timeout_note = ""
    # 边运行边把 stdout 流式追加到日志文件（前端可实时 tail 该文件）
    with open(log_file, "w", encoding="utf-8", errors="ignore") as f:
        def _pump():
            for raw_line in iter(proc.stdout.readline, b""):
                f.write(raw_line.decode("utf-8", "ignore"))
                f.flush()   # 逐行刷盘，保证前端实时 tail 能读到
            f.flush()
        pump_thread = threading.Thread(target=_pump, daemon=True)
        pump_thread.start()
        try:
            proc.wait(timeout=SCRIPT_TIMEOUT_SECONDS)
            status = 1 if proc.returncode == 0 else 2
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            status = 3
            timeout_note = f"\n[timeout] 超过 {SCRIPT_TIMEOUT_SECONDS}s 被强制终止"
        pump_thread.join(timeout=10)
        if timeout_note:
            f.write(timeout_note)
        f.flush()
    end_time = datetime.now()
    # DB 只存尾部摘要 + 完整日志文件路径（全量在日志文件里）
    try:
        file_size = os.path.getsize(log_file)
        with open(log_file, "rb") as f:
            if file_size > OUTPUT_SUMMARY_CHARS:
                f.seek(file_size - OUTPUT_SUMMARY_CHARS)
                tail_bytes = f.read()
                tail = tail_bytes.decode("utf-8", "ignore")
                tail = tail[tail.find("\n") + 1:] if "\n" in tail else tail
            else:
                tail = f.read().decode("utf-8", "ignore")
    except OSError:
        tail = ""
    log_relative_path = run_log_file_relative(start_time, run_log_id)
    summary = f"{tail}\n[完整日志文件] {log_relative_path}"
    log_dao.update_by_id(run_log_id, {"end_time": end_time, "status": status, "output": summary})
    job_dao.update({
        "last_run_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "last_run_date": end_time.strftime("%Y-%m-%d"),
        "last_run_status": status,
    }, {job_dao.id: job_id})
    _cleanup_log_files()
    logger.info(f"job finished: {script_name} status={status} elapsed={(end_time - start_time).total_seconds():.0f}s")


if __name__ == '__main__':
    exit(0)
