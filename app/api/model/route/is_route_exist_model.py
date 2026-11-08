#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 20:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : is_route_exist_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """GET 查询参数"""
    model_config = ConfigDict(title="RouteExistQuery")

    routeName: str = Field(
        ...,
        min_length=1,
        title="路由名称",
        description="检查是否存在于当前用户可访问路由与常量路由中"
    )


if __name__ == '__main__':
    exit(0)
