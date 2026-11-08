#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 14:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : script_base_model.py
# @Project : Soybean-backend
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ScriptParam(BaseModel):
    """脚本入参定义元素（params JSON 数组元素，对齐 db-schema-script-info.md 第 3 节）"""
    model_config = ConfigDict(title="ScriptParam")

    param_name: str = Field(..., title="参数名")
    description: str = Field(..., title="参数说明")
    param_type: str = Field(..., title="参数类型 String/INT")
    mandatory: bool = Field(..., title="true=必填 false=可选")
    default: Any = Field(None, title="默认值，可 null")


if __name__ == '__main__':
    exit(0)
