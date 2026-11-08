#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_receipt_model.py
# @Project : CMS-Backend
"""修改收款明细（仅收款金额可改；收款日期/合同编号不可改；作废合同禁止维护）"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import OptionalAmount


class Input(BaseModel):
    model_config = ConfigDict(title="ReceiptUpdateInput")

    id: int = Field(..., title="主键ID")
    receiptAmount: OptionalAmount = Field(None, ge=0, title="收款金额（≥0，选填，空串按未填）")


if __name__ == '__main__':
    exit(0)
