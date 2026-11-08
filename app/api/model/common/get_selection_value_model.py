# -*- coding: utf-8 -*-
# @Function: 
# @Author: Jamie
# @Time : 2024/12/18 15:31


from pydantic import BaseModel, Field


class Input(BaseModel):
    types: list = Field(
        default=None,
        title="下拉框label类型",
        description="下拉框label类型"
    )


class Output(BaseModel):
    selectionValues: dict = Field(
        default={},
        title="下拉框label类型对应的值",
        description="下拉框label类型对应的值"
    )


if __name__ == '__main__':
    exit(0)
