#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : main.py
# @Project : CMS-Backend
"""合同基本信息接口（contractManage），数据源：cms 库 contract_info。
上传解析 -> 暂存 -> 落库转正；合同/报告文件管理见 contract_file.py"""
import datetime
import os

from fastapi import Request, UploadFile
from fastapi.responses import FileResponse

from app.api.model.contract_manage import add_contract_model
from app.api.model.contract_manage import contract_id_model
from app.api.model.contract_manage import get_contract_list_model
from app.api.model.contract_manage import update_contract_model
from app.api.model.contract_manage import upload_contract_model
from app.service.contract_manage import contract_file, contract_parser
from app.service.contract_manage.common import (
    current_user, err, fmt, get_active_contract, ok, page, rows, system_error)
from dao.contract_info import ContractInfoDao
from dao.contract_invoice_detail import ContractInvoiceDetailDao
from dao.contract_receipt_detail import ContractReceiptDetailDao
from utils.loging_util import logger


def _calc_expire_date(sign_date):
    """合同到期日期 = 签约日期 + 1 年（次年同月同日；2/29 → 次年 2/28）"""
    try:
        return sign_date.replace(year=sign_date.year + 1)
    except ValueError:  # 2 月 29 日
        return sign_date.replace(year=sign_date.year + 1, month=2, day=28)


# 远程排序白名单：camelCase（前端列 key）-> snake_case（DB 列）
SORT_FIELD_MAP = {
    "id": "id",
    "contractNo": "contract_no",
    "month": "contract_month",
    "region": "region",
    "companyName": "company_name",
    "projectType": "project_type",
    "contractAmount": "contract_amount",
    "vatTax": "vat_tax",
    "grossProfit": "gross_profit",
    "signDate": "sign_date",
    "expireDate": "expire_date",
    "completionStatus": "completion_status",
    "status": "status",
    "createTime": "create_time",
}


def _contract_view(row):
    """contract_info 行（联表含 total_receipt/total_invoice）-> 前端记录结构"""
    contract_amount = float(row["contract_amount"])
    total_receipt = float(row.get("total_receipt", 0) or 0)
    total_invoice = float(row.get("total_invoice", 0) or 0)
    return {
        "id": int(row["id"]),
        "contractNo": row["contract_no"],
        "month": row["contract_month"],
        "region": row["region"],
        "companyName": row["company_name"],
        "projectType": row["project_type"],
        "contractFile": row["contract_file"],
        "contractPdfFile": row.get("contract_pdf_file"),
        "contractAmount": contract_amount,
        "costSiteAudit": float(row["cost_site_audit"] or 0),
        "costExpertReview": float(row["cost_expert_review"] or 0),
        "costIntermediaryFee": float(row["cost_intermediary_fee"] or 0),
        "costReportCommission": float(row["cost_report_commission"] or 0),
        "costQualification": float(row["cost_qualification"] or 0),
        "costSalesmanCommission": float(row["cost_salesman_commission"] or 0),
        "vatTax": float(row["vat_tax"] or 0),
        "grossProfit": float(row["gross_profit"] or 0),
        "contactPerson": row["contact_person"],
        "contactPhone": row["contact_phone"],
        "signDate": fmt(row["sign_date"]),
        "expireDate": fmt(row["expire_date"]),
        "completionStatus": fmt(row["completion_status"]),
        "status": fmt(row["status"]),
        "reportFile": row["report_file"],
        "totalReceiptAmount": total_receipt,
        "totalInvoiceAmount": total_invoice,
        "remainingReceiptAmount": round(contract_amount - total_receipt, 2),
        "remainingInvoiceAmount": round(contract_amount - total_invoice, 2),
        "createTime": fmt(row["create_time"]),
        "createBy": row["create_by"],
        "updateTime": fmt(row["update_time"]),
        "updateBy": row["update_by"],
    }


