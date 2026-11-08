#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : batch_delete_role_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(title="RoleBatchDeleteInput")

    ids: list = Field(
        ...,
        min_length=1,
        title="角色ID列表"
    )


if __name__ == '__main__':
    exit(0)
