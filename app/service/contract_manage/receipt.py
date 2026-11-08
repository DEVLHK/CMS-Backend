#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : receipt.py
# @Project : CMS-Backend
"""合同收款明细接口（contractManage），数据源：cms 库 contract_receipt_detail。
业务 key = 合同编号+收款日期+序号（seq 自动生成）；修改仅收款金额可改；作废合同禁止维护"""
from fastapi import Request

from app.api.model.contract_manage import add_receipt_model
from app.api.model.contract_manage import detail_id_model
from app.api.model.contract_manage import get_receipt_list_model
from app.api.model.contract_manage import update_receipt_model
from app.service.contract_manage.common import (
    current_user, err, fmt, get_active_contract, ok, page, rows, system_error)
from dao.contract_info import ContractInfoDao
from dao.contract_receipt_detail import ContractReceiptDetailDao


def _receipt_view(row):
    return {
        "id": int(row["id"]),
        "contractNo": row["contract_no"],
        "receiptDate": fmt(row["receipt_date"]),
        "seq": int(row["seq"]),
        "receiptAmount": float(row["receipt_amount"]) if row["receipt_amount"] is not None else None,
        "createTime": fmt(row["create_time"]),
        "createBy": row["create_by"],
        "updateTime": fmt(row["update_time"]),
        "updateBy": row["update_by"],
    }


def _contract_header(contract_dao, contract_row):
    """弹窗上方基础信息：合同编号、客户信息、余收款金额"""
    contract_amount = float(contract_row["contract_amount"])
    total_receipt = ContractReceiptDetailDao().total_amount(contract_row["contract_no"])
    return {
        "contractNo": contract_row["contract_no"],
        "companyName": contract_row["company_name"],
        "contactPerson": contract_row["contact_person"],
        "contactPhone": contract_row["contact_phone"],
        "remainingReceiptAmount": round(contract_amount - total_receipt, 2),
    }


# 远程排序白名单：camelCase（前端列 key）-> snake_case（DB 列），非法值回退默认排序
SORT_FIELD_MAP = {
    "receiptDate": "receipt_date",
    "receiptAmount": "receipt_amount",
}


def get_receipt_list(data: get_receipt_list_model.Input, request: Request):
    """
    @url:contractManage/getReceiptList（contractNo 带出；收款日期区间默认当天由前端控制；
    sortField=receiptDate/receiptAmount + sortOrder=asc/desc，非法值回退默认）
    """
    try:
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_no(data.contractNo).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.contractNo}")
        receipt_dao = ContractReceiptDetailDao()
        where_sql = ("contract_no = %s"
                     + (" and receipt_date >= %s" if data.receiptDateStart else "")
                     + (" and receipt_date <= %s" if data.receiptDateEnd else ""))
        values = [data.contractNo] + ([data.receiptDateStart] if data.receiptDateStart else []) \
                 + ([data.receiptDateEnd] if data.receiptDateEnd else [])
        total_res = receipt_dao.count_custom(where_sql, values)
        if total_res["code"] != 0:
            return err("-1", "查询收款明细总数失败")
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        # 远程排序（白名单）优先；默认按收款日期倒序、当日序号升序
        sort_column = SORT_FIELD_MAP.get((data.sortField or "").strip())
        sort_order = (data.sortOrder or "").strip().lower()
        if sort_column and sort_order in ("asc", "desc"):
            clauses = (f"order by {sort_column} {sort_order}, {receipt_dao.seq} "
                       f"limit {offset},{data.pageSize}")
        else:
            clauses = (f"order by {receipt_dao.receipt_date} desc, {receipt_dao.seq} "
                       f"limit {offset},{data.pageSize}")
        receipt_rows = rows(receipt_dao.query_custom(where_sql, values, clauses).get("data"))
        records = [_receipt_view(r) for r in receipt_rows]
        result = page(records, data.current, data.pageSize, total)
        result["header"] = _contract_header(contract_dao, contract_rows[0])
        return ok(result)
    except Exception:
        return system_error()


def add_receipt(data: add_receipt_model.Input, request: Request):
    """
    @url:contractManage/addReceipt（seq 按 合同编号+收款日期 分组自动+1；作废合同禁止维护）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(contract_dao, contract_no=data.contractNo)
        if contract_row is None:
            return err("E3004", active_error)
        receipt_dao = ContractReceiptDetailDao()
        seq = receipt_dao.next_seq(data.contractNo, data.receiptDate)
        if seq is None:
            return err("-1", "生成收款序号失败")
        insert_res = receipt_dao.insert({
            "contract_no": data.contractNo,
            "receipt_date": data.receiptDate,
            "seq": seq,
            "receipt_amount": data.receiptAmount,
            "create_by": user_name,
            "update_by": user_name,
        })
        if insert_res["code"] != 0:
            return err("-1", f"新增收款明细失败: {insert_res['data']}")
        return ok()
    except Exception:
        return system_error()


def update_receipt(data: update_receipt_model.Input, request: Request):
    """
    @url:contractManage/updateReceipt（仅收款金额可改；合同编号/收款日期不可改；作废合同禁止维护）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        receipt_dao = ContractReceiptDetailDao()
        receipt_rows = rows(receipt_dao.query_by_id(data.id).get("data"))
        if not receipt_rows:
            return err("E3101", f"收款明细不存在: {data.id}")
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(
            contract_dao, contract_no=receipt_rows[0]["contract_no"])
        if contract_row is None:
            return err("E3004", active_error)
        update_res = receipt_dao.update(
            {"receipt_amount": data.receiptAmount, "update_by": user_name},
            {receipt_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", f"修改收款明细失败: {update_res['data']}")
        return ok()
    except Exception:
        return system_error()


def delete_receipt(data: detail_id_model.Input, request: Request):
    """
    @url:contractManage/deleteReceipt（直接删除，二次确认由前端负责；作废合同禁止维护）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        receipt_dao = ContractReceiptDetailDao()
        receipt_rows = rows(receipt_dao.query_by_id(data.id).get("data"))
        if not receipt_rows:
            return err("E3101", f"收款明细不存在: {data.id}")
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(
            contract_dao, contract_no=receipt_rows[0]["contract_no"])
        if contract_row is None:
            return err("E3004", active_error)
        delete_res = receipt_dao.delete_by_id(data.id)
        if delete_res["code"] != 0:
            return err("-1", f"删除收款明细失败: {delete_res['data']}")
        return ok()
    except Exception:
        return system_error()


if __name__ == '__main__':
    exit(0)
