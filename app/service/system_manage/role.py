#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 17:00
# @Author : KenLin
# @Email : kenlin@hisunglobal.com
# @File : role.py
# @Project : Soybean-backend
"""角色维护 + 角色菜单授权接口（systemManage/Role、systemManage/RoleMenuAuth），
数据源：cms 库 sys_role / sys_user_role / sys_menu / sys_role_menu"""
import traceback

from fastapi import Request

from app.api.model.system_manage.role import add_role_model
from app.api.model.system_manage.role import batch_delete_role_model
from app.api.model.system_manage.role import delete_role_model
from app.api.model.system_manage.role import get_role_button_auth_model
from app.api.model.system_manage.role import get_role_list_model
from app.api.model.system_manage.role import get_role_menu_auth_model
from app.api.model.system_manage.role import update_role_button_auth_model
from app.api.model.system_manage.role import update_role_menu_auth_model
from app.api.model.system_manage.role import update_role_model
from app.service.system_manage.common import SYSTEM_ERROR, err, fmt, ok, page, parse_json, rows
from dao.sys_menu_info import SysMenuDao
from dao.sys_role_button_info import SysRoleButtonDao
from dao.sys_role_info import SysRoleDao
from dao.sys_role_menu_info import SysRoleMenuDao
from dao.sys_user_role_info import SysUserRoleDao
from utils.loging_util import logger

SUPER_ROLE_CODE = "R_SUPER"


def _role_view(row):
    """sys_role 行 -> 前端 Role 结构（home 为授权接口专用，列表不输出）"""
    return {
        "id": int(row["id"]),
        "roleName": row["role_name"],
        "roleCode": row["role_code"],
        "roleDesc": row["role_desc"],
        "status": fmt(row["status"]),
        "createBy": row["create_by"],
        "createTime": fmt(row["create_time"]),
        "updateBy": row["update_by"],
        "updateTime": fmt(row["update_time"]),
    }


def _system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def _role_in_use(user_role_dao, role_id):
    return len(rows(user_role_dao.query({user_role_dao.role_id: ("=", role_id)}).get("data"))) > 0


def get_role_list(data: get_role_list_model.Input, request: Request):
    """
    @url:systemManage/getRoleList
    """
    try:
        role_dao = SysRoleDao()
        fields = {}
        if data.roleName:
            fields[role_dao.role_name] = ("like", f"%{data.roleName}%")
        if data.roleCode:
            fields[role_dao.role_code] = ("like", f"%{data.roleCode}%")
        if data.status:
            fields[role_dao.status] = ("=", int(data.status))
        total_res = role_dao.count(fields)
        if total_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        total = total_res["data"]
        offset = (data.current - 1) * data.size
        role_rows = rows(role_dao.query(fields, f"order by {role_dao.id} limit {offset},{data.size}").get("data"))
        return ok(page([_role_view(r) for r in role_rows], data.current, data.size, total))
    except Exception:
        return _system_error()


