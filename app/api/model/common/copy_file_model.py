# -*- coding: utf-8 -*-
# @Function: 
# @Author: Jamie
# @Time : 2025/1/8 20:30
from typing import List

from pydantic import BaseModel, Field
from app.api.model.common.upload_file_model import Resource


class Input(BaseModel):
    fileInfo: List[Resource] = Field(
        default_factory=lambda: [Resource()],
        title="",
        description="",
    )


class Output(BaseModel):
    fileInfo: List[Resource] = Field(
        default_factory=lambda: [Resource()],
        title="",
        description="",
    )
