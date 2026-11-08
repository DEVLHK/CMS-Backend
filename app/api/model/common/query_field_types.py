#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : query_field_types.py
# @Project : CMS-Backend
"""查询/表单参数容错类型：前端常把空参数原样提交（如 invoiceDateStart=）或枚举传数字
（如 invoiceType=1），统一在此处归一化，避免 422。

- EmptyToNone: 空串/纯空白 -> None（用于可选日期、金额等）
- QueryFlag:   空串 -> None、int/float -> str（用于 Literal["1","2"] 枚举）
- OptionalAmount: 同 EmptyToNone，配合 Optional[float]
"""
from typing import Annotated, Literal, Optional

from pydantic import BeforeValidator


def _empty_to_none(value):
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _normalize_flag(value):
    value = _empty_to_none(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(int(value))
    return value


EmptyToNone = BeforeValidator(_empty_to_none)
FlagNormalize = BeforeValidator(_normalize_flag)

QueryDate = Annotated[Optional[str], EmptyToNone]          # YYYY-MM / YYYY-MM-DD，空串跳过 pattern
QueryMonth = Annotated[Optional[str], EmptyToNone]         # YYYY-MM
QueryFlag = Annotated[Optional[Literal["1", "2"]], FlagNormalize]
OptionalAmount = Annotated[Optional[float], EmptyToNone]   # ≥0 金额，空串按未填处理


if __name__ == '__main__':
    exit(0)