def get_all_roles(data, request: Request):
    """
    @url:systemManage/getAllRoles（仅启用角色，下拉用）
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.status: ("=", 1)}).get("data"))
        return ok([{"id": int(r["id"]), "roleName": r["role_name"], "roleCode": r["role_code"]} for r in role_rows])
    except Exception:
        return _system_error()


def add_role(data: add_role_model.Input, request: Request):
    """
    @url:systemManage/addRole
    """
    try:
        role_dao = SysRoleDao()
        if rows(role_dao.query({role_dao.role_code: ("=", data.roleCode)}).get("data")):
            return err("E1003", f"角色编码 {data.roleCode} 已存在")
        insert_res = role_dao.insert({
            "role_name": data.roleName,
            "role_code": data.roleCode,
            "role_desc": data.roleDesc,
            "status": int(data.status),
            "create_by": "admin",
        })
        if insert_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def update_role(data: update_role_model.Input, request: Request):
    """
    @url:systemManage/updateRole
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.id: ("=", data.id)}).get("data"))
        if not role_rows:
            return err("E0001", f"角色不存在: {data.id}")
        if role_rows[0]["role_code"] == SUPER_ROLE_CODE:
            return err("E0001", "内置超管角色不允许修改")
        if data.roleCode != role_rows[0]["role_code"]:
            # roleCode 仅作一致性匹配，不接受修改
            return err("E1003", f"角色编码不允许修改: 传入 {data.roleCode} 与库中 {role_rows[0]['role_code']} 不一致")
        update_res = role_dao.update({
            "role_name": data.roleName,
            "role_desc": data.roleDesc,
            "status": int(data.status),
            "update_by": "admin",
        }, {role_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def _check_role_deletable(role, user_role_dao):
    """返回错误信息或 None"""
    if role["role_code"] == SUPER_ROLE_CODE:
        return "内置超管角色不允许删除"
    if _role_in_use(user_role_dao, int(role["id"])):
        return "该角色已分配用户，请先移除用户身上的该角色"
    return None


def delete_role(data: delete_role_model.Input, request: Request):
    """
    @url:systemManage/deleteRole（被用户引用时拒绝；sys_role_menu 授权随外键 CASCADE 清理）
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.id: ("=", data.id)}).get("data"))
        if not role_rows:
            return err("E0001", f"角色不存在: {data.id}")
        error = _check_role_deletable(role_rows[0], SysUserRoleDao())
        if error:
            return err("E1004", error)
        delete_res = role_dao.delete({role_dao.id: data.id})
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def batch_delete_role(data: batch_delete_role_model.Input, request: Request):
    """
    @url:systemManage/batchDeleteRole（逐个校验，任一不满足则整体不删除）
    """
    try:
        role_dao = SysRoleDao()
        user_role_dao = SysUserRoleDao()
        to_delete = []
        for role_id in data.ids:
            role_rows = rows(role_dao.query({role_dao.id: ("=", role_id)}).get("data"))
            if not role_rows:
                return err("E0001", f"角色不存在: {role_id}")
            error = _check_role_deletable(role_rows[0], user_role_dao)
            if error:
                return err("E1004", f"{role_rows[0]['role_name']}: {error}")
            to_delete.append(role_id)
        delete_res = role_dao.delete_many(role_dao.id, to_delete)
        if delete_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def _complete_menu_ancestors(menu_rows, menu_ids):
    """补全祖先链：前端 NTree 勾选项可能不含父节点（目录），不补全会导致目录不显示"""
    by_id = {int(m["id"]): m for m in menu_rows}
    result = set()
    for menu_id in menu_ids:
        node = by_id.get(menu_id)
        while node is not None:
            result.add(int(node["id"]))
            node = by_id.get(int(node["parent_id"]))
    return result


def get_role_menu_auth(data: get_role_menu_auth_model.Input, request: Request):
    """
    @url:systemManage/getRoleMenuAuth（回显）
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.id: ("=", data.roleId)}).get("data"))
        if not role_rows:
            return err("E0001", f"角色不存在: {data.roleId}")
        role_menu_dao = SysRoleMenuDao()
        menu_ids = sorted(int(m["menu_id"]) for m in
                          rows(role_menu_dao.query({role_menu_dao.role_id: ("=", data.roleId)}).get("data")))
        return ok({"home": role_rows[0]["home"], "menuIds": menu_ids})
    except Exception:
        return _system_error()


