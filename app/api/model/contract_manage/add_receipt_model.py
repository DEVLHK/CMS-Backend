#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_receipt_model.py
# @Project : CMS-Backend
"""新增收款明细（seq 后端按 合同编号+收款日期 分组自动+1；作废合同禁止维护）"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import OptionalAmount

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


class Input(BaseModel):
    model_config = ConfigDict(title="ReceiptAddInput")

    contractNo: str = Field(..., min_length=1, max_length=50, title="合同编号（带出，不可改）")
    receiptDate: str = Field(..., title="收款日期（YYYY-MM-DD，业务key之一）", pattern=DATE_PATTERN)
    receiptAmount: OptionalAmount = Field(None, ge=0, title="收款金额（≥0，选填，空串按未填）")


if __name__ == '__main__':
    exit(0)