def get_contract_list(data: get_contract_list_model.Input, request: Request):
    """
    @url:contractManage/getContractList（编号/企业名称模糊不分大小写；月份范围默认当月由前端控制）
    """
    try:
        contract_dao = ContractInfoDao()
        fields = {}
        extra_conditions = []
        contract_no = (data.contractNo or "").strip()
        company_name = (data.companyName or "").strip()
        project_type = (data.projectType or "").strip()
        if contract_no:
            fields[contract_dao.contract_no] = ("like", f"%{contract_no}%")
        if company_name:
            fields[contract_dao.company_name] = ("like", f"%{company_name}%")
        if data.completionStatus:
            fields[contract_dao.completion_status] = ("=", data.completionStatus)
        if data.monthStart:
            extra_conditions.append((f"c.{contract_dao.contract_month} >= %s", data.monthStart))
        if data.monthEnd:
            extra_conditions.append((f"c.{contract_dao.contract_month} <= %s", data.monthEnd))
        regions = [r.strip() for r in (data.region or "").split(",") if r and r.strip()]
        if regions:
            extra_conditions.append(
                (f"c.{contract_dao.region} IN ({','.join(['%s'] * len(regions))})", regions))
        if project_type:
            fields[contract_dao.project_type] = ("like", f"%{project_type}%")
        if data.status:
            fields[contract_dao.status] = ("=", data.status)
        total_res = contract_dao.count(fields, extra_conditions)
        if total_res["code"] != 0:
            return err("-1", "查询合同总数失败")
        total = total_res["data"]
        offset = (data.current - 1) * data.pageSize
        sort_column = SORT_FIELD_MAP.get((data.sortField or "").strip())
        sort_order = "asc" if (data.sortOrder or "").strip().lower() == "asc" else \
            ("desc" if (data.sortOrder or "").strip().lower() == "desc" else None)
        if sort_column and sort_order:
            order_clause = f"order by c.{sort_column} {sort_order}, c.{contract_dao.id} desc"
        else:
            # 默认按签约日期倒序，id 兜底保持同日期记录稳定次序
            order_clause = f"order by c.{contract_dao.sign_date} desc, c.{contract_dao.id} desc"
        clauses = f"{order_clause} limit {offset},{data.pageSize}"
        contract_rows = rows(contract_dao.query_with_totals(fields, clauses, extra_conditions).get("data"))
        records = [_contract_view(r) for r in contract_rows]
        return ok(page(records, data.current, data.pageSize, total))
    except Exception:
        return system_error()


def upload_contract(data: upload_contract_model.Input, request: Request, file: UploadFile):
    """
    @url:contractManage/uploadContract（先上传后解析：.doc 暂存 + 固定格式解析，返回预填字段）
    """
    try:
        ext_error = contract_file.check_ext(file, contract_file.CONTRACT_EXTS)
        if ext_error:
            return err("E3001", ext_error)
        temp_key = contract_file.save_incoming(file)
        source = contract_file.resolve_incoming(temp_key)
        fields, missing = contract_parser.parse_contract(source)
        result = upload_contract_model.Output(tempKey=temp_key, missing=missing, **fields)
        return ok(result.model_dump())
    except Exception:
        return system_error()


def _contract_data(data, contract_no=None):
    """add/update 公共字段 -> DB 列（生成列与 create/update 审计列不在此处）"""
    return {
        "contract_month": data.month,
        "region": data.region,
        "company_name": data.companyName,
        "project_type": data.projectType,
        "contract_amount": data.contractAmount,
        "cost_site_audit": data.costSiteAudit or 0,
        "cost_expert_review": data.costExpertReview or 0,
        "cost_intermediary_fee": data.costIntermediaryFee or 0,
        "cost_report_commission": data.costReportCommission or 0,
        "cost_qualification": data.costQualification or 0,
        "cost_salesman_commission": data.costSalesmanCommission or 0,
        "contact_person": data.contactPerson,
        "contact_phone": data.contactPhone,
        "sign_date": data.signDate,
        "completion_status": data.completionStatus,
    }


