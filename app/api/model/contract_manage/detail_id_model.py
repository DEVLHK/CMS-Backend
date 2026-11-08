#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : detail_id_model.py
# @Project : CMS-Backend
"""收款/开票明细主键入参（删除、发票预览/下载共用）"""
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(title="ContractDetailIdInput")

    id: int = Field(..., title="明细主键ID")


if __name__ == '__main__':
    exit(0)
