#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 10:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_user_info_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Output(BaseModel):
    model_config = ConfigDict(title="UserInfo")

    userId: str = Field(
        ...,
        title="用户ID",
        description="用户ID"
    )
    userName: str = Field(
        ...,
        title="用户名称",
        description="展示用用户名"
    )
    roles: list = Field(
        ...,
        title="角色码",
        description='角色码列表，静态路由模式超管角色固定为 R_SUPER'
    )
    buttons: list = Field(
        ...,
        title="按钮权限码",
        description="按钮权限码列表，无按钮权限返回空数组[]，不要null"
    )


if __name__ == '__main__':
    exit(0)
