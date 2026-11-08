#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_role_list_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.page_model import PageRecord
from app.api.model.system_manage.role.role_base_model import RoleBase


class Input(BaseModel):
    """GET 查询参数（全部可空，空则不过滤）"""
    model_config = ConfigDict(title="RoleListQuery")

    current: int = Field(1, title="页码")
    size: int = Field(10, title="每页条数")
    roleName: Optional[str] = Field(None, title="角色名称（模糊匹配）")
    roleCode: Optional[str] = Field(None, title="角色编码（模糊匹配）")
    status: Optional[str] = Field(None, title="状态 1:启用 2:禁用（精确）")


class RoleRecord(RoleBase):
    model_config = ConfigDict(title="RoleRecord")

    id: int = Field(..., title="角色ID")
    createBy: str = Field("", title="创建人")
    createTime: Optional[str] = Field(None, title="创建时间")
    updateBy: str = Field("", title="更新人")
    updateTime: Optional[str] = Field(None, title="更新时间")


class Output(PageRecord):
    model_config = ConfigDict(title="RolePageOutput")

    records: list[RoleRecord] = Field([], title="角色记录列表")


if __name__ == '__main__':
    exit(0)
