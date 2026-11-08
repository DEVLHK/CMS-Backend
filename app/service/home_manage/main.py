#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 21:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : main.py
# @Project : CMS-Backend
"""首页统计接口（homeManage），数据源：cms 库 contract_info（仅统计生效合同 status=1）。
统计口径："即将到期" = expire_date <= 今天 + 2 个月（含已过期，越紧急越靠前）"""
from fastapi import Request

from app.api.model.home_manage import get_expiring_contracts_model
from app.api.model.home_manage import get_home_stats_model
from app.service.contract_manage.common import current_user, err, fmt, ok, page, rows, system_error
from dao.contract_info import ContractInfoDao


def get_home_stats(data, request: Request):
    """
    @url:homeManage/getHomeStats（聚合统计：合同数/合同额/收款额/毛利润/即将到期数）
    """
    try:
        if current_user(request) is None:
            return err("9999", "token expired")
        stats_res = ContractInfoDao().query_home_stats()
        if stats_res["code"] != 0:
            return err("-1", "查询首页统计失败")
        stats = rows(stats_res["data"])[0]
        result = get_home_stats_model.Output(
            contractCount=int(stats["contract_count"]),
            totalContractAmount=round(float(stats["total_contract_amount"]), 2),
            totalReceiptAmount=round(float(stats["total_receipt_amount"]), 2),
            totalGrossProfit=round(float(stats["total_gross_profit"]), 2),
            expiringCount=int(stats["expiring_count"]),
        )
        return ok(result.model_dump())
    except Exception:
        return system_error()


def get_expiring_contracts(data: get_expiring_contracts_model.Input, request: Request):
    """
    @url:homeManage/getExpiringContracts（即将到期合同清单，expire_date 升序：已过期最前、越紧急越靠前）
    """
    try:
        if current_user(request) is None:
            return err("9999", "token expired")
        contract_dao = ContractInfoDao()
        total_res = contract_dao.count_expiring()
        if total_res["code"] != 0:
            return err("-1", "查询即将到期合同总数失败")
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        clauses = f"order by expire_date asc, id desc limit {offset},{data.pageSize}"
        contract_rows = rows(contract_dao.query_expiring(clauses).get("data"))
        records = [{
            "id": int(r["id"]),
            "contractNo": r["contract_no"],
            "companyName": r["company_name"],
            "expireDate": fmt(r["expire_date"]),
        } for r in contract_rows]
        return ok(page(records, data.current, data.pageSize, total))
    except Exception:
        return system_error()


if __name__ == '__main__':
    exit(0)
