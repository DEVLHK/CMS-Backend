#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 17:00
# @Author : KenLin
# @Email : kenlin@hisunglobal.com
# @File : common.py
# @Project : Soybean-backend
"""系统管理模块共享工具：响应构造、分页、行值格式化、JSON 解析"""
import json

from app.api.model.auth.api_response_model import ApiResponse

SYSTEM_ERROR = "系统出错,请联系系统管理员！"


def err(code, msg):
    return ApiResponse(code=code, msg=msg, data=None)


def ok(data=None):
    return ApiResponse(code="0000", msg="", data=data)


def page(records, current, size, total):
    return {"records": records, "current": current, "size": size, "total": total}


def fmt(value):
    """数据库行值 -> API 字符串（datetime -> 'YYYY-MM-DD HH:MM:SS'，TINYINT -> '1'/'2'，NULL -> None）"""
    if value is None:
        return None
    return str(value)


def parse_json(value):
    """JSON 列（route_props/buttons）-> dict/list；容忍驱动已解析或 NULL 的情况"""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)


def rows(df):
    """DataFrame -> [dict]，空表返回 []"""
    if df is None or len(df) == 0:
        return []
    return df.to_dict("records")


if __name__ == '__main__':
    exit(0)
