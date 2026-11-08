# -*- coding: utf-8 -*-
# @Function: 
# @Author: Jamie
# @Time : 2024/12/26 19:56
from pydantic import BaseModel, Field
from typing import List, Optional


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


class Output(BaseModel):
    fileList: List[Resource] = Field(
        default_factory=lambda: [Resource()],
        title="下拉框label类型对应的值",
        description="下拉框label类型对应的值"
    )


class UploadResponse(BaseModel):
    code: str = Field(
        "0",
        title="Response Code",
        description="if the code not 0, then it mean the error from server"
    )
    # message: MessageItem=None
    message: str = ""
    data: Optional[Output] = None


class ResourceForUploadImages(BaseModel):
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
    url: str = Field(
        default="",
        title="访问服务器上图片资源的路径",
        description="访问服务器上图片资源的路径"
    )


class OutputForUploadImages(BaseModel):
    fileList: List[ResourceForUploadImages] = Field(
        default_factory=lambda: [ResourceForUploadImages()],
        title="下拉框label类型对应的值",
        description="下拉框label类型对应的值"
    )


class UploadImagesResponse(BaseModel):
    code: int = Field(
        0,
        title="Response Code",
        description="if the code not 0, then it mean the error from server"
    )
    # message: MessageItem=None
    message: str = ""
    data: Optional[OutputForUploadImages] = None


if __name__ == '__main__':
    exit(0)
