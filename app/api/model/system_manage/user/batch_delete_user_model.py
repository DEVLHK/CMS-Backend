#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : batch_delete_user_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(title="UserBatchDeleteInput")

    ids: list = Field(
        ...,
        min_length=1,
        title="用户ID列表"
    )


if __name__ == '__main__':
    exit(0)
