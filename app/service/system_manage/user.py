#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 17:00
# @Author : KenLin
# @Email : kenlin@hisunglobal.com
# @File : user.py
# @Project : Soybean-backend
"""用户维护接口（systemManage/User），数据源：cms 库 sys_user / sys_role / sys_user_role"""
import traceback

import bcrypt
from fastapi import Request

from app.api.model.system_manage.user import add_user_model
from app.api.model.system_manage.user import batch_delete_user_model
from app.api.model.system_manage.user import delete_user_model
from app.api.model.system_manage.user import get_user_list_model
from app.api.model.system_manage.user import update_user_model
from app.service.system_manage.common import SYSTEM_ERROR, err, fmt, ok, page, rows
from dao.sys_role_info import SysRoleDao
from dao.sys_user_info import SysUserDao
from dao.sys_user_role_info import SysUserRoleDao
from utils.loging_util import logger


def _hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _user_view(row, user_roles):
    """sys_user 行 -> 前端 User 结构（camelCase，status/userGender 输出字符串）"""
    return {
        "id": int(row["id"]),
        "userName": row["user_name"],
        "userGender": fmt(row["user_gender"]),
        "nickName": row["nick_name"],
        "userPhone": row["user_phone"],
        "userEmail": row["user_email"],
        "userRoles": user_roles,
        "status": fmt(row["status"]),
        "createBy": row["create_by"],
        "createTime": fmt(row["create_time"]),
        "updateBy": row["update_by"],
        "updateTime": fmt(row["update_time"]),
    }


def _load_user_roles(user_ids):
    """批量汇总用户角色编码：{user_id: [roleCode, ...]}"""
    result = {user_id: [] for user_id in user_ids}
    if not user_ids:
        return result
    link_dao = SysUserRoleDao()
    links = rows(link_dao.query({link_dao.user_id: ("in", user_ids)}).get("data"))
    if not links:
        return result
    role_dao = SysRoleDao()
    role_map = {int(r["id"]): r["role_code"] for r in rows(role_dao.query().get("data"))}
    for link in links:
        user_id = int(link["user_id"])
        role_code = role_map.get(int(link["role_id"]))
        if role_code and user_id in result and role_code not in result[user_id]:
            result[user_id].append(role_code)
    return result


def _resolve_role_codes(role_codes):
    """roleCode 列表 -> (role_id 列表, 错误信息)"""
    if not role_codes:
        return [], None
    role_dao = SysRoleDao()
    code_id = {r["role_code"]: int(r["id"]) for r in rows(role_dao.query().get("data"))}
    role_ids = []
    for code in role_codes:
        if code not in code_id:
            return [], f"角色编码不存在: {code}"
        if code_id[code] not in role_ids:
            role_ids.append(code_id[code])
    return role_ids, None


def _phone_email_duplicated(user_dao, field, value, exclude_user_id=None):
    for row in rows(user_dao.query({field: ("=", value)}).get("data")):
        if exclude_user_id is None or int(row["id"]) != exclude_user_id:
            return True
    return False


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def get_user_list(data: get_user_list_model.Input, request: Request):
    """
    @url:systemManage/getUserList
    """
    try:
        user_dao = SysUserDao()
        fields = {}
        if data.userName:
            fields[user_dao.user_name] = ("like", f"%{data.userName}%")
        if data.nickName:
            fields[user_dao.nick_name] = ("like", f"%{data.nickName}%")
        if data.userGender:
            fields[user_dao.user_gender] = ("=", int(data.userGender))
        if data.userPhone:
            fields[user_dao.user_phone] = ("=", data.userPhone)
        if data.userEmail:
            fields[user_dao.user_email] = ("=", data.userEmail)
        if data.status:
            fields[user_dao.status] = ("=", int(data.status))
        total_res = user_dao.count(fields)
        if total_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        total = total_res["data"]
        offset = (data.current - 1) * data.size
        df = user_dao.query(fields, f"order by {user_dao.id} limit {offset},{data.size}").get("data")
        user_rows = rows(df)
        roles_map = _load_user_roles([int(r["id"]) for r in user_rows])
        records = [_user_view(row, roles_map.get(int(row["id"]), [])) for row in user_rows]
        return ok(page(records, data.current, data.size, total))
    except Exception:
        return _system_error()


