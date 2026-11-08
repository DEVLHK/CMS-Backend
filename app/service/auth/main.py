#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 18:00
# @Author : KenLin
# @Email : kenlin@hisunglobal.com
# @File : auth
# @Project : Soybean-backend
"""
认证接口（auth），数据源：cms 库 sys_user / sys_role / sys_user_role / sys_menu / sys_role_menu / sys_refresh_token

- 登录：sys_user + bcrypt 校验（status=1），成功签发 token 对
- access token：HMAC-SHA256 签名的无状态令牌（含 userId/userName/exp），不落库
- refreshToken：随机串，库内存 SHA-256 哈希（sys_refresh_token），一次性轮换、可吊销
- getUserInfo：token 鉴权 -> 用户启用角色 roleCode + 角色关联菜单 buttons 展开去重（R_SUPER 短路全量）
"""
import base64
import hashlib
import hmac
import json
import time
import traceback
import uuid
from datetime import datetime, timedelta

import bcrypt
from fastapi import Request

from app.api.model.auth import login_model
from app.api.model.auth import refresh_token_model
from app.api.model.auth.get_user_info_model import Output as UserInfoOutput
from app.service.system_manage.common import SYSTEM_ERROR, err, ok, parse_json, rows
from dao.sys_menu_info import SysMenuDao
from dao.sys_refresh_token_info import SysRefreshTokenDao
from dao.sys_role_button_info import SysRoleButtonDao
from dao.sys_role_info import SysRoleDao
from dao.sys_role_menu_info import SysRoleMenuDao
from dao.sys_user_info import SysUserDao
from dao.sys_user_role_info import SysUserRoleDao
from utils.loging_util import logger

SUPER_ROLE_CODE = "R_SUPER"
ACCESS_TOKEN_TTL = 3600            # access token 有效期（秒）
REFRESH_TOKEN_TTL_DAYS = 7         # refreshToken 有效期（天）
# TODO: 上线前移到配置并妥善保管
TOKEN_SECRET = b"cms-backend-token-secret"


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


