#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_user_model.py
# @Project : Soybean-backend
from pydantic import ConfigDict, Field

from app.api.model.system_manage.user.user_base_model import UserBase


class Input(UserBase):
    """编辑用户（不含 password；userRoles 整体替换）"""
    model_config = ConfigDict(title="UserUpdateInput")

    id: int = Field(..., title="用户ID")


if __name__ == '__main__':
    exit(0)
