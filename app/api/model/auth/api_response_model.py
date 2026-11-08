#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 10:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : api_response_model.py
# @Project : Soybean-backend
from typing import Union
from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    """Soybean Admin 前端通用响应信封，字段名固定：code/msg/data"""
    model_config = ConfigDict(title="ApiResponse")

    code: str = Field(
        "0000",
        title="Response Code",
        description='"0000"=成功；"8888"/"8889"=静默登出；"7777"/"7778"=弹窗登出；"9999"/"9998"/"3333"=token过期；其他=toast提示msg'
    )
    msg: str = Field(
        "",
        title="Response Message",
        description='成功为""，失败时前端直接toast显示'
    )
    data: Union[bool, dict, list, None] = Field(
        None,
        title="Response Data",
        description="业务数据，失败时为null（isRouteExist 等接口可能返回 bool）"
    )


if __name__ == '__main__':
    exit(0)
