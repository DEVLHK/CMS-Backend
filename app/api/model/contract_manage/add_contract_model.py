#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_contract_model.py
# @Project : CMS-Backend
"""新增合同（须先 uploadContract 解析，凭 tempKey 关联暂存合同文件转正）"""
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import OptionalAmount

MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
PHONE_PATTERN = r"^1[3-9]\d{9}$"


class Input(BaseModel):
    """新增合同（contractAmount 等金额单位元、≥0；生成列 vatTax/grossProfit 由数据库自动计算）"""
    model_config = ConfigDict(title="ContractAddInput")

    tempKey: str = Field(..., title="暂存合同文件 key（uploadContract 返回）")
    contractNo: str = Field(..., min_length=1, max_length=50, title="合同编号（唯一，业务key）")
    month: str = Field(..., title="合同签订月份（YYYY-MM，按签约日期预填可修正）", pattern=MONTH_PATTERN)
    region: str = Field(..., min_length=1, title="区域（茂南区/化州市/高州市/电白区/高新区/滨海新区）")
    companyName: str = Field(..., min_length=1, max_length=200, title="企业名称（合同甲方）")
    projectType: str = Field(..., min_length=1, max_length=50, title="项目类型")
    contractAmount: float = Field(..., ge=0, title="合同金额（合同技术服务费）")
    costSiteAudit: OptionalAmount = Field(None, ge=0, title="成本核算-现场核查（选填）")
    costExpertReview: OptionalAmount = Field(None, ge=0, title="成本核算-专家评审（选填）")
    costIntermediaryFee: OptionalAmount = Field(None, ge=0, title="成本核算-居间费用（选填）")
    costReportCommission: OptionalAmount = Field(None, ge=0, title="成本核算-报告编制提成（选填）")
    costQualification: OptionalAmount = Field(None, ge=0, title="成本核算-资质费/分包费（选填）")
    costSalesmanCommission: OptionalAmount = Field(None, ge=0, title="成本核算-业务员提成（选填）")
    contactPerson: str = Field(..., min_length=1, max_length=30, title="联系人")
    contactPhone: str = Field(..., title="联系方式（手机号）", pattern=PHONE_PATTERN)
    signDate: str = Field(..., title="签约日期（YYYY-MM-DD）", pattern=DATE_PATTERN)
    completionStatus: Literal["1", "2"] = Field("2", title="项目完成情况 1:完成 2:未完成")


if __name__ == '__main__':
    exit(0)
