#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : script_manage.py
# @Project : Soybean-backend
"""脚本信息管理接口（scheduleManage/scriptManage），数据源：cms 库 script_info"""
import json
import os
import traceback
from pathlib import Path

from fastapi import Request, UploadFile

from app.api.model.schedule_manage.script_manage import add_script_info_model
from app.api.model.schedule_manage.script_manage import delete_script_info_model
from app.api.model.schedule_manage.script_manage import get_script_content_model
from app.api.model.schedule_manage.script_manage import get_script_info_detail_model
from app.api.model.schedule_manage.script_manage import get_script_info_list_model
from app.api.model.schedule_manage.script_manage import update_script_info_model
from app.service.auth.main import _parse_access_token
from app.service.system_manage.common import SYSTEM_ERROR, err, fmt, ok, page, parse_json, rows
from dao.script_info import ScriptInfoDao
from utils.loging_util import logger

# 仓库根目录（app/service/schedule_manage/script_manage.py 上溯 3 级）
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 允许查看/写入内容的脚本目录白名单（防路径穿越，路径需位于其下）
SCRIPT_DIR_WHITELIST = ("app/schedule/scripts",)


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def _script_path_in_whitelist(script_path):
    """scriptPath 是否位于脚本目录白名单内（同时拦截 .. / 盘符绝对路径等穿越尝试）"""
    target = _resolve_script_target(script_path)
    if target is None:
        return False
    rel = target.relative_to(PROJECT_ROOT).as_posix()
    return any(rel == d or rel.startswith(d + "/") for d in SCRIPT_DIR_WHITELIST)


def _current_user(request):
    """从 Authorization 解析登录账号，失败返回 None"""
    authorization = request.headers.get("Authorization", "")
    token = authorization[7:] if authorization.startswith("Bearer ") else ""
    payload = _parse_access_token(token)
    return payload["userName"] if payload else None


def _dump_params(params):
    """入参定义数组 -> JSON 字符串（空统一写入 []；ScriptParam 为 pydantic 模型，需先 model_dump）"""
    return json.dumps([p.model_dump() for p in (params or [])], ensure_ascii=False)


def _script_view(row):
    """script_info 行 -> 前端记录结构（params 解析为 JSON 数组，空输出 []）"""
    return {
        "scriptName": row["script_name"],
        "scriptPath": row["script_path"],
        "description": row["description"],
        "params": parse_json(row["params"]) or [],
        "createTime": fmt(row["create_time"]),
        "createBy": row["create_by"],
        "updateTime": fmt(row["update_time"]),
        "updateBy": row["update_by"],
        "ts": fmt(row["ts"]),
    }


def get_script_info_list(data: get_script_info_list_model.Input, request: Request):
    """
    @url:scheduleManage/getScriptInfoList（scriptName 模糊查询，排序：script_name）
    """
    try:
        script_dao = ScriptInfoDao()
        fields = {}
        if data.scriptName:
            fields[script_dao.script_name] = ("like", f"%{data.scriptName}%")
        total_res = script_dao.count(fields)
        if total_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        clauses = f"order by {script_dao.script_name} limit {offset},{data.pageSize}"
        script_rows = rows(script_dao.query(fields, clauses).get("data"))
        records = [_script_view(r) for r in script_rows]
        return ok(page(records, data.current, data.pageSize, total))
    except Exception:
        return _system_error()


def get_script_info_detail(data: get_script_info_detail_model.Input, request: Request):
    """
    @url:scheduleManage/getScriptInfoDetail（按主键 scriptName 查询）
    """
    try:
        script_dao = ScriptInfoDao()
        script_rows = rows(script_dao.query_by_name(data.scriptName).get("data"))
        if not script_rows:
            return err("E1012", f"脚本不存在: {data.scriptName}")
        return ok(_script_view(script_rows[0]))
    except Exception:
        return _system_error()


def get_script_content(data: get_script_content_model.Input, request: Request):
    """
    @url:scheduleManage/getScriptContent（查看脚本文件内容，utf-8 文本；
    路径不在白名单报 E1014，文件不存在/读取失败报 E1015）
    """
    try:
        script_dao = ScriptInfoDao()
        script_rows = rows(script_dao.query_by_name(data.scriptName).get("data"))
        if not script_rows:
            return err("E1012", f"脚本不存在: {data.scriptName}")
        script_path = script_rows[0]["script_path"]
        if not _script_path_in_whitelist(script_path):
            return err("E1014", f"脚本路径不在允许的目录内: {script_path}")
        target = _resolve_script_target(script_path)
        if not target.is_file():
            return err("E1015", f"脚本文件不存在: {script_path}")
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return err("E1015", f"脚本文件不是有效的 UTF-8 文本: {script_path}")
        except OSError as exc:
            return err("E1015", f"脚本文件读取失败: {exc}")
        return ok({"scriptName": data.scriptName, "content": content})
    except Exception:
        return _system_error()


def _write_script_content(target, content):
    """utf-8 原子写入脚本文件（同目录临时文件 + os.replace），返回 None 或失败信息"""
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, target)
        return None
    except OSError as exc:
        logger.error(f"script content write failed: {target} error={exc}")
        return f"脚本内容写入失败: {exc}"


