# -*- coding: utf-8 -*-
# @Function: 
# @Author: Jamie
# @Time : 2024/12/26 19:56
from typing import List

from pydantic import BaseModel, Field


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
        title="下拉框label类型对应的值",
        description="下拉框label类型对应的值"
    )


if __name__ == '__main__':
    exit(0)