def update_role_menu_auth(data: update_role_menu_auth_model.Input, request: Request):
    """
    @url:systemManage/updateRoleMenuAuth（保存：更新 sys_role.home + 先删后插 sys_role_menu）
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.id: ("=", data.roleId)}).get("data"))
        if not role_rows:
            return err("E0001", f"角色不存在: {data.roleId}")
        menu_dao = SysMenuDao()
        menu_rows = rows(menu_dao.query().get("data"))
        known_ids = {int(m["id"]) for m in menu_rows}
        for menu_id in data.menuIds:
            if menu_id not in known_ids:
                return err("E0001", f"菜单不存在: {menu_id}")
        home_res = role_dao.update({role_dao.home: data.home, role_dao.update_by: "admin"}, {role_dao.id: data.roleId})
        if home_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        role_menu_dao = SysRoleMenuDao()
        link_res = role_menu_dao.replace_role_menus(data.roleId, sorted(_complete_menu_ancestors(menu_rows, data.menuIds)))
        if link_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


def _menu_buttons(menu):
    """菜单 buttons JSON -> [{code, desc}]（过滤无 code 的脏数据）"""
    return [b for b in (parse_json(menu["buttons"]) or []) if isinstance(b, dict) and b.get("code")]


def get_role_button_auth(data: get_role_button_auth_model.Input, request: Request):
    """
    @url:systemManage/getRoleButtonAuth（回显：某菜单在 sys_role_button 无记录 = 该菜单按钮全给，默认全选）
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.id: ("=", data.roleId)}).get("data"))
        if not role_rows:
            return err("E0001", f"角色不存在: {data.roleId}")
        menu_dao = SysMenuDao()
        menu_rows = rows(menu_dao.query().get("data"))
        if role_rows[0]["role_code"] == SUPER_ROLE_CODE:
            # 超管：返回全部含按钮菜单
            authorized_ids = {int(m["id"]) for m in menu_rows}
        else:
            role_menu_dao = SysRoleMenuDao()
            authorized_ids = {int(m["menu_id"]) for m in
                              rows(role_menu_dao.query({role_menu_dao.role_id: ("=", data.roleId)}).get("data"))}
        rb_dao = SysRoleButtonDao()
        rb_map = {}
        for record in rows(rb_dao.query({rb_dao.role_id: ("=", data.roleId)}).get("data")):
            rb_map.setdefault(int(record["menu_id"]), set()).add(record["button_code"])
        menus = []
        checked = []
        for menu in sorted((m for m in menu_rows if int(m["id"]) in authorized_ids),
                           key=lambda m: (int(m["parent_id"]), (parse_json(m["route_props"]) or {}).get("order") or 0)):
            buttons = _menu_buttons(menu)
            if not buttons:
                continue
            menus.append({"menuId": int(menu["id"]), "menuName": menu["menu_name"], "buttons": buttons})
            codes = rb_map.get(int(menu["id"]))
            if codes is None:
                codes = [b["code"] for b in buttons]
            for code in codes:
                if code not in checked:
                    checked.append(code)
        return ok({"menus": menus, "checkedCodes": checked})
    except Exception:
        return _system_error()


def update_role_button_auth(data: update_role_button_auth_model.Input, request: Request):
    """
    @url:systemManage/updateRoleButtonAuth（事务内整表替换；未授权菜单的按钮码直接忽略；R_SUPER 不落库）
    """
    try:
        role_dao = SysRoleDao()
        role_rows = rows(role_dao.query({role_dao.id: ("=", data.roleId)}).get("data"))
        if not role_rows:
            return err("E0001", f"角色不存在: {data.roleId}")
        if role_rows[0]["role_code"] == SUPER_ROLE_CODE:
            # 超管始终全量，不落库
            return ok(None)
        role_menu_dao = SysRoleMenuDao()
        authorized_ids = {int(m["menu_id"]) for m in
                          rows(role_menu_dao.query({role_menu_dao.role_id: ("=", data.roleId)}).get("data"))}
        menu_dao = SysMenuDao()
        menu_rows = rows(menu_dao.query().get("data"))
        # 应用层建立 button_code -> menu_id 映射（仅限该角色已授权菜单）
        code_menu = {}
        for menu in menu_rows:
            if int(menu["id"]) not in authorized_ids:
                continue
            for button in _menu_buttons(menu):
                code_menu[button["code"]] = int(menu["id"])
        records = []
        for code in data.buttonCodes:
            menu_id = code_menu.get(code)
            if menu_id is None or (menu_id, code) in records:
                continue
            records.append((menu_id, code))
        rb_dao = SysRoleButtonDao()
        replace_res = rb_dao.replace_role_buttons(data.roleId, records)
        if replace_res["code"] != 0:
            return err("-1", SYSTEM_ERROR)
        return ok(None)
    except Exception:
        return _system_error()


if __name__ == '__main__':
    exit(0)
