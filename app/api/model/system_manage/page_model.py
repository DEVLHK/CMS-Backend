#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : page_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, Field


class PageRecord(BaseModel):
    """分页响应结构（前端 PaginatingQueryRecord）"""
    records: list = Field(
        [],
        title="当前页记录",
        description="当前页数据列表"
    )
    current: int = Field(
        1,
        title="页码",
        description="当前页码，从1开始"
    )
    size: int = Field(
        10,
        title="每页条数"
    )
    total: int = Field(
        0,
        title="总记录数"
    )


if __name__ == '__main__':
    exit(0)