def add_contract(data: add_contract_model.Input, request: Request, filePdf: UploadFile = None):
    """
    @url:contractManage/addContract（tempKey 关联暂存 Word 转正；filePdf 必传=.pdf 副本存档，解析只用 Word）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        source = contract_file.resolve_incoming(data.tempKey)
        if source is None:
            return err("E3002", f"暂存合同文件不存在或已失效，请重新上传: {data.tempKey}")
        if filePdf is None or not getattr(filePdf, "filename", ""):
            return err("E3001", "缺少合同 PDF 副本（filePdf），请上传 .pdf 文件")
        ext_error = contract_file.check_ext(filePdf, contract_file.CONTRACT_PDF_EXTS)
        if ext_error:
            return err("E3001", ext_error)
        contract_dao = ContractInfoDao()
        if len(rows(contract_dao.query_by_no(data.contractNo).get("data"))) > 0:
            return err("E3003", f"合同编号已存在: {data.contractNo}")
        # 先落盘（Word 转正 + PDF 保存，文件名保留原始名）再落库；落库失败回滚删除文件
        word_rel = contract_file.promote_incoming(data.tempKey, data.contractNo)
        if word_rel is None:
            return err("-1", "合同 Word 文件转正失败，请重新上传")
        pdf_rel = contract_file.save_contract_pdf(data.contractNo, filePdf, occupied={word_rel})
        insert_data = _contract_data(data)
        sign_date = datetime.date.fromisoformat(data.signDate)
        insert_data.update({
            "contract_no": data.contractNo,
            "contract_file": word_rel,
            "contract_pdf_file": pdf_rel,
            "expire_date": _calc_expire_date(sign_date),
            "report_file": None,
            "create_by": user_name,
            "update_by": user_name,
        })
        insert_res = contract_dao.insert(insert_data)
        if insert_res["code"] != 0:
            contract_file.delete_file_at(word_rel)
            contract_file.delete_file_at(pdf_rel)
            return err("-1", f"保存合同失败: {insert_res['data']}")
        return ok()
    except Exception:
        return system_error()


def update_contract(data: update_contract_model.Input, request: Request,
                    file: UploadFile = None, filePdf: UploadFile = None):
    """
    @url:contractManage/updateContract（contractNo 不可改；作废合同禁止修改；
    file 选传=覆盖 Word 合同；filePdf 选传=覆盖 PDF 副本，两者语义独立）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        if filePdf is not None and getattr(filePdf, "filename", ""):
            ext_error = contract_file.check_ext(filePdf, contract_file.CONTRACT_PDF_EXTS)
            if ext_error:
                return err("E3001", ext_error)
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(contract_dao, contract_id=data.id)
        if contract_row is None:
            return err("E3004", active_error)
        update_data = _contract_data(data)
        update_data["update_by"] = user_name
        # 到期日期随签约日期自动重算（后端计算，前端不传）
        update_data["expire_date"] = _calc_expire_date(
            datetime.date.fromisoformat(data.signDate))
        contract_no = contract_row["contract_no"]
        old_word_rel = contract_row.get("contract_file")
        old_pdf_rel = contract_row.get("contract_pdf_file")
        old_report_rel = contract_row.get("report_file")
        # Word 覆盖：tempKey（解析流程）或 file 直接重传，保留原始文件名，删旧文件防孤儿
        word_new_rel = None
        if data.tempKey:
            source = contract_file.resolve_incoming(data.tempKey)
            if source is None:
                return err("E3002", f"暂存合同文件不存在或已失效，请重新上传: {data.tempKey}")
            word_new_rel = contract_file.promote_incoming(data.tempKey, contract_no)
            if word_new_rel is None:
                return err("-1", "合同文件覆盖失败")
        elif file is not None and getattr(file, "filename", ""):
            ext_error = contract_file.check_ext(file, contract_file.CONTRACT_EXTS)
            if ext_error:
                return err("E3001", ext_error)
            word_new_rel = contract_file.save_contract_word(
                contract_no, file, occupied={old_pdf_rel, old_report_rel})
        # PDF 覆盖：保留原始文件名；避让 Word 新路径与报告
        pdf_uploaded = filePdf is not None and getattr(filePdf, "filename", "")
        pdf_new_rel = None
        if pdf_uploaded:
            pdf_new_rel = contract_file.save_contract_pdf(
                contract_no, filePdf,
                occupied={old_report_rel, word_new_rel or old_word_rel})
            update_data["contract_pdf_file"] = pdf_new_rel
        if word_new_rel:
            update_data["contract_file"] = word_new_rel
        update_res = contract_dao.update(update_data, {contract_dao.id: data.id})
        if update_res["code"] != 0:
            for rel in (word_new_rel, pdf_new_rel):
                if rel:
                    contract_file.delete_file_at(rel)
            return err("-1", f"修改合同失败: {update_res['data']}")
        # 落库成功后清理被替换的旧文件（路径不同才删）
        if word_new_rel and word_new_rel != old_word_rel:
            contract_file.delete_file_at(old_word_rel)
        if pdf_new_rel and pdf_new_rel != old_pdf_rel:
            contract_file.delete_file_at(old_pdf_rel)
        return ok()
    except Exception:
        return system_error()


