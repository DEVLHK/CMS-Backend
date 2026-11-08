#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : user_base_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户公共字段（对齐前端 Api.SystemManage.User）"""
    userName: str = Field(
        ...,
        min_length=1,
        title="用户名",
        description="登录账号，唯一"
    )
    userGender: Optional[str] = Field(
        None,
        title="性别",
        description="1:男 2:女，字符串类型，null为未设置"
    )
    nickName: str = Field(
        "",
        title="昵称"
    )
    userPhone: Optional[str] = Field(
        None,
        title="手机号",
        description="唯一，空字符串入库前转null"
    )
    userEmail: Optional[str] = Field(
        None,
        title="邮箱",
        description="唯一，空字符串入库前转null"
    )
    userRoles: list = Field(
        [],
        title="角色编码列表",
        description="roleCode 数组，如 [\"R_SUPER\"]"
    )
    status: str = Field(
        "1",
        title="状态",
        description="1:启用 2:禁用，字符串类型"
    )


if __name__ == '__main__':
    exit(0)
