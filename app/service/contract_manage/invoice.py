#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : invoice.py
# @Project : CMS-Backend
"""合同开票明细接口（contractManage），数据源：cms 库 contract_invoice_detail。
业务 key = 合同编号+开票日期+序号（seq 自动生成）；开票日期≤今天；发票仅图片；作废合同禁止维护"""
import datetime
import os

from fastapi import Request
from fastapi.responses import FileResponse

from app.api.model.contract_manage import add_invoice_model
from app.api.model.contract_manage import detail_id_model
from app.api.model.contract_manage import get_invoice_list_model
from app.api.model.contract_manage import update_invoice_model
from app.service.contract_manage import contract_file
from app.service.contract_manage.common import (
    current_user, err, fmt, get_active_contract, ok, page, rows, system_error)
from dao.contract_info import ContractInfoDao
from dao.contract_invoice_detail import ContractInvoiceDetailDao
from dao.contract_receipt_detail import ContractReceiptDetailDao


def _invoice_view(row):
    return {
        "id": int(row["id"]),
        "contractNo": row["contract_no"],
        "invoiceType": fmt(row["invoice_type"]),
        "invoiceDate": fmt(row["invoice_date"]),
        "seq": int(row["seq"]),
        "invoiceAmount": float(row["invoice_amount"]) if row["invoice_amount"] is not None else None,
        "invoiceFile": row["invoice_file"],
        "createTime": fmt(row["create_time"]),
        "createBy": row["create_by"],
        "updateTime": fmt(row["update_time"]),
        "updateBy": row["update_by"],
    }


def _invoice_header(contract_row):
    """弹窗上方基础信息：合同编号、客户信息、余开票金额"""
    contract_amount = float(contract_row["contract_amount"])
    total_invoice = ContractInvoiceDetailDao().total_amount(contract_row["contract_no"])
    return {
        "contractNo": contract_row["contract_no"],
        "companyName": contract_row["company_name"],
        "contactPerson": contract_row["contact_person"],
        "contactPhone": contract_row["contact_phone"],
        "remainingInvoiceAmount": round(contract_amount - total_invoice, 2),
    }


def _check_invoice_date(invoice_date):
    """开票日期只可 ≤ 今天"""
    if invoice_date > datetime.date.today().isoformat():
        return f"开票日期不可晚于今天: {invoice_date}"
    return None


# 远程排序白名单：camelCase（前端列 key）-> snake_case（DB 列），非法值回退默认排序
SORT_FIELD_MAP = {
    "invoiceDate": "invoice_date",
    "invoiceAmount": "invoice_amount",
}


def get_invoice_list(data: get_invoice_list_model.Input, request: Request):
    """
    @url:contractManage/getInvoiceList（contractNo 带出；开票日期区间默认当天由前端控制；
    sortField=invoiceDate/invoiceAmount + sortOrder=asc/desc，非法值回退默认）
    """
    try:
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_no(data.contractNo).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.contractNo}")
        invoice_dao = ContractInvoiceDetailDao()
        where_sql = ("contract_no = %s"
                     + (" and invoice_date >= %s" if data.invoiceDateStart else "")
                     + (" and invoice_date <= %s" if data.invoiceDateEnd else "")
                     + (" and invoice_type = %s" if data.invoiceType else ""))
        values = [data.contractNo] + ([data.invoiceDateStart] if data.invoiceDateStart else []) \
                 + ([data.invoiceDateEnd] if data.invoiceDateEnd else []) \
                 + ([data.invoiceType] if data.invoiceType else [])
        total_res = invoice_dao.count_custom(where_sql, values)
        if total_res["code"] != 0:
            return err("-1", "查询开票明细总数失败")
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        # 远程排序（白名单）优先；默认按开票日期倒序、当日序号升序
        sort_column = SORT_FIELD_MAP.get((data.sortField or "").strip())
        sort_order = (data.sortOrder or "").strip().lower()
        if sort_column and sort_order in ("asc", "desc"):
            clauses = (f"order by {sort_column} {sort_order}, {invoice_dao.seq} "
                       f"limit {offset},{data.pageSize}")
        else:
            clauses = (f"order by {invoice_dao.invoice_date} desc, {invoice_dao.seq} "
                       f"limit {offset},{data.pageSize}")
        invoice_rows = rows(invoice_dao.query_custom(where_sql, values, clauses).get("data"))
        records = [_invoice_view(r) for r in invoice_rows]
        result = page(records, data.current, data.pageSize, total)
        result["header"] = _invoice_header(contract_rows[0])
        return ok(result)
    except Exception:
        return system_error()


