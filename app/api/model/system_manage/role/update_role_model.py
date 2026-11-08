#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 19:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_role_model.py
# @Project : Soybean-backend
from pydantic import ConfigDict, Field

from app.api.model.system_manage.role.role_base_model import RoleBase


class Input(RoleBase):
    """编辑角色；roleCode 仅作一致性匹配（与库中不一致返回 E1003），不接受修改"""
    model_config = ConfigDict(title="RoleUpdateInput")

    id: int = Field(..., title="角色ID")


if __name__ == '__main__':
    exit(0)
