#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_receipt_list_model.py
# @Project : CMS-Backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import QueryDate
from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    """GET 收款明细查询（合同编号必传；收款日期可指定区间，默认当天由前端控制；空参数自动忽略）"""
    model_config = ConfigDict(title="ReceiptListQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")
    contractNo: str = Field(..., title="合同编号（从合同基本信息带出）")
    receiptDateStart: QueryDate = Field(None, title="收款日期起（YYYY-MM-DD）",
                                        pattern=r"^\d{4}-\d{2}-\d{2}$")
    receiptDateEnd: QueryDate = Field(None, title="收款日期止（YYYY-MM-DD）",
                                      pattern=r"^\d{4}-\d{2}-\d{2}$")
    sortField: Optional[str] = Field(None, title="排序字段（仅允许 receiptDate/receiptAmount，其余值回退默认）")
    sortOrder: Optional[str] = Field(None, title="排序方向 asc/desc（非法值回退默认排序）")


class ReceiptRecord(BaseModel):
    """收款明细记录（业务 key = 合同编号+收款日期+序号；修改时收款日期不可改）"""
    model_config = ConfigDict(title="ReceiptRecord")

    id: int = Field(..., title="主键ID")
    contractNo: str = Field(..., title="合同编号")
    receiptDate: str = Field(..., title="收款日期（YYYY-MM-DD）")
    seq: int = Field(..., title="序号（同合同同日期内自动+1）")
    receiptAmount: Optional[float] = Field(None, title="收款金额（≥0，选填）")
    createTime: Optional[str] = Field(None, title="创建时间")
    createBy: str = Field("", title="创建人")
    updateTime: Optional[str] = Field(None, title="更新时间")
    updateBy: str = Field("", title="更新人")


class ContractHeader(BaseModel):
    """弹窗上方基础信息：合同编号、客户信息、余收款/余开票金额（收款弹窗用前者，开票弹窗用后者）"""
    model_config = ConfigDict(title="ContractHeader")

    contractNo: str = Field(..., title="合同编号")
    companyName: str = Field(..., title="客户信息（企业名称）")
    contactPerson: str = Field("", title="联系人")
    contactPhone: str = Field("", title="联系方式")
    remainingReceiptAmount: Optional[float] = Field(None, title="余收款金额=合同金额-总收款（收款弹窗）")
    remainingInvoiceAmount: Optional[float] = Field(None, title="余开票金额=合同金额-总开票（开票弹窗）")


class Output(PageRecord):
    model_config = ConfigDict(title="ReceiptPageOutput")

    header: ContractHeader = Field(..., title="上方基础信息")
    records: list[ReceiptRecord] = Field([], title="收款明细记录列表")


if __name__ == '__main__':
    exit(0)
