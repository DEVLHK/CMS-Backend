#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : common.py
# @Project : CMS-Backend
"""合同管理模块共享工具：响应构造复用系统管理模块，另有登录解析与"生效合同"校验"""
import traceback

from fastapi import Request

from app.service.auth.main import _parse_access_token
from app.service.system_manage.common import SYSTEM_ERROR, err, fmt, ok, page, parse_json, rows
from dao.contract_info import ContractInfoDao
from utils.loging_util import logger

__all__ = ["SYSTEM_ERROR", "err", "fmt", "ok", "page", "parse_json", "rows",
           "system_error", "current_user", "get_active_contract"]


def system_error():
    for msg in str(traceback.format_exc()).split("\n"):
        logger.error(msg)
    return err("-1", SYSTEM_ERROR)


def current_user(request: Request):
    """从 Authorization 解析登录账号，失败返回 None"""
    authorization = request.headers.get("Authorization", "")
    token = authorization[7:] if authorization.startswith("Bearer ") else ""
    payload = _parse_access_token(token)
    return payload["userName"] if payload else None


def get_active_contract(contract_dao, contract_id=None, contract_no=None):
    """按 id/编号取合同行；不存在/已作废返回 (None, 错误信息)；生效返回 (row, None)。
    作废合同不可维护（决议 Q6），明细增删改与主表修改均须先过此校验"""
    if contract_id is not None:
        df = contract_dao.query_by_id(contract_id).get("data")
    else:
        df = contract_dao.query_by_no(contract_no).get("data")
    if df is None or len(df) == 0:
        return None, "合同不存在"
    row = df.to_dict("records")[0]
    if int(row["status"]) != 1:
        return None, f"合同已作废，禁止维护: {row['contract_no']}"
    return row, None


if __name__ == '__main__':
    exit(0)
