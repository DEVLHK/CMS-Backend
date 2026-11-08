#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_user_list_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.page_model import PageRecord
from app.api.model.system_manage.user.user_base_model import UserBase


class Input(BaseModel):
    """GET 查询参数（全部可空，空则不过滤）"""
    model_config = ConfigDict(title="UserListQuery")

    current: int = Field(1, title="页码")
    size: int = Field(10, title="每页条数")
    userName: Optional[str] = Field(None, title="用户名（模糊匹配）")
    nickName: Optional[str] = Field(None, title="昵称（模糊匹配）")
    userGender: Optional[str] = Field(None, title="性别 1:男 2:女（精确）")
    userPhone: Optional[str] = Field(None, title="手机号（精确）")
    userEmail: Optional[str] = Field(None, title="邮箱（精确）")
    status: Optional[str] = Field(None, title="状态 1:启用 2:禁用（精确）")


class UserRecord(UserBase):
    model_config = ConfigDict(title="UserRecord")

    id: int = Field(..., title="用户ID")
    createBy: str = Field("", title="创建人")
    createTime: Optional[str] = Field(None, title="创建时间")
    updateBy: str = Field("", title="更新人")
    updateTime: Optional[str] = Field(None, title="更新时间")


class Output(PageRecord):
    model_config = ConfigDict(title="UserPageOutput")

    records: list[UserRecord] = Field([], title="用户记录列表")


if __name__ == '__main__':
    exit(0)
