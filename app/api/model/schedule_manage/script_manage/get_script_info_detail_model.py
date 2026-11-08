#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 14:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_script_info_detail_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """查询脚本详情（按主键 scriptName 定位）"""
    model_config = ConfigDict(title="ScriptInfoDetailQuery")

    scriptName: str = Field(..., title="脚本名（精确）")


if __name__ == '__main__':
    exit(0)
