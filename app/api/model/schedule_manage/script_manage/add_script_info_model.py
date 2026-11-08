#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 14:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_script_info_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.schedule_manage.script_manage.script_base_model import ScriptParam


class Input(BaseModel):
    """新增脚本（create_by 取当前登录账号；params 为空写入 []）"""
    model_config = ConfigDict(title="ScriptInfoAddInput")

    scriptName: str = Field(..., title="脚本名（主键）")
    scriptPath: str = Field(..., title="脚本路径（唯一，仓库相对路径）")
    description: str = Field("", title="脚本描述")
    params: Optional[list[ScriptParam]] = Field(None, title="入参定义数组，可空（空写入 []）")


if __name__ == '__main__':
    exit(0)
