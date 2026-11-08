#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 14:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_script_info_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.schedule_manage.script_manage.script_base_model import ScriptParam


class Input(BaseModel):
    """修改脚本（按主键 scriptName 定位，仅传需要修改的；params 传空数组=清空为 []）"""
    model_config = ConfigDict(title="ScriptInfoUpdateInput")

    scriptName: str = Field(..., title="脚本名（定位条件，不可修改）")
    scriptPath: Optional[str] = Field(None, title="脚本路径（唯一）")
    description: Optional[str] = Field(None, title="脚本描述")
    params: Optional[list[ScriptParam]] = Field(None, title="入参定义数组（None=不修改，空数组=清空为 []）")
    content: Optional[str] = Field(
        None, title="脚本文件内容（utf-8 文本；None=不修改，传值=覆盖写入 scriptPath 指向文件）",
        description="写入采用同目录临时文件 + os.replace 原子替换；路径须在脚本目录白名单内")


if __name__ == '__main__':
    exit(0)
