#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_invoice_model.py
# @Project : CMS-Backend
"""新增开票明细（开票日期≤今天；seq 后端按 合同编号+开票日期 分组自动+1；发票图片选传；作废合同禁止维护）"""
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import OptionalAmount

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


class Input(BaseModel):
    model_config = ConfigDict(title="InvoiceAddInput")

    contractNo: str = Field(..., min_length=1, max_length=50, title="合同编号（带出，不可改）")
    invoiceType: Literal["1", "2"] = Field(..., title="开票类型 1:专票 2:普票")
    invoiceDate: str = Field(..., title="开票日期（YYYY-MM-DD，≤今天，业务key之一）", pattern=DATE_PATTERN)
    invoiceAmount: OptionalAmount = Field(None, ge=0, title="开票金额（≥0，选填，空串按未填）")


if __name__ == '__main__':
    exit(0)
