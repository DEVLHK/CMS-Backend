#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_all_roles_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Output(BaseModel):
    """启用角色下拉项（仅 status=1）"""
    model_config = ConfigDict(title="RoleOption")

    id: int = Field(..., title="角色ID")
    roleName: str = Field(..., title="角色名称")
    roleCode: str = Field(..., title="角色编码")


if __name__ == '__main__':
    exit(0)
