#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 11:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : scheduler_job.py
# @Project : Soybean-backend
"""定时任务管理接口（scheduleManage/schedulerJob），数据源：cms 库 scheduler_job / scheduler_job_run_log"""
import json
import os
import traceback

from fastapi import Request
from fastapi.responses import FileResponse

from app.api.model.schedule_manage.scheduler_job import add_scheduler_job_model
from app.api.model.schedule_manage.scheduler_job import delete_scheduler_job_model
from app.api.model.schedule_manage.scheduler_job import get_scheduler_job_detail_model
from app.api.model.schedule_manage.scheduler_job import get_scheduler_job_list_model
from app.api.model.schedule_manage.scheduler_job import get_scheduler_job_run_log_content_model
from app.api.model.schedule_manage.scheduler_job import get_scheduler_job_run_log_model
from app.api.model.schedule_manage.scheduler_job import update_scheduler_job_model
from app.service.auth.main import _parse_access_token
from app.service.system_manage.common import SYSTEM_ERROR, err, fmt, ok, page, parse_json, rows
from app.schedule import job_engine
from dao.scheduler_job_info import SchedulerJobDao
from dao.scheduler_job_run_log_info import SchedulerJobRunLogDao
from dao.script_info import ScriptInfoDao
from utils.loging_util import logger


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def _current_user(request):
    """从 Authorization 解析登录账号，失败返回 None"""
    authorization = request.headers.get("Authorization", "")
    token = authorization[7:] if authorization.startswith("Bearer ") else ""
    payload = _parse_access_token(token)
    return payload["userName"] if payload else None


def _job_view(row):
    """scheduler_job 行 -> 前端记录结构（last_run_status/enabled 输出字符串）"""
    return {
        "id": int(row["id"]),
        "jobName": row["job_name"],
        "scriptName": row["script_name"],
        "description": row["description"],
        "periodType": row["period_type"],
        "periodInterval": int(row["period_interval"]),
        "firstRunDate": fmt(row["first_run_date"]),
        "firstRunTime": fmt(row["first_run_time"]),
        "lastRunTime": fmt(row["last_run_time"]),
        "lastRunDate": fmt(row["last_run_date"]),
        "lastRunStatus": fmt(row["last_run_status"]),
        "enabled": fmt(row["enabled"]),
        "running": job_engine.is_running(int(row["id"])),
        "logLevel": row["log_level"],
        "params": parse_json(row.get("params")) or {},
        "createTime": fmt(row["create_time"]),
        "createBy": row["create_by"],
        "updateTime": fmt(row["update_time"]),
        "updateBy": row["update_by"],
        "ts": fmt(row["ts"]),
    }


def get_scheduler_job_list(data: get_scheduler_job_list_model.Input, request: Request):
    """
    @url:scheduleManage/getSchedulerJobList（jobName/scriptName 模糊查询，排序：id）
    """
    try:
        job_dao = SchedulerJobDao()
        fields = {}
        if data.jobName:
            fields[job_dao.job_name] = ("like", f"%{data.jobName}%")
        if data.scriptName:
            fields[job_dao.script_name] = ("like", f"%{data.scriptName}%")
        total_res = job_dao.count(fields)
        if total_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        clauses = f"order by {job_dao.id} limit {offset},{data.pageSize}"
        job_rows = rows(job_dao.query(fields, clauses).get("data"))
        records = [_job_view(r) for r in job_rows]
        return ok(page(records, data.current, data.pageSize, total))
    except Exception:
        return _system_error()


def get_scheduler_job_detail(data: get_scheduler_job_detail_model.Input, request: Request):
    """
    @url:scheduleManage/getSchedulerJobDetail（按 id 查询单条）
    """
    try:
        job_dao = SchedulerJobDao()
        job_rows = rows(job_dao.query_by_id(data.id).get("data"))
        if not job_rows:
            return err("E1009", f"任务不存在: {data.id}")
        return ok(_job_view(job_rows[0]))
    except Exception:
        return _system_error()


def _job_name_duplicated(job_dao, job_name, exclude_id=None):
    for row in rows(job_dao.query({job_dao.job_name: ("=", job_name)}).get("data")):
        if exclude_id is None or int(row["id"]) != exclude_id:
            return True
    return False


def _script_name_duplicated(job_dao, script_name, exclude_id=None):
    for row in rows(job_dao.query({job_dao.script_name: ("=", script_name)}).get("data")):
        if exclude_id is None or int(row["id"]) != exclude_id:
            return True
    return False


