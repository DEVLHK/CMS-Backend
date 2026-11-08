#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 19:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_role_button_auth_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """GET 查询参数"""
    model_config = ConfigDict(title="RoleButtonAuthQuery")

    roleId: int = Field(..., title="角色ID")


class ButtonItem(BaseModel):
    model_config = ConfigDict(title="MenuButtonItem")

    code: str = Field(..., title="按钮权限码")
    desc: str = Field("", title="按钮描述")


class MenuButtons(BaseModel):
    """含按钮的菜单节点（授权弹窗树的数据源）"""
    model_config = ConfigDict(title="RoleButtonAuthMenu")

    menuId: int = Field(..., title="菜单ID")
    menuName: str = Field(..., title="菜单名称")
    buttons: list = Field([], title="该菜单的全部按钮")


class Output(BaseModel):
    """角色按钮授权回显；某菜单在 sys_role_button 无记录 = 该菜单按钮全给（默认全选）"""
    model_config = ConfigDict(title="RoleButtonAuth")

    menus: list = Field([], title="含按钮的已授权菜单列表")
    checkedCodes: list = Field([], title="已勾选按钮码列表")


if __name__ == '__main__':
    exit(0)
