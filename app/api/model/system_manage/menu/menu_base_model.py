#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : menu_base_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MenuButton(BaseModel):
    """按钮权限码（对齐前端 Api.SystemManage.MenuButton）"""
    model_config = ConfigDict(title="MenuButton")

    code: str = Field(
        ...,
        min_length=1,
        title="按钮权限码",
        description="如 B_USER::BTN_ADD"
    )
    desc: str = Field(
        "",
        title="按钮描述"
    )


class MenuBase(BaseModel):
    """菜单公共字段（对齐前端 Api.SystemManage.Menu，路由属性已拍平；
    库内 i18nKey/keepAlive/order 等存 route_props JSON）"""
    parentId: int = Field(
        0,
        title="父菜单ID",
        description="0=顶级"
    )
    menuType: str = Field(
        "2",
        title="菜单类型",
        description="1:目录 2:菜单，字符串类型"
    )
    menuName: str = Field(
        ...,
        min_length=1,
        title="菜单名称"
    )
    routeName: str = Field(
        ...,
        min_length=1,
        title="路由名称",
        description="唯一"
    )
    routePath: str = Field(
        ...,
        min_length=1,
        title="路由路径"
    )
    component: Optional[str] = Field(
        None,
        title="组件路径",
        description="目录为null"
    )
    icon: str = Field(
        "",
        title="图标名"
    )
    iconType: str = Field(
        "1",
        title="图标类型",
        description="1:iconify 2:本地，字符串类型"
    )
    buttons: Optional[list[MenuButton]] = Field(
        None,
        title="按钮权限码列表",
        description='[{"code":"B_USER::BTN_ADD","desc":"新增用户"}]'
    )
    i18nKey: Optional[str] = Field(None, title="国际化key")
    keepAlive: bool = Field(False, title="是否缓存")
    constant: bool = Field(False, title="是否固定路由")
    order: int = Field(0, title="排序")
    href: Optional[str] = Field(None, title="外链地址")
    hideInMenu: bool = Field(False, title="是否在菜单中隐藏")
    activeMenu: Optional[str] = Field(None, title="高亮菜单")
    multiTab: bool = Field(False, title="是否多标签页")
    fixedIndexInTab: Optional[int] = Field(None, title="固定标签页序号")
    query: Optional[dict] = Field(None, title="路由查询参数")

    @field_validator("query", mode="before")
    @classmethod
    def _query_empty_list_to_none(cls, value):
        """前端表单的 query 输入为空时会提交 []，归一为 None（合法值为对象或 null）"""
        if isinstance(value, list) and len(value) == 0:
            return None
        return value
    status: str = Field(
        "1",
        title="状态",
        description="1:启用 2:禁用，字符串类型"
    )


if __name__ == '__main__':
    exit(0)
