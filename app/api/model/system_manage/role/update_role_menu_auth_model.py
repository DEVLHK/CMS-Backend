#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_role_menu_auth_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """保存角色菜单授权（后端补全 menuIds 祖先链后整体替换）"""
    model_config = ConfigDict(title="RoleMenuAuthUpdateInput")

    roleId: int = Field(..., title="角色ID")
    home: str = Field("home", title="角色首页路由名")
    menuIds: list = Field([], title="勾选的菜单ID列表")


if __name__ == '__main__':
    exit(0)
