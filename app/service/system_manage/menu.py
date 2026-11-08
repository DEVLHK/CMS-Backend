#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 17:00
# @Author : KenLin
# @Email : kenlin@hisunglobal.com
# @File : menu.py
# @Project : Soybean-backend
"""菜单维护接口（systemManage/Menu），数据源：cms 库 sys_menu（route_props/buttons JSON 列）"""
import json
import traceback

from fastapi import Request

from app.api.model.system_manage.menu import add_menu_model
from app.api.model.system_manage.menu import delete_menu_model
from app.api.model.system_manage.menu import get_menu_list_model
from app.api.model.system_manage.menu import update_menu_model
from app.service.system_manage.common import SYSTEM_ERROR, err, fmt, ok, page, parse_json, rows
from dao.sys_menu_info import SysMenuDao
from utils.loging_util import logger


def _menu_view(row):
    """sys_menu 行 -> 前端拍平 Menu 结构（解包 route_props/buttons JSON）"""
    view = {
        "id": int(row["id"]),
        "parentId": int(row["parent_id"]),
        "menuType": fmt(row["menu_type"]),
        "menuName": row["menu_name"],
        "routeName": row["route_name"],
        "routePath": row["route_path"],
        "component": row["component"],
        "icon": row["icon"],
        "iconType": fmt(row["icon_type"]),
        "buttons": parse_json(row["buttons"]) or [],
    }
    view.update(parse_json(row["route_props"]) or {})
    view["status"] = fmt(row["status"])
    view["createBy"] = row["create_by"]
    view["createTime"] = fmt(row["create_time"])
    view["updateBy"] = row["update_by"]
    view["updateTime"] = fmt(row["update_time"])
    return view


def _menu_order(menu_view):
    return menu_view.get("order") or 0


def _pack_route_props(data):
    """前端拍平的路由属性 -> 库内 route_props JSON 字符串"""
    return json.dumps({
        "i18nKey": data.i18nKey,
        "keepAlive": data.keepAlive,
        "constant": data.constant,
        "order": data.order,
        "href": data.href,
        "hideInMenu": data.hideInMenu,
        "activeMenu": data.activeMenu,
        "multiTab": data.multiTab,
        "fixedIndexInTab": data.fixedIndexInTab,
        "query": data.query,
    }, ensure_ascii=False)


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def get_menu_list(data: get_menu_list_model.Input, request: Request):
    """
    @url:systemManage/getMenuList/v2（current/size 不传返回全量，平铺+按 parent_id/order 排序）
    """
    try:
        menu_dao = SysMenuDao()
        menu_rows = rows(menu_dao.query().get("data"))
        records = sorted((_menu_view(r) for r in menu_rows), key=lambda m: (m["parentId"], _menu_order(m)))
        if data.current is None or data.size is None:
            return ok(page(records, 1, len(records), len(records)))
        start = (data.current - 1) * data.size
        return ok(page(records[start:start + data.size], data.current, data.size, len(records)))
    except Exception:
        return _system_error()


def get_all_pages(data, request: Request):
    """
    @url:systemManage/getAllPages（全部页面路由名）
    """
    try:
        menu_dao = SysMenuDao()
        fields = {menu_dao.menu_type: ("=", 2), menu_dao.status: ("=", 1)}
        menu_rows = rows(menu_dao.query(fields).get("data"))
        return ok(sorted({r["route_name"] for r in menu_rows}))
    except Exception:
        return _system_error()


def _build_menu_tree(menu_rows, parent_id):
    children = sorted((m for m in menu_rows if int(m["parent_id"]) == parent_id),
                      key=lambda m: (parse_json(m["route_props"]) or {}).get("order") or 0)
    if not children:
        return None
    return [{"id": int(m["id"]), "label": m["menu_name"], "pId": int(m["parent_id"]),
             "children": _build_menu_tree(menu_rows, int(m["id"]))} for m in children]


def get_menu_tree(data, request: Request):
    """
    @url:systemManage/getMenuTree（授权弹窗用，仅启用菜单）
    """
    try:
        menu_dao = SysMenuDao()
        menu_rows = rows(menu_dao.query({menu_dao.status: ("=", 1)}).get("data"))
        return ok(_build_menu_tree(menu_rows, 0) or [])
    except Exception:
        return _system_error()


def add_menu(data: add_menu_model.Input, request: Request):
    """
    @url:systemManage/addMenu（路由属性打包进 route_props JSON）
    """
    try:
        menu_dao = SysMenuDao()
        if rows(menu_dao.query({menu_dao.route_name: ("=", data.routeName)}).get("data")):
            return err("E1005", f"路由名称 {data.routeName} 已存在")
        if data.parentId != 0 and not rows(menu_dao.query({menu_dao.id: ("=", data.parentId)}).get("data")):
            return err("E0001", f"父菜单不存在: {data.parentId}")
        buttons = json.dumps([b.model_dump() for b in data.buttons], ensure_ascii=False) if data.buttons else None
        insert_res = menu_dao.insert({
            "parent_id": data.parentId,
            "menu_type": int(data.menuType),
            "menu_name": data.menuName,
            "route_name": data.routeName,
            "route_path": data.routePath,
            "component": data.component or None,
            "icon": data.icon,
            "icon_type": int(data.iconType),
            "route_props": _pack_route_props(data),
            "buttons": buttons,
            "status": int(data.status),
            "create_by": "admin",
        })
        if insert_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def update_menu(data: update_menu_model.Input, request: Request):
    """
    @url:systemManage/updateMenu
    """
    try:
        menu_dao = SysMenuDao()
        menu_rows = rows(menu_dao.query({menu_dao.id: ("=", data.id)}).get("data"))
        if not menu_rows:
            return err("E0001", f"菜单不存在: {data.id}")
        if data.routeName != menu_rows[0]["route_name"] and \
                rows(menu_dao.query({menu_dao.route_name: ("=", data.routeName)}).get("data")):
            return err("E1005", f"路由名称 {data.routeName} 已存在")
        if data.parentId != 0 and not rows(menu_dao.query({menu_dao.id: ("=", data.parentId)}).get("data")):
            return err("E0001", f"父菜单不存在: {data.parentId}")
        buttons = json.dumps([b.model_dump() for b in data.buttons], ensure_ascii=False) if data.buttons else None
        update_res = menu_dao.update({
            "parent_id": data.parentId,
            "menu_type": int(data.menuType),
            "menu_name": data.menuName,
            "route_name": data.routeName,
            "route_path": data.routePath,
            "component": data.component or None,
            "icon": data.icon,
            "icon_type": int(data.iconType),
            "route_props": _pack_route_props(data),
            "buttons": buttons,
            "status": int(data.status),
            "update_by": "admin",
        }, {menu_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def delete_menu(data: delete_menu_model.Input, request: Request):
    """
    @url:systemManage/deleteMenu（有子菜单禁止删除；sys_role_menu 授权随外键 CASCADE 删除）
    """
    try:
        menu_dao = SysMenuDao()
        if not rows(menu_dao.query({menu_dao.id: ("=", data.id)}).get("data")):
            return err("E0001", f"菜单不存在: {data.id}")
        if rows(menu_dao.query({menu_dao.parent_id: ("=", data.id)}).get("data")):
            return err("E1006", "请先删除子菜单")
        delete_res = menu_dao.delete({menu_dao.id: data.id})
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
