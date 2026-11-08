#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_invoice_model.py
# @Project : CMS-Backend
"""修改开票明细（合同编号不可改；开票类型/日期/金额/发票可改，日期变更时 seq 在新日期组内重算；≤今天；作废合同禁止维护）"""
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import OptionalAmount

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


class Input(BaseModel):
    model_config = ConfigDict(title="InvoiceUpdateInput")

    id: int = Field(..., title="主键ID")
    invoiceType: Literal["1", "2"] = Field(..., title="开票类型 1:专票 2:普票")
    invoiceDate: str = Field(..., title="开票日期（YYYY-MM-DD，≤今天）", pattern=DATE_PATTERN)
    invoiceAmount: OptionalAmount = Field(None, ge=0, title="开票金额（≥0，选填，空串按未填）")


if __name__ == '__main__':
    exit(0)