def delete_contract(data: contract_id_model.Input, request: Request):
    """
    @url:contractManage/deleteContract（删除合同+收款/开票明细+文件目录，二次确认由前端负责）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_id(data.id).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.id}")
        contract_no = contract_rows[0]["contract_no"]
        if contract_dao.delete_by_id(data.id)["code"] != 0:
            return err("-1", "删除合同失败")
        ContractReceiptDetailDao().delete_by_contract_no(contract_no)
        ContractInvoiceDetailDao().delete_by_contract_no(contract_no)
        contract_file.delete_contract_dir(contract_no)
        return ok()
    except Exception:
        return system_error()


def void_contract(data: contract_id_model.Input, request: Request):
    """
    @url:contractManage/voidContract（status 置 2；作废后主表不可改、明细禁增删改）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_id(data.id).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.id}")
        if int(contract_rows[0]["status"]) == 2:
            return err("E3005", f"合同已作废: {contract_rows[0]['contract_no']}")
        update_res = contract_dao.update(
            {"status": 2, "update_by": user_name}, {contract_dao.id: data.id})
        if update_res["code"] != 0:
            return err("-1", f"作废合同失败: {update_res['data']}")
        return ok()
    except Exception:
        return system_error()


def upload_report(data: contract_id_model.Input, request: Request, file: UploadFile):
    """
    @url:contractManage/uploadReport（报告上传：保留原始文件名，覆盖式回写 report_file，删旧文件防孤儿）
    """
    try:
        user_name = current_user(request)
        if user_name is None:
            return err("9999", "token expired")
        ext_error = contract_file.check_ext(file, contract_file.REPORT_EXTS)
        if ext_error:
            return err("E3001", ext_error)
        contract_dao = ContractInfoDao()
        contract_row, active_error = get_active_contract(contract_dao, contract_id=data.id)
        if contract_row is None:
            return err("E3004", active_error)
        old_report_rel = contract_row.get("report_file")
        new_report_rel = contract_file.save_report(
            contract_row["contract_no"], file,
            occupied={contract_row.get("contract_file"), contract_row.get("contract_pdf_file")})
        update_res = contract_dao.update(
            {"report_file": new_report_rel, "update_by": user_name}, {contract_dao.id: data.id})
        if update_res["code"] != 0:
            contract_file.delete_file_at(new_report_rel)
            return err("-1", f"保存报告失败: {update_res['data']}")
        if new_report_rel != old_report_rel:
            contract_file.delete_file_at(old_report_rel)
        return ok()
    except Exception:
        return system_error()


def download_contract(data: contract_id_model.Input, request: Request):
    """
    @url:contractManage/downloadContract（下载/在线预览合同 Word 原件，.doc 由前端按附件处理）
    """
    try:
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_id(data.id).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.id}")
        file_path = contract_file.absolute_of(contract_rows[0]["contract_file"])
        if file_path is None:
            return err("E3006", f"合同文件不存在: {contract_rows[0]['contract_file']}")
        return FileResponse(file_path, filename=os.path.basename(contract_rows[0]["contract_file"]))
    except Exception:
        return system_error()


def download_contract_pdf(data: contract_id_model.Input, request: Request):
    """
    @url:contractManage/downloadContractPdf（下载合同 PDF 副本；未上传/文件缺失报 E3302；作废合同允许下载）
    """
    try:
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_id(data.id).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.id}")
        pdf_relative = contract_rows[0].get("contract_pdf_file")
        if not pdf_relative:
            return err("E3302", f"合同 PDF 副本未上传: {contract_rows[0]['contract_no']}")
        file_path = contract_file.absolute_of(pdf_relative)
        if file_path is None:
            return err("E3302", f"合同 PDF 文件不存在: {pdf_relative}")
        return FileResponse(file_path, filename=os.path.basename(pdf_relative))
    except Exception:
        return system_error()


def download_report(data: contract_id_model.Input, request: Request):
    """
    @url:contractManage/downloadReport（下载报告文件；未上传报错；作废合同允许下载）
    """
    try:
        contract_dao = ContractInfoDao()
        contract_rows = rows(contract_dao.query_by_id(data.id).get("data"))
        if not contract_rows:
            return err("E3004", f"合同不存在: {data.id}")
        report_relative = contract_rows[0].get("report_file")
        if not report_relative:
            return err("E3303", f"报告未上传: {contract_rows[0]['contract_no']}")
        file_path = contract_file.absolute_of(report_relative)
        if file_path is None:
            return err("E3303", f"报告文件不存在: {report_relative}")
        filename = os.path.basename(file_path)
        return FileResponse(file_path, filename=filename)
    except Exception:
        return system_error()


if __name__ == '__main__':
    exit(0)
