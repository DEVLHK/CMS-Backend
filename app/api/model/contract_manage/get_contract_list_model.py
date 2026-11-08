#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_contract_list_model.py
# @Project : CMS-Backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.common.query_field_types import QueryDate, QueryFlag, QueryMonth
from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    """GET 查询参数（除分页外均可空；编号/企业名称模糊查询不分大小写，月份可指定范围；
    空参数自动忽略，枚举字段兼容数字传参）"""
    model_config = ConfigDict(title="ContractListQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")
    contractNo: Optional[str] = Field(None, title="合同编号（模糊查询，不分大小写）")
    companyName: Optional[str] = Field(None, title="企业名称（模糊查询，不分大小写）")
    completionStatus: QueryFlag = Field(None, title="项目完成情况 1:完成 2:未完成")
    monthStart: QueryMonth = Field(None, title="合同月份起（YYYY-MM）", pattern=r"^\d{4}-\d{2}$")
    monthEnd: QueryMonth = Field(None, title="合同月份止（YYYY-MM）", pattern=r"^\d{4}-\d{2}$")
    region: QueryDate = Field(
        None, title="区域多选（英文逗号分隔，如 region=茂南区,化州市；空参数忽略）")
    projectType: Optional[str] = Field(None, title="项目类型（模糊查询）")
    status: QueryFlag = Field(None, title="状态 1:生效 2:作废")
    sortField: Optional[str] = Field(None, title="排序字段（camelCase，需在排序白名单内）")
    sortOrder: Optional[str] = Field(None, title="排序方向 asc/desc，默认不传按 id 倒序")


class ContractRecord(BaseModel):
    """合同基本信息记录（序号由前端按行序展示，不落表；余收款/余开票由后端联表汇总）"""
    model_config = ConfigDict(title="ContractRecord")

    id: int = Field(..., title="主键ID")
    contractNo: str = Field(..., title="合同编号（业务key，修改不可改）")
    month: str = Field(..., title="合同签订月份（YYYY-MM）")
    region: str = Field(..., title="区域")
    companyName: str = Field(..., title="企业名称（合同甲方）")
    projectType: str = Field(..., title="项目类型")
    contractFile: str = Field(..., title="合同文件相对路径")
    contractPdfFile: Optional[str] = Field(None, title="PDF 合同副本相对路径，NULL=未上传（控制下载按钮可用性）")
    contractAmount: float = Field(..., title="合同金额（合同技术服务费）")
    costSiteAudit: float = Field(0, title="成本核算-现场核查")
    costExpertReview: float = Field(0, title="成本核算-专家评审")
    costIntermediaryFee: float = Field(0, title="成本核算-居间费用")
    costReportCommission: float = Field(0, title="成本核算-报告编制提成")
    costQualification: float = Field(0, title="成本核算-资质费/分包费")
    costSalesmanCommission: float = Field(0, title="成本核算-业务员提成")
    vatTax: float = Field(0, title="增值税费=合同金额×1%（自动计算，readonly）")
    grossProfit: float = Field(0, title="毛利润=合同金额-成本核算合计（自动计算，readonly）")
    contactPerson: str = Field(..., title="联系人")
    contactPhone: str = Field(..., title="联系方式（手机号）")
    signDate: str = Field(..., title="签约日期（YYYY-MM-DD）")
    expireDate: str = Field(..., title="合同到期日期（YYYY-MM-DD，=签约日期+1年，后端自动计算）")
    completionStatus: str = Field("2", title="项目完成情况 1:完成 2:未完成")
    status: str = Field("1", title="状态 1:生效 2:作废")
    reportFile: Optional[str] = Field(None, title="报告文件相对路径（NULL=未上传）")
    totalReceiptAmount: float = Field(0, title="总收款金额")
    totalInvoiceAmount: float = Field(0, title="总开票金额")
    remainingReceiptAmount: float = Field(0, title="余收款金额=合同金额-总收款（readonly）")
    remainingInvoiceAmount: float = Field(0, title="余开票金额=合同金额-总开票（readonly）")
    createTime: Optional[str] = Field(None, title="创建时间")
    createBy: str = Field("", title="创建人")
    updateTime: Optional[str] = Field(None, title="更新时间")
    updateBy: str = Field("", title="更新人")


class Output(PageRecord):
    model_config = ConfigDict(title="ContractPageOutput")

    records: list[ContractRecord] = Field([], title="合同记录列表")


if __name__ == '__main__':
    exit(0)
