#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 20:00
# @Author : KenLin
# @Email : kenlin@hisunglobal.com
# @File : route
# @Project : Soybean-backend
"""
动态路由接口（route），数据源：cms 库 sys_menu / sys_role_menu / sys_role
三个接口均需 Bearer access token，按当前用户计算（api-route-spec）。
"""
import traceback

from fastapi import Request

from app.api.model.auth.api_response_model import ApiResponse
from app.api.model.route import is_route_exist_model
from app.service.auth.main import SUPER_ROLE_CODE, _parse_access_token, _user_role_ids_and_codes
from app.service.system_manage.common import SYSTEM_ERROR, err, ok, parse_json, rows
from dao.sys_menu_info import SysMenuDao
from dao.sys_role_info import SysRoleDao
from dao.sys_role_menu_info import SysRoleMenuDao
from utils.loging_util import logger

# 常量路由（无需登录，与前端静态定义一致，api-route-spec 第 2 节）
CONSTANT_ROUTES = [
    {
        "name": "login",
        "path": "/login/:module(pwd-login|code-login|register|reset-pwd|bind-wechat)?",
        "component": "layout.blank$view.login",
        "props": True,
        "meta": {"title": "login", "i18nKey": "route.login", "constant": True, "hideInMenu": True}
    },
    {
        "name": "403", "path": "/403", "component": "layout.blank$view.403",
        "meta": {"title": "403", "i18nKey": "route.403", "constant": True, "hideInMenu": True}
    },
    {
        "name": "404", "path": "/404", "component": "layout.blank$view.404",
        "meta": {"title": "404", "i18nKey": "route.404", "constant": True, "hideInMenu": True}
    },
    {
        "name": "500", "path": "/500", "component": "layout.blank$view.500",
        "meta": {"title": "500", "i18nKey": "route.500", "constant": True, "hideInMenu": True}
    },
]
CONSTANT_ROUTE_NAMES = {r["name"] for r in CONSTANT_ROUTES}


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def _bearer_payload(request: Request):
    """解析 Bearer access token，无效/过期返回 None"""
    authorization = request.headers.get("Authorization", "")
    token = authorization[7:] if authorization.startswith("Bearer ") else ""
    return _parse_access_token(token)


def _accessible_menus(user_id):
    """当前用户全部启用角色经 sys_role_menu 授权的启用菜单行（并集）；R_SUPER -> 全部启用菜单"""
    menu_dao = SysMenuDao()
    menu_rows = rows(menu_dao.query({menu_dao.status: ("=", 1)}).get("data"))
    role_ids, role_codes = _user_role_ids_and_codes(user_id)
    if SUPER_ROLE_CODE in role_codes:
        return menu_rows
    if not role_ids:
        return []
    role_menu_dao = SysRoleMenuDao()
    menu_ids = {int(m["menu_id"]) for m in
                rows(role_menu_dao.query({role_menu_dao.role_id: ("in", role_ids)}).get("data"))}
    return [m for m in menu_rows if int(m["id"]) in menu_ids]


def _menu_order_key(menu):
    order = (parse_json(menu["route_props"]) or {}).get("order")
    return int(order) if order is not None else int(menu["id"])


def _menu_route_node(menu):
    """sys_menu 行 -> MenuRoute 节点（api-route-spec 第 0 节映射规则）"""
    route_props = parse_json(menu["route_props"]) or {}
    order = route_props.get("order")
    meta = {
        "title": menu["menu_name"],
        "order": int(order) if order is not None else int(menu["id"]),
        "requiresAuth": True,
    }
    if menu["icon"]:
        meta["icon"] = menu["icon"]
    if route_props.get("i18nKey"):
        meta["i18nKey"] = route_props["i18nKey"]
    for key in ("keepAlive", "hideInMenu", "href", "activeMenu", "multiTab", "fixedIndexInTab", "query"):
        value = route_props.get(key)
        if value is not None and value is not False:
            meta[key] = value
    node = {
        "id": str(menu["id"]),
        "name": menu["route_name"],
        "path": menu["route_path"],
        "component": menu["component"],
        "meta": meta,
    }
    # props 优先级：route_props.props（对象，如 iframe 文档页 view.iframe-page 的 {"url": ...}）
    # > 路径含参数（:id/:url）时 true > 省略；props 不属于 meta 透传字段
    if route_props.get("props") is not None:
        node["props"] = route_props["props"]
    elif ":" in menu["route_path"]:
        node["props"] = True
    return node


def _build_route_tree(menu_rows):
    """按 parent_id 组树；父级不在集合内（未启用/未授权）的子树整体不返回；兄弟按 order 升序"""
    by_id = {int(m["id"]): m for m in menu_rows}
    children_map = {}
    for menu in menu_rows:
        parent_id = int(menu["parent_id"])
        if parent_id in by_id:
            children_map.setdefault(parent_id, []).append(menu)
    built = {}

    def build(menu):
        menu_id = int(menu["id"])
        if menu_id in built:
            return built[menu_id]
        node = _menu_route_node(menu)
        children = children_map.get(menu_id)
        if children:
            node["children"] = [build(child) for child in sorted(children, key=_menu_order_key)]
        built[menu_id] = node
        return node

    roots = [m for m in menu_rows if int(m["parent_id"]) == 0]
    return [build(m) for m in sorted(roots, key=_menu_order_key)]


def _user_home(user_id, accessible_pages):
    """第一个启用角色的 sys_role.home；不属于可访问页面时回退 home"""
    role_ids, _ = _user_role_ids_and_codes(user_id)
    if role_ids:
        role_dao = SysRoleDao()
        role_map = {int(r["id"]): r for r in rows(role_dao.query().get("data"))}
        role = role_map.get(role_ids[0])
        if role is not None:
            home = role.get("home") or "home"
            if home in accessible_pages:
                return home
    return "home"


def get_user_routes(data, request: Request):
    """
    @url:route/getUserRoutes（可靠性要求：内部异常兜底返回空树，避免前端登出）
    """
    try:
        payload = _bearer_payload(request)
        if payload is None:
            return err("9999", "token expired")
        try:
            menus = _accessible_menus(payload["userId"])
            pages = {m["route_name"] for m in menus if m["menu_type"] == 2}
            return ok({"routes": _build_route_tree(menus), "home": _user_home(payload["userId"], pages)})
        except Exception:
            for msg in str(traceback.format_exc()).split("\n"):
                logger.error(msg)
            return ok({"routes": [], "home": "home"})
    except Exception:
        return _system_error()


def get_constant_routes(data, request: Request):
    """
    @url:route/getConstantRoutes（固定内容，无需登录态校验）
    """
    try:
        return ok(CONSTANT_ROUTES)
    except Exception:
        return _system_error()


def is_route_exist(data: is_route_exist_model.Input, request: Request):
    """
    @url:route/isRouteExist（用户可访问路由 ∪ 常量路由）
    """
    try:
        payload = _bearer_payload(request)
        if payload is None:
            return err("9999", "token expired")
        try:
            names = {m["route_name"] for m in _accessible_menus(payload["userId"])}
        except Exception:
            for msg in str(traceback.format_exc()).split("\n"):
                logger.error(msg)
            names = set()
        return ok(data.routeName in names or data.routeName in CONSTANT_ROUTE_NAMES)
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
