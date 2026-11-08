#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 10:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : refresh_token_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(title="RefreshTokenInput")

    refreshToken: str = Field(
        ...,
        min_length=1,
        title="刷新令牌",
        description="登录时返回的刷新令牌"
    )


class Output(BaseModel):
    model_config = ConfigDict(title="LoginToken")

    token: str = Field(
        ...,
        title="访问令牌",
        description="新的访问令牌"
    )
    refreshToken: str = Field(
        ...,
        title="刷新令牌",
        description="新的刷新令牌"
    )


if __name__ == '__main__':
    exit(0)
