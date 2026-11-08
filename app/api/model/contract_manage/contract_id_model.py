#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : contract_id_model.py
# @Project : CMS-Backend
"""合同主键入参（删除/作废/报告上传共用）"""
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(title="ContractIdInput")

    id: int = Field(..., title="合同主键ID")


if __name__ == '__main__':
    exit(0)
