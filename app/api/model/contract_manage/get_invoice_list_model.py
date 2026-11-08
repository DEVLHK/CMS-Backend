#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_invoice_list_model.py
# @Project : CMS-Backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import QueryDate, QueryFlag
from app.api.model.system_manage.page_model import PageRecord
from app.api.model.contract_manage.get_receipt_list_model import ContractHeader


class Input(BaseModel):
    """GET 开票明细查询（合同编号必传；开票日期可指定区间，默认当天由前端控制；空参数自动忽略，
    invoiceType 兼容数字传参）"""
    model_config = ConfigDict(title="InvoiceListQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")
    contractNo: str = Field(..., title="合同编号（从合同基本信息带出）")
    invoiceDateStart: QueryDate = Field(None, title="开票日期起（YYYY-MM-DD）",
                                        pattern=r"^\d{4}-\d{2}-\d{2}$")
    invoiceDateEnd: QueryDate = Field(None, title="开票日期止（YYYY-MM-DD）",
                                      pattern=r"^\d{4}-\d{2}-\d{2}$")
    invoiceType: QueryFlag = Field(None, title="开票类型 1:专票 2:普票")
    sortField: Optional[str] = Field(None, title="排序字段（仅允许 invoiceDate/invoiceAmount，其余值回退默认）")
    sortOrder: Optional[str] = Field(None, title="排序方向 asc/desc（非法值回退默认排序）")


class InvoiceRecord(BaseModel):
    """开票明细记录（业务 key = 合同编号+开票日期+序号；发票为图片文件，选填）"""
    model_config = ConfigDict(title="InvoiceRecord")

    id: int = Field(..., title="主键ID")
    contractNo: str = Field(..., title="合同编号")
    invoiceType: str = Field(..., title="开票类型 1:专票 2:普票")
    invoiceDate: str = Field(..., title="开票日期（YYYY-MM-DD）")
    seq: int = Field(..., title="序号（同合同同日期内自动+1）")
    invoiceAmount: Optional[float] = Field(None, title="开票金额（≥0，选填）")
    invoiceFile: Optional[str] = Field(None, title="发票文件相对路径（图片/PDF/Office 常见格式，NULL=未上传）")
    createTime: Optional[str] = Field(None, title="创建时间")
    createBy: str = Field("", title="创建人")
    updateTime: Optional[str] = Field(None, title="更新时间")
    updateBy: str = Field("", title="更新人")


class Output(PageRecord):
    model_config = ConfigDict(title="InvoicePageOutput")

    header: ContractHeader = Field(..., title="上方基础信息（余开票金额口径）")
    records: list[InvoiceRecord] = Field([], title="开票明细记录列表")


if __name__ == '__main__':
    exit(0)
