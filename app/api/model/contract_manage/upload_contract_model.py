#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : upload_contract_model.py
# @Project : CMS-Backend
"""合同上传解析（multipart，file 必传；Input 无表单字段）"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """无表单字段，仅 file 上传"""
    model_config = ConfigDict(title="ContractUploadInput")


class Output(BaseModel):
    """解析结果：tempKey 供 addContract/updateContract 关联暂存文件；missing 为未解析到的字段（前端留空手填）"""
    model_config = ConfigDict(title="ContractParseOutput")

    tempKey: str = Field(..., title="暂存合同文件 key")
    contractNo: Optional[str] = Field(None, title="合同编号（解析）")
    companyName: Optional[str] = Field(None, title="企业名称（解析，合同甲方）")
    contactPerson: Optional[str] = Field(None, title="联系人（解析）")
    contactPhone: Optional[str] = Field(None, title="联系方式（解析）")
    projectType: Optional[str] = Field(None, title="项目类型（解析）")
    contractAmount: Optional[float] = Field(None, title="合同金额（解析，合同技术服务费）")
    signDate: Optional[str] = Field(None, title="签约日期（解析，YYYY-MM-DD）")
    month: Optional[str] = Field(None, title="合同月份（按签约日期推导，YYYY-MM）")
    region: Optional[str] = Field(None, title="区域（按甲方地址辅助预填，可修正）")
    missing: list[str] = Field([], title="未解析到的字段清单（camelCase）")


if __name__ == '__main__':
    exit(0)