def add_invoice(data: add_invoice_model.Input, request: Request, file=None):
    """
    @url:contractManage/addInvoice（seq 按 合同编号+开票日期 分组自动+1；file 仅图片选传；作废合同禁止维护）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        date_error = _check_invoice_date(data.invoiceDate)
        if date_error:
            return err("E3201", date_error)
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(contract_dao, contract_no=data.contractNo)
        if contract_row is None:
            return err("E3004", active_error)
        if file is not None:
            ext_error = contract_file.check_ext(file, contract_file.INVOICE_EXTS)
            if ext_error:
                return err("E3001", ext_error)
        invoice_dao = ContractInvoiceDetailDao()
        seq = invoice_dao.next_seq(data.contractNo, data.invoiceDate)
        if seq is None:
            return err("-1", "生成开票序号失败")
        insert_res = invoice_dao.insert({
            "contract_no": data.contractNo,
            "invoice_type": data.invoiceType,
            "invoice_date": data.invoiceDate,
            "seq": seq,
            "invoice_amount": data.invoiceAmount,
            "invoice_file": None,
            "create_by": user_name,
            "update_by": user_name,
        })
        if insert_res["code"] != 0:
            return err("-1", f"新增开票明细失败: {insert_res['data']}")
        if file is not None:
            detail_rows = rows(invoice_dao.query_custom(
                "contract_no = %s and invoice_date = %s and seq = %s",
                [data.contractNo, data.invoiceDate, seq]).get("data"))
            if detail_rows:
                invoice_relative = contract_file.save_invoice_image(
                    data.contractNo, int(detail_rows[0]["id"]), file)
                invoice_dao.update({"invoice_file": invoice_relative, "update_by": user_name},
                                   {invoice_dao.id: int(detail_rows[0]["id"])})
        return ok()
    except Exception:
        return system_error()


def update_invoice(data: update_invoice_model.Input, request: Request, file=None):
    """
    @url:contractManage/updateInvoice（类型/日期/金额/发票可改；日期变更时 seq 在新日期组内重算；作废合同禁止维护）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        date_error = _check_invoice_date(data.invoiceDate)
        if date_error:
            return err("E3201", date_error)
        invoice_dao = ContractInvoiceDetailDao()
        invoice_rows = rows(invoice_dao.query_by_id(data.id).get("data"))
        if not invoice_rows:
            return err("E3202", f"开票明细不存在: {data.id}")
        invoice_row = invoice_rows[0]
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(
            contract_dao, contract_no=invoice_row["contract_no"])
        if contract_row is None:
            return err("E3004", active_error)
        if file is not None:
            ext_error = contract_file.check_ext(file, contract_file.INVOICE_EXTS)
            if ext_error:
                return err("E3001", ext_error)
        seq = int(invoice_row["seq"])
        if str(invoice_row["invoice_date"])[:10] != data.invoiceDate:
            # 日期变更：seq 在新日期组内重新生成，保证业务 key 唯一
            new_seq = invoice_dao.next_seq(invoice_row["contract_no"], data.invoiceDate)
            if new_seq is None:
                return err("-1", "生成开票序号失败")
            seq = new_seq
        update_res = invoice_dao.update(
            {"invoice_type": data.invoiceType, "invoice_date": data.invoiceDate, "seq": seq,
             "invoice_amount": data.invoiceAmount, "update_by": user_name},
            {invoice_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", f"修改开票明细失败: {update_res['data']}")
        if file is not None:
            invoice_relative = contract_file.save_invoice_image(
                invoice_row["contract_no"], int(invoice_row["id"]), file)
            invoice_dao.update({"invoice_file": invoice_relative, "update_by": user_name},
                               {invoice_dao.id: data.id})
        return ok()
    except Exception:
        return system_error()


def delete_invoice(data: detail_id_model.Input, request: Request):
    """
    @url:contractManage/deleteInvoice（直接删除并清理发票图片，二次确认由前端负责；作废合同禁止维护）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        invoice_dao = ContractInvoiceDetailDao()
        invoice_rows = rows(invoice_dao.query_by_id(data.id).get("data"))
        if not invoice_rows:
            return err("E3202", f"开票明细不存在: {data.id}")
        invoice_row = invoice_rows[0]
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(
            contract_dao, contract_no=invoice_row["contract_no"])
        if contract_row is None:
            return err("E3004", active_error)
        delete_res = invoice_dao.delete_by_id(data.id)
        if delete_res["code"] != 0:
            return err("-1", f"删除开票明细失败: {delete_res['data']}")
        if invoice_row["invoice_file"]:
            contract_file.delete_invoice_file(invoice_row["invoice_file"])
        return ok()
    except Exception:
        return system_error()


def preview_invoice(data: detail_id_model.Input, request: Request):
    """
    @url:contractManage/previewInvoice（浏览器内预览发票图片）
    """
    return _invoice_file_response(data, download=False)


def download_invoice(data: detail_id_model.Input, request: Request):
    """
    @url:contractManage/downloadInvoice（下载发票图片附件）
    """
    return _invoice_file_response(data, download=True)


def _invoice_file_response(data, download):
    try:
        invoice_dao = ContractInvoiceDetailDao()
        invoice_rows = rows(invoice_dao.query_by_id(data.id).get("data"))
        if not invoice_rows:
            return err("E3202", f"开票明细不存在: {data.id}")
        invoice_relative = invoice_rows[0]["invoice_file"]
        if not invoice_relative:
            return err("E3203", "该开票明细未上传发票")
        file_path = contract_file.absolute_of(invoice_relative)
        if file_path is None:
            return err("E3203", f"发票文件不存在: {invoice_relative}")
        filename = os.path.basename(invoice_relative)
        if download:
            return FileResponse(file_path, filename=filename)
        return FileResponse(file_path, media_type=_image_media_type(filename))
    except Exception:
        return system_error()


def _image_media_type(filename):
    """预览 media_type：图片按扩展名，其余一律 octet-stream（防上传 HTML 等文件被浏览器 inline 渲染）"""
    ext = os.path.splitext(filename)[1].lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".bmp": "image/bmp", ".webp": "image/webp",
            ".pdf": "application/pdf"}.get(ext, "application/octet-stream")


if __name__ == '__main__':
    exit(0)
