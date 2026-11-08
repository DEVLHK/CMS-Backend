#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 19:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_role_button_auth_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """保存角色按钮授权（不属于该角色已授权菜单的按钮码会被忽略；R_SUPER 直接成功不落库）"""
    model_config = ConfigDict(title="RoleButtonAuthUpdateInput")

    roleId: int = Field(..., title="角色ID")
    buttonCodes: list = Field([], title="勾选的按钮权限码列表")


if __name__ == '__main__':
    exit(0)
