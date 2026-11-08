#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_menu_list_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.menu.menu_base_model import MenuBase
from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    """GET 查询参数（current/size 不传则返回全量）"""
    model_config = ConfigDict(title="MenuListQuery")

    current: Optional[int] = Field(None, title="页码，不传返回全量")
    size: Optional[int] = Field(None, title="每页条数，不传返回全量")


class MenuRecord(MenuBase):
    """菜单记录：库内 route_props/buttons JSON 解包后拍平输出"""
    model_config = ConfigDict(title="MenuRecord")

    id: int = Field(..., title="菜单ID")
    createBy: str = Field("", title="创建人")
    createTime: Optional[str] = Field(None, title="创建时间")
    updateBy: str = Field("", title="更新人")
    updateTime: Optional[str] = Field(None, title="更新时间")


class Output(PageRecord):
    model_config = ConfigDict(title="MenuPageOutput")

    records: list[MenuRecord] = Field([], title="菜单记录列表（平铺，按 parent_id + order 排序）")


if __name__ == '__main__':
    exit(0)
