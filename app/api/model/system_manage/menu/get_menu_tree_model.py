#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_menu_tree_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Output(BaseModel):
    """菜单树节点（前端 MenuTree，字段名必须是 label/pId）"""
    model_config = ConfigDict(title="MenuTreeNode")

    id: int = Field(..., title="菜单ID")
    label: str = Field(..., title="显示名称（menu_name）")
    pId: int = Field(..., title="父菜单ID")
    children: Optional[list] = Field(None, title="子节点，叶子为null")


if __name__ == '__main__':
    exit(0)