# ============================================================================
# access token：HMAC-SHA256 签名（base64(payload).hex signature）
# ============================================================================
def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _create_access_token(user_id, user_name):
    payload = json.dumps({"userId": int(user_id), "userName": user_name,
                          "exp": int(time.time()) + ACCESS_TOKEN_TTL})
    signature = hmac.new(TOKEN_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return _b64encode(payload.encode()) + "." + signature


def _parse_access_token(token):
    """校验签名与有效期，返回 payload dict；无效/过期返回 None"""
    try:
        body, signature = token.rsplit(".", 1)
        payload_json = _b64decode(body).decode()
        expected = hmac.new(TOKEN_SECRET, payload_json.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


# ============================================================================
# 角色与按钮汇总（getUserInfo）
# ============================================================================
def _user_role_ids_and_codes(user_id):
    """用户全部启用角色的 (role_id 列表, roleCode 列表)"""
    link_dao = SysUserRoleDao()
    links = rows(link_dao.query({link_dao.user_id: ("=", user_id)}).get("data"))
    if not links:
        return [], []
    role_dao = SysRoleDao()
    role_map = {int(r["id"]): r for r in rows(role_dao.query().get("data"))}
    role_ids = []
    role_codes = []
    for link in links:
        role = role_map.get(int(link["role_id"]))
        if role and role["status"] == 1:
            if int(role["id"]) not in role_ids:
                role_ids.append(int(role["id"]))
            if role["role_code"] not in role_codes:
                role_codes.append(role["role_code"])
    return role_ids, role_codes


def _collect_button_codes(menu_rows):
    codes = []
    for menu in menu_rows:
        for button in parse_json(menu["buttons"]) or []:
            code = button.get("code") if isinstance(button, dict) else None
            if code and code not in codes:
                codes.append(code)
    return codes


def _user_buttons(role_ids, role_codes):
    """
    按钮聚合（api-system-manage-spec 8.4）：
    R_SUPER -> 全部菜单 buttons 全集；
    否则按 (角色, 已授权菜单) 逐个判断：sys_role_button 无记录 -> 该菜单全量按钮；有记录 -> 仅勾选码；最终求并集去重
    """
    menu_dao = SysMenuDao()
    menu_rows = rows(menu_dao.query().get("data"))
    if SUPER_ROLE_CODE in role_codes:
        return _collect_button_codes(menu_rows)
    if not role_ids:
        return []
    role_menu_dao = SysRoleMenuDao()
    pairs = rows(role_menu_dao.query({role_menu_dao.role_id: ("in", role_ids)}).get("data"))
    rb_dao = SysRoleButtonDao()
    rb_map = {}
    for record in rows(rb_dao.query({rb_dao.role_id: ("in", role_ids)}).get("data")):
        rb_map.setdefault((int(record["role_id"]), int(record["menu_id"])), set()).add(record["button_code"])
    menu_map = {int(m["id"]): m for m in menu_rows}
    buttons = []
    for pair in pairs:
        menu = menu_map.get(int(pair["menu_id"]))
        if menu is None:
            continue
        codes = rb_map.get((int(pair["role_id"]), int(pair["menu_id"])))
        if codes is None:
            codes = [b["code"] for b in (parse_json(menu["buttons"]) or [])
                     if isinstance(b, dict) and b.get("code")]
        for code in codes:
            if code not in buttons:
                buttons.append(code)
    return buttons


# ============================================================================
# 接口
# ============================================================================
def user_login(data: login_model.Input, request: Request):
    """
    @url:auth/login
    """
    try:
        user_dao = SysUserDao()
        user_rows = rows(user_dao.query({user_dao.user_name: ("=", data.userName)}).get("data"))
        if not user_rows:
            return err("E0001", "用户名或密码错误")
        user = user_rows[0]
        if user["status"] != 1:
            return err("E0001", "用户名或密码错误")
        try:
            password_ok = bcrypt.checkpw(data.password.encode(), user["password"].encode())
        except ValueError:
            # 库内哈希非 bcrypt 格式（如导入的占位数据），一律视为密码错误
            password_ok = False
        if not password_ok:
            return err("E0001", "用户名或密码错误")
        user_id = int(user["id"])
        token = _create_access_token(user_id, user["user_name"])
        refresh_token = _issue_refresh_token(user_id)
        if refresh_token is None:
            return err("-1", SYSTEM_ERROR)
        return ok(login_model.Output(token=token, refreshToken=refresh_token).model_dump())
    except Exception:
        return _system_error()


def _issue_refresh_token(user_id):
    """签发新的 refreshToken（随机串，库内存 SHA-256 哈希），失败返回 None"""
    refresh_token = uuid.uuid4().hex
    rt_dao = SysRefreshTokenDao()
    insert_res = rt_dao.insert({
        "user_id": user_id,
        "token_hash": _sha256(refresh_token),
        "expires_at": datetime.now() + timedelta(days=REFRESH_TOKEN_TTL_DAYS),
    })
    if insert_res["code"] != 0:
        return None
    return refresh_token


def get_user_info(data, request: Request):
    """
    @url:auth/getUserInfo（GET，Bearer access token 鉴权）
    """
    try:
        authorization = request.headers.get("Authorization", "")
        token = authorization[7:] if authorization.startswith("Bearer ") else ""
        payload = _parse_access_token(token)
        if payload is None:
            # 过期码，前端会自动调 /auth/refreshToken 并重放该请求
            return err("9999", "token expired")
        user_dao = SysUserDao()
        user_rows = rows(user_dao.query({user_dao.id: ("=", payload["userId"])}).get("data"))
        if not user_rows or user_rows[0]["status"] != 1:
            # token 有效但用户已删除/禁用 -> 登出码，避免前端无限刷新
            return err("8888", "login expired")
        role_ids, role_codes = _user_role_ids_and_codes(payload["userId"])
        response_data = UserInfoOutput(
            userId=str(payload["userId"]),
            userName=user_rows[0]["user_name"],
            roles=role_codes,
            buttons=_user_buttons(role_ids, role_codes),
        )
        return ok(response_data.model_dump())
    except Exception:
        return _system_error()


def refresh_token(data: refresh_token_model.Input, request: Request):
    """
    @url:auth/refreshToken（一次性轮换：旧的吊销、签发全新 token 对）
    """
    try:
        token_hash = _sha256(data.refreshToken)
        rt_dao = SysRefreshTokenDao()
        # 哈希 + 未吊销条件查库，过期时间在应用侧比较（避免应用/DB 时区差异）
        token_rows = rows(rt_dao.query({rt_dao.token_hash: ("=", token_hash),
                                        rt_dao.revoked: ("=", 0)}).get("data"))
        if not token_rows or token_rows[0]["expires_at"] <= datetime.now():
            # 必须返回登出码(8888)，不能返回过期码(9999等)，否则前端会无限循环刷新
            return err("8888", "login expired")
        token_row = token_rows[0]
        user_id = int(token_row["user_id"])
        user_dao = SysUserDao()
        user_rows = rows(user_dao.query({user_dao.id: ("=", user_id)}).get("data"))
        if not user_rows or user_rows[0]["status"] != 1:
            rt_dao.revoke(token_hash)
            return err("8888", "login expired")
        rt_dao.revoke(token_hash)
        new_refresh_token = _issue_refresh_token(user_id)
        if new_refresh_token is None:
            return err("-1", SYSTEM_ERROR)
        token = _create_access_token(user_id, user_rows[0]["user_name"])
        return ok(refresh_token_model.Output(token=token, refreshToken=new_refresh_token).model_dump())
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