def _validate_job_params(script_name, params):
    """任务入参与 script_info 的入参定义比对：mandatory=true 且未提供非空值 -> 错误信息；
    脚本未登记或无入参定义时不校验（返回 None）"""
    script_rows = rows(ScriptInfoDao().query_by_name(script_name).get("data"))
    if not script_rows:
        return None
    defs = parse_json(script_rows[0]["params"]) or []
    missing = [d.get("param_name") for d in defs
               if d.get("mandatory") and not str((params or {}).get(d.get("param_name")) or "").strip()]
    if missing:
        return f"必填参数缺少值: {', '.join(m for m in missing if m)}"
    return None


def add_scheduler_job(data: add_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/addSchedulerJob（create_by 取当前登录账号；job_name/script_name 唯一校验）
    """
    try:
        user_name = _current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        job_dao = SchedulerJobDao()
        if _job_name_duplicated(job_dao, data.jobName):
            return err("E1007", f"任务名称已存在: {data.jobName}")
        if _script_name_duplicated(job_dao, data.scriptName):
            return err("E1008", f"脚本已配置任务: {data.scriptName}")
        param_error = _validate_job_params(data.scriptName, data.params)
        if param_error:
            return err("E1012", param_error)
        insert_res = job_dao.insert({
            "job_name": data.jobName,
            "script_name": data.scriptName,
            "description": data.description,
            "period_type": data.periodType,
            "period_interval": data.periodInterval,
            "first_run_date": data.firstRunDate or None,
            "first_run_time": data.firstRunTime or None,
            "log_level": (data.logLevel or "INFO").upper(),
            "params": json.dumps(data.params or {}, ensure_ascii=False),
            "create_by": user_name,
        })
        if insert_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        # 新任务默认启用，注册进调度器（改频率等走 update 分支刷新）
        new_rows = rows(job_dao.query({job_dao.script_name: ("=", data.scriptName)}).get("data"))
        if new_rows:
            try:
                job_engine.register_job(request.app.state.scheduler, new_rows[0])
            except Exception as exc:
                logger.error(f"job register failed: {data.scriptName} error={exc}")
                return err("E1010", f"任务已保存，但注册调度器失败: {exc}")
        return ok(None)
    except Exception:
        return _system_error()


def update_scheduler_job(data: update_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/updateSchedulerJob（按 id 定位，仅更新传入字段；firstRun 传空串=清除）
    """
    try:
        user_name = _current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        job_dao = SchedulerJobDao()
        job_rows = rows(job_dao.query_by_id(data.id).get("data"))
        if not job_rows:
            return err("E1009", f"任务不存在: {data.id}")
        if data.jobName is not None and data.jobName != job_rows[0]["job_name"] \
                and _job_name_duplicated(job_dao, data.jobName, data.id):
            return err("E1007", f"任务名称已存在: {data.jobName}")
        if data.scriptName is not None and data.scriptName != job_rows[0]["script_name"] \
                and _script_name_duplicated(job_dao, data.scriptName, data.id):
            return err("E1008", f"脚本已配置任务: {data.scriptName}")
        update_fields = {}
        if data.jobName is not None:
            update_fields["job_name"] = data.jobName
        if data.scriptName is not None:
            update_fields["script_name"] = data.scriptName
        if data.description is not None:
            update_fields["description"] = data.description
        if data.periodType is not None:
            update_fields["period_type"] = data.periodType
        if data.periodInterval is not None:
            update_fields["period_interval"] = data.periodInterval
        if data.firstRunDate is not None:
            update_fields["first_run_date"] = data.firstRunDate or None
        if data.firstRunTime is not None:
            update_fields["first_run_time"] = data.firstRunTime or None
        if data.logLevel is not None:
            update_fields["log_level"] = data.logLevel.upper()
        if data.params is not None:
            target_script = data.scriptName or job_rows[0]["script_name"]
            param_error = _validate_job_params(target_script, data.params)
            if param_error:
                return err("E1012", param_error)
            update_fields["params"] = json.dumps(data.params, ensure_ascii=False)
        if not update_fields:
            return ok(None)
        update_fields["update_by"] = user_name
        update_res = job_dao.update(update_fields, {job_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        # 频率/脚本变更后刷新调度器注册（停用状态则仅注销）
        fresh_rows = rows(job_dao.query_by_id(data.id).get("data"))
        if fresh_rows:
            scheduler = request.app.state.scheduler
            try:
                if int(fresh_rows[0]["enabled"]) == 1:
                    job_engine.register_job(scheduler, fresh_rows[0])
                else:
                    job_engine.unregister_job(scheduler, data.id)
            except Exception as exc:
                logger.error(f"job re-register failed: id={data.id} error={exc}")
                return err("E1010", f"任务已保存，但刷新调度器失败: {exc}")
        return ok(None)
    except Exception:
        return _system_error()


def delete_scheduler_job(data: delete_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/deleteSchedulerJob（按 id 删除）
    """
    try:
        job_dao = SchedulerJobDao()
        if not rows(job_dao.query_by_id(data.id).get("data")):
            return err("E1009", f"任务不存在: {data.id}")
        delete_res = job_dao.delete_by_id(data.id)
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        # 同步注销调度器并终止运行中的实例（历史运行日志保留）
        job_engine.unregister_job(request.app.state.scheduler, data.id)
        job_engine.kill_running(data.id)
        return ok(None)
    except Exception:
        return _system_error()


def start_scheduler_job(data: delete_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/startSchedulerJob（enabled=1 并注册调度器）
    """
    try:
        user_name = _current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        started, error = job_engine.start_job(request.app.state.scheduler, data.id, user_name)
        if not started:
            return err("E1009", error)
        return ok(None)
    except Exception:
        return _system_error()


def stop_scheduler_job(data: delete_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/stopSchedulerJob（enabled=0、注销调度器并终止运行中的实例）
    """
    try:
        user_name = _current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        stopped, error = job_engine.stop_job(request.app.state.scheduler, data.id, user_name)
        if not stopped:
            return err("E1009", error)
        return ok(None)
    except Exception:
        return _system_error()


def run_scheduler_job_once(data: delete_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/runSchedulerJobOnce（手动立即执行一次，后台运行，进度看运行日志）
    """
    try:
        submitted, error = job_engine.run_job_now(data.id)
        if not submitted:
            return err("E1011", error)
        return ok(None)
    except Exception:
        return _system_error()


def get_scheduler_job_run_log(data: get_scheduler_job_run_log_model.Input, request: Request):
    """
    @url:scheduleManage/getSchedulerJobRunLog（运行历史，按开始时间倒序；status 0:运行中 1:成功 2:失败 3:超时）
    """
    try:
        log_dao = SchedulerJobRunLogDao()
        fields = {}
        if data.jobId is not None:
            fields[log_dao.job_id] = ("=", data.jobId)
        if data.status:
            fields[log_dao.status] = ("=", int(data.status))
        total_res = log_dao.count(fields)
        if total_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        clauses = f"order by {log_dao.start_time} desc, {log_dao.id} desc limit {offset},{data.pageSize}"
        log_rows = rows(log_dao.query(fields, clauses).get("data"))
        records = [{
            "id": int(r["id"]),
            "jobId": int(r["job_id"]),
            "scriptName": r["script_name"],
            "triggerType": r["trigger_type"],
            "status": fmt(r["status"]),
            "startTime": fmt(r["start_time"]),
            "endTime": fmt(r["end_time"]),
            "pid": int(r["pid"]) if r["pid"] is not None else None,
            "output": r["output"],
        } for r in log_rows]
        return ok(page(records, data.current, data.pageSize, total))
    except Exception:
        return _system_error()


def download_scheduler_job_run_log(data: delete_scheduler_job_model.Input, request: Request):
    """
    @url:scheduleManage/downloadSchedulerJobRunLog（下载运行输出全量日志文件，
    路径规则 temp/job_logs/{yyyyMMdd}/{run_log_id}.log，仅保留过去30天）
    """
    try:
        log_dao = SchedulerJobRunLogDao()
        log_rows = rows(log_dao.query({log_dao.id: ("=", data.id)}).get("data"))
        if not log_rows:
            return err("E2004", "运行记录不存在")
        run = log_rows[0]
        if str(run["start_time"]) in ("", "None", "NaT"):
            return err("E2004", "该记录没有开始时间，无日志文件")
        date_dir = str(run["start_time"])[:10].replace("-", "")
        log_file = os.path.normpath(os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
            "temp", "job_logs", date_dir, f"{data.id}.log"))
        if not os.path.isfile(log_file):
            return err("E2004", f"日志文件不存在: temp/job_logs/{date_dir}/{data.id}.log")
        return FileResponse(log_file, media_type="text/plain",
                            filename=f"job_run_{data.id}.log")
    except Exception:
        return _system_error()


def _read_log_lines_window(log_file, limit, before=None, after=None):
    """按行号窗口读取日志文件（流式遍历，不整读入内存）
    行号 1-based：after -> (after, after+limit]；before -> [before-limit+1, before-1]；缺省 -> 最后 limit 行
    返回 (total_lines, lines, start_line, end_line, has_more_before, has_more_after)"""
    from collections import deque
    total = 0
    lines = []
    start_line = end_line = 0
    has_more_before = has_more_after = False
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        if after is not None:
            want_start, want_end = after + 1, after + limit
            for line_no, raw in enumerate(f, 1):
                total = line_no
                if line_no < want_start:
                    continue
                if line_no > want_end:
                    has_more_after = True
                    break
                lines.append(raw.rstrip("\r\n"))
            if lines:
                start_line, end_line = want_start, want_start + len(lines) - 1
                has_more_after = end_line < total
            else:
                # after >= total（无新内容）：回显请求位置而非 0，
                # endLine 含义为"前端已确认加载到的行号"，供轮询状态衔接
                start_line, end_line = want_start, after
                has_more_after = end_line < total
                has_more_before = want_start > 1
        elif before is not None:
            want_start, want_end = max(1, before - limit + 1), before - 1
            for line_no, raw in enumerate(f, 1):
                total = line_no
                if line_no < want_start:
                    continue
                if line_no > want_end:
                    break
                lines.append(raw.rstrip("\r\n"))
            if lines:
                start_line, end_line = want_start, want_start + len(lines) - 1
            has_more_before = want_start > 1
        else:
            tail = deque(maxlen=limit)
            for line_no, raw in enumerate(f, 1):
                total = line_no
                tail.append(raw.rstrip("\r\n"))
            lines = list(tail)
            start_line = total - len(lines) + 1
            end_line = total
            has_more_before = start_line > 1
    return total, lines, start_line, end_line, has_more_before, has_more_after


def get_scheduler_job_run_log_content(data: get_scheduler_job_run_log_content_model.Input, request: Request):
    """
    @url:scheduleManage/getSchedulerJobRunLogContent（分页查看运行日志文件内容，
    支持尾部/向上/向下三种窗口；任务运行中文件持续增长，可用 after 端轮询跟随）
    """
    try:
        limit = min(max(data.limit, 1), 1000)
        log_dao = SchedulerJobRunLogDao()
        log_rows = rows(log_dao.query({log_dao.id: ("=", data.id)}).get("data"))
        if not log_rows:
            return err("E2004", "运行记录不存在")
        run = log_rows[0]
        running = job_engine.is_running(int(run["job_id"]))
        if str(run["start_time"]) in ("", "None", "NaT"):
            return ok({"id": data.id, "fileExists": False, "running": running,
                       "totalLines": 0, "startLine": 0, "endLine": 0,
                       "lines": [], "hasMoreBefore": False, "hasMoreAfter": False})
        log_file = job_engine.run_log_file_path(run["start_time"], data.id)
        if not os.path.isfile(log_file):
            return ok({"id": data.id, "fileExists": False, "running": running,
                       "totalLines": 0, "startLine": 0, "endLine": 0,
                       "lines": [], "hasMoreBefore": False, "hasMoreAfter": False})
        total, lines, start_line, end_line, has_more_before, has_more_after = \
            _read_log_lines_window(log_file, limit, data.before, data.after)
        return ok({"id": data.id, "fileExists": True, "running": running,
                   "totalLines": total, "startLine": start_line, "endLine": end_line,
                   "lines": lines, "hasMoreBefore": has_more_before, "hasMoreAfter": has_more_after})
    except Exception:
        return _system_error()


def debug_scheduler_jobs(data, request: Request):
    """
    @url:scheduleManage/debugSchedulerJobs（临时调试：导出调度器内作业的 next_run_time 等内部状态）
    """
    try:
        scheduler = request.app.state.scheduler
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "nextRunTime": str(job.next_run_time),
                "trigger": str(job.trigger),
            })
        return ok({"schedulerRunning": scheduler.running, "jobs": jobs})
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
