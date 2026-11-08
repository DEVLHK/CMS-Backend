#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 14:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_script_info_list_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    """GET 查询参数（均可空）"""
    model_config = ConfigDict(title="ScriptInfoListQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")
    scriptName: Optional[str] = Field(None, title="脚本名（模糊匹配）")


class ScriptInfoRecord(BaseModel):
    """脚本信息记录（params 输出 JSON 数组，空为 []）"""
    model_config = ConfigDict(title="ScriptInfoRecord")

    scriptName: str = Field(..., title="脚本名（主键）")
    scriptPath: str = Field(..., title="脚本路径")
    description: str = Field("", title="脚本描述")
    params: list = Field([], title="入参定义数组")
    createTime: Optional[str] = Field(None, title="创建时间")
    createBy: str = Field("", title="创建人（登录账号）")
    updateTime: Optional[str] = Field(None, title="更新时间")
    updateBy: str = Field("", title="更新人（登录账号）")
    ts: Optional[str] = Field(None, title="时间戳（数据库自动维护）")


class Output(PageRecord):
    model_config = ConfigDict(title="ScriptInfoPageOutput")

    records: list[ScriptInfoRecord] = Field([], title="脚本信息记录列表")


if __name__ == '__main__':
    exit(0)
