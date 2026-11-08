#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 21:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_home_stats_model.py
# @Project : CMS-Backend
"""首页聚合统计（一次返回 5 个数字，仅统计生效合同）"""
from pydantic import BaseModel, ConfigDict, Field


class Output(BaseModel):
    model_config = ConfigDict(title="HomeStatsOutput")

    contractCount: int = Field(0, title="合同数（status=1）")
    totalContractAmount: float = Field(0, title="合同额=生效合同 contract_amount 合计")
    totalReceiptAmount: float = Field(0, title="收款额=生效合同的收款明细合计")
    totalGrossProfit: float = Field(0, title="毛利润=生效合同 gross_profit 合计")
    expiringCount: int = Field(0, title="即将到期合同数（expire_date <= 今天+2个月，含已过期）")


if __name__ == '__main__':
    exit(0)