def add_user(data: add_user_model.Input, request: Request):
    """
    @url:systemManage/addUser
    """
    try:
        user_dao = SysUserDao()
        if rows(user_dao.query({user_dao.user_name: ("=", data.userName)}).get("data")):
            return err("E1001", f"用户名 {data.userName} 已存在")
        if data.userPhone and _phone_email_duplicated(user_dao, user_dao.user_phone, data.userPhone):
            return err("E1002", "手机号已被使用")
        if data.userEmail and _phone_email_duplicated(user_dao, user_dao.user_email, data.userEmail):
            return err("E1002", "邮箱已被使用")
        role_ids, error = _resolve_role_codes(data.userRoles or [])
        if error:
            return err("E0001", error)
        insert_res = user_dao.insert({
            "user_name": data.userName,
            "password": _hash_password(data.password),
            "user_gender": int(data.userGender) if data.userGender else None,
            "nick_name": data.nickName,
            "user_phone": data.userPhone or None,
            "user_email": data.userEmail or None,
            "status": int(data.status),
            "create_by": "admin",
        })
        if insert_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        # 回查自增 id（user_name 唯一），再写角色关联
        new_user = rows(user_dao.query({user_dao.user_name: ("=", data.userName)}).get("data"))
        if not new_user:
            return err("-1", SYSTEM_ERROR)
        new_user_id = int(new_user[0]["id"])
        if role_ids:
            link_dao = SysUserRoleDao()
            link_res = link_dao.bulk_insert([{"user_id": new_user_id, "role_id": rid} for rid in role_ids])
            if link_res["code"] != 0:
                return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def update_user(data: update_user_model.Input, request: Request):
    """
    @url:systemManage/updateUser
    """
    try:
        user_dao = SysUserDao()
        user_rows = rows(user_dao.query({user_dao.id: ("=", data.id)}).get("data"))
        if not user_rows:
            return err("E0001", f"用户不存在: {data.id}")
        if data.userName != user_rows[0]["user_name"] and \
                rows(user_dao.query({user_dao.user_name: ("=", data.userName)}).get("data")):
            return err("E1001", f"用户名 {data.userName} 已存在")
        if data.userPhone and _phone_email_duplicated(user_dao, user_dao.user_phone, data.userPhone, data.id):
            return err("E1002", "手机号已被使用")
        if data.userEmail and _phone_email_duplicated(user_dao, user_dao.user_email, data.userEmail, data.id):
            return err("E1002", "邮箱已被使用")
        role_ids, error = _resolve_role_codes(data.userRoles or [])
        if error:
            return err("E0001", error)
        update_res = user_dao.update({
            "user_name": data.userName,
            "user_gender": int(data.userGender) if data.userGender else None,
            "nick_name": data.nickName,
            "user_phone": data.userPhone or None,
            "user_email": data.userEmail or None,
            "status": int(data.status),
            "update_by": "admin",
        }, {user_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        # 先删后插整体替换角色关联（事务）
        link_dao = SysUserRoleDao()
        link_res = link_dao.replace_user_roles(data.id, role_ids)
        if link_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def delete_user(data: delete_user_model.Input, request: Request):
    """
    @url:systemManage/deleteUser（sys_user_role / sys_refresh_token 随外键 CASCADE 清理）
    """
    try:
        user_dao = SysUserDao()
        if not rows(user_dao.query({user_dao.id: ("=", data.id)}).get("data")):
            return err("E0001", f"用户不存在: {data.id}")
        delete_res = user_dao.delete({user_dao.id: data.id})
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def batch_delete_user(data: batch_delete_user_model.Input, request: Request):
    """
    @url:systemManage/batchDeleteUser（逐个校验存在性，任一不存在则整体不删除）
    """
    try:
        user_dao = SysUserDao()
        for user_id in data.ids:
            if not rows(user_dao.query({user_dao.id: ("=", user_id)}).get("data")):
                return err("E0001", f"用户不存在: {user_id}")
        delete_res = user_dao.delete_many(user_dao.id, data.ids)
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
