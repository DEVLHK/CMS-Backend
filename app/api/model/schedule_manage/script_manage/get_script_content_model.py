#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/30 21:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_script_content_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """查看脚本文件内容（按主键 scriptName 定位）"""
    model_config = ConfigDict(title="ScriptContentQuery")

    scriptName: str = Field(..., title="脚本名")


class Output(BaseModel):
    model_config = ConfigDict(title="ScriptContentOutput")

    scriptName: str = Field(..., title="脚本名")
    content: str = Field("", title="脚本文件内容（utf-8 文本）")


if __name__ == '__main__':
    exit(0)
