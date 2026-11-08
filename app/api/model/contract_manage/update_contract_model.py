#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_contract_model.py
# @Project : CMS-Backend
"""修改合同（contractNo 不可改；作废合同禁止修改；可重新上传覆盖旧合同，文件选传）"""
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import OptionalAmount
from app.api.model.contract_manage.add_contract_model import (
    DATE_PATTERN, MONTH_PATTERN, PHONE_PATTERN)


class Input(BaseModel):
    """修改合同（不收 contractNo；tempKey 不传=不更换合同文件，传=覆盖旧合同）"""
    model_config = ConfigDict(title="ContractUpdateInput")

    id: int = Field(..., title="主键ID")
    month: str = Field(..., title="合同签订月份（YYYY-MM）", pattern=MONTH_PATTERN)
    region: str = Field(..., min_length=1, title="区域")
    companyName: str = Field(..., min_length=1, max_length=200, title="企业名称")
    projectType: str = Field(..., min_length=1, max_length=50, title="项目类型")
    contractAmount: float = Field(..., ge=0, title="合同金额")
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
    tempKey: Optional[str] = Field(None, title="新合同暂存 key（不传=不更换合同文件）")


if __name__ == '__main__':
    exit(0)
