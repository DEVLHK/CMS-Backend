#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : role_base_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """角色公共字段（对齐前端 Api.SystemManage.Role）"""
    roleName: str = Field(
        ...,
        min_length=1,
        title="角色名称"
    )
    roleCode: str = Field(
        ...,
        min_length=1,
        title="角色编码",
        description="如 R_SUPER，唯一"
    )
    roleDesc: str = Field(
        "",
        title="角色描述"
    )
    status: str = Field(
        "1",
        title="状态",
        description="1:启用 2:禁用，字符串类型"
    )


if __name__ == '__main__':
    exit(0)
