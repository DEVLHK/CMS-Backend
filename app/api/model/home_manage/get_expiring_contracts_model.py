#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 21:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_expiring_contracts_model.py
# @Project : CMS-Backend
"""即将到期合同清单（分页，按到期日期升序，越紧急越靠前）"""
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    model_config = ConfigDict(title="ExpiringContractsQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")


class ExpiringContractRecord(BaseModel):
    model_config = ConfigDict(title="ExpiringContractRecord")

    id: int = Field(..., title="合同主键ID")
    contractNo: str = Field(..., title="合同编号")
    companyName: str = Field(..., title="企业名称（合同甲方）")
    expireDate: str = Field(..., title="合同到期日期（YYYY-MM-DD）")


class Output(PageRecord):
    model_config = ConfigDict(title="ExpiringContractsPageOutput")

    records: list[ExpiringContractRecord] = Field([], title="即将到期合同列表")


if __name__ == '__main__':
    exit(0)