def _read_script_content(target):
    """读取现有文件内容用于失败回滚；文件不存在返回 None"""
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _path_duplicated(script_dao, script_path, exclude_name=None):
    for row in rows(script_dao.query({script_dao.script_path: ("=", script_path)}).get("data")):
        if exclude_name is None or row["script_name"] != exclude_name:
            return True
    return False


def _resolve_script_target(script_path):
    """scriptPath -> 仓库内绝对路径；非法（含 .. / 越出仓库根目录）返回 None"""
    rel = script_path.replace("\\", "/").lstrip("/")
    if ".." in Path(rel).parts or not rel:
        return None
    target = (PROJECT_ROOT / rel).resolve()
    if PROJECT_ROOT not in target.parents:
        return None
    return target


def _remove_saved_file(target):
    """删除已写入的脚本文件（新增失败/异常时回滚，删除失败仅记日志不影响返回）"""
    if target is None:
        return
    try:
        if target.exists():
            target.unlink()
            logger.info(f"rollback script file: {target}")
    except Exception:
        logger.error(f"rollback script file failed: {target}")


def add_script_info(data: add_script_info_model.Input, request: Request, file: UploadFile = None):
    """
    @url:scheduleManage/addScriptInfo（multipart：file 保存到 scriptPath 指定路径；
    文件已存在报 E1013，路径非法报 E1014；params 为空写入 []；
    未返回成功或出现异常时，回滚删除已写入的文件）
    """
    saved_target = None
    try:
        user_name = _current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        script_dao = ScriptInfoDao()
        if rows(script_dao.query_by_name(data.scriptName).get("data")):
            return err("E1010", f"脚本名已存在: {data.scriptName}")
        if _path_duplicated(script_dao, data.scriptPath):
            return err("E1011", f"脚本路径已存在: {data.scriptPath}")
        if file is not None:
            if not _script_path_in_whitelist(data.scriptPath):
                return err("E1014", f"脚本路径不在允许的目录内: {data.scriptPath}")
            target = _resolve_script_target(data.scriptPath)
            if target is None:
                return err("E1014", f"脚本路径非法: {data.scriptPath}")
            if target.exists():
                return err("E1013", f"脚本文件已存在: {data.scriptPath}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(file.file.read())
            saved_target = target
        insert_res = script_dao.insert({
            "script_name": data.scriptName,
            "script_path": data.scriptPath,
            "description": data.description,
            "params": _dump_params(data.params),
            "create_by": user_name,
        })
        if insert_res["code"] != 0:
            _remove_saved_file(saved_target)
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        _remove_saved_file(saved_target)
        return _system_error()


def update_script_info(data: update_script_info_model.Input, request: Request):
    """
    @url:scheduleManage/updateScriptInfo（按主键 scriptName 定位，仅更新传入字段；params 空数组=清空为 []；
    content 传值=覆盖写入 scriptPath 指向文件（utf-8、原子替换、白名单校验），None=不触碰文件；
    先写文件后更新 DB，DB 失败时回滚文件内容）
    """
    try:
        user_name = _current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        script_dao = ScriptInfoDao()
        script_rows = rows(script_dao.query_by_name(data.scriptName).get("data"))
        if not script_rows:
            return err("E1012", f"脚本不存在: {data.scriptName}")
        target_path = data.scriptPath or script_rows[0]["script_path"]
        if data.content is not None:
            if not _script_path_in_whitelist(target_path):
                return err("E1014", f"脚本路径不在允许的目录内: {target_path}")
            content_target = _resolve_script_target(target_path)
            if content_target is None:
                return err("E1014", f"脚本路径非法: {target_path}")
        if data.scriptPath is not None and data.scriptPath != script_rows[0]["script_path"] \
                and _path_duplicated(script_dao, data.scriptPath, data.scriptName):
            return err("E1011", f"脚本路径已存在: {data.scriptPath}")
        update_fields = {}
        if data.scriptPath is not None:
            update_fields["script_path"] = data.scriptPath
        if data.description is not None:
            update_fields["description"] = data.description
        if data.params is not None:
            update_fields["params"] = _dump_params(data.params)
        if not update_fields and data.content is None:
            return ok(None)
        update_fields["update_by"] = user_name
        # 先写文件（保存旧内容用于 DB 失败回滚），DB 更新成功后落定
        old_content = None
        if data.content is not None:
            old_content = _read_script_content(content_target)
            write_error = _write_script_content(content_target, data.content)
            if write_error:
                return err("-1", write_error)
        update_res = script_dao.update(update_fields, {script_dao.script_name: data.scriptName})
        if update_res["code"] != 0:
            if data.content is not None:
                _write_script_content(content_target, old_content) \
                    if old_content is not None else _remove_saved_file(content_target)
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def delete_script_info(data: delete_script_info_model.Input, request: Request):
    """
    @url:scheduleManage/deleteScriptInfo（按主键 scriptName 删除）
    """
    try:
        script_dao = ScriptInfoDao()
        if not rows(script_dao.query_by_name(data.scriptName).get("data")):
            return err("E1012", f"脚本不存在: {data.scriptName}")
        delete_res = script_dao.delete({script_dao.script_name: data.scriptName})
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
