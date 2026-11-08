#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/6/21 02:35
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : upgrade_oms_model.py
# @Project : CMS-Backend
from pydantic import BaseModel, Field
from typing import List

class Resource(BaseModel):
    fileName: str = Field(
        default="",
        title="文件名称",
        description="文件名称"
    )
    id: str = Field(
        default="",
        title="日期变量拼接上面随机生成的目录名",
        description="日期变量拼接上面随机生成的目录名"
    )
class Input(BaseModel):
    fileList: List[Resource] = Field(
        default_factory=lambda: [Resource()],
        title="资源列表",
        description="资源列表"
    )


class Output(BaseModel):
    pass

if __name__ == '__main__' :
    exit(0)
