#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_role_menu_auth_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """GET 查询参数"""
    model_config = ConfigDict(title="RoleMenuAuthQuery")

    roleId: int = Field(..., title="角色ID")


class Output(BaseModel):
    """角色菜单授权回显"""
    model_config = ConfigDict(title="RoleMenuAuth")

    home: str = Field("home", title="角色首页路由名")
    menuIds: list = Field([], title="已授权菜单ID列表（含目录节点）")


if __name__ == '__main__':
    exit(0)
