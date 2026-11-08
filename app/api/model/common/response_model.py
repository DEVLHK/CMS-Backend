#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/7/26 02:10
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : response_model.py
# @Project : hbs_flink
from pydantic import BaseModel, Field
from typing import Optional, Union

class MessageItem(BaseModel):
    cn_message: str=Field(
        "",
        title="Chinese Message",
        description="Error message in Chinese"
    )
    en_message: str = Field(
        "0",
        title="English Message",
        description="Error message in English"
    )
class Response(BaseModel):
    code: str=Field(
        "0",
        title="Response Code",
        description="if the code not 0, then it mean the error from server"
    )
    # message: MessageItem=None
    message: str=None
    data: Union[dict,None]=None


if __name__ == '__main__':
    exit(0)
