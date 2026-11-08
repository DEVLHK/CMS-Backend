#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_user_model.py
# @Project : Soybean-backend
from pydantic import ConfigDict, Field

from app.api.model.system_manage.user.user_base_model import UserBase


class Input(UserBase):
    model_config = ConfigDict(title="UserAddInput")

    password: str = Field(
        ...,
        min_length=1,
        title="登录密码",
        description="明文传输依赖HTTPS，mock阶段不入库，接库后bcrypt存储"
    )


if __name__ == '__main__':
    exit(0)
