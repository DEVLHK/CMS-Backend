#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 10:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : login_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(title="UserLoginInput")

    userName: str = Field(
        ...,
        min_length=1,
        title="用户名称",
        description="用户登录名称或账号"
    )
    password: str = Field(
        ...,
        min_length=1,
        title="用户密码",
        description="用户登录密码"
    )


class Output(BaseModel):
    model_config = ConfigDict(title="LoginToken")

    token: str = Field(
        ...,
        title="访问令牌",
        description="访问令牌，后续请求通过 Header Authorization: Bearer <token> 携带"
    )
    refreshToken: str = Field(
        ...,
        title="刷新令牌",
        description="刷新令牌，token过期后用于换取新的令牌对"
    )


if __name__ == '__main__':
    exit(0)
