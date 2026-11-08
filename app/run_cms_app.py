#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/7/25 15:05
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : run_cms_app.py
# @Project : CMS-Backend
import sys
import os
from apscheduler.triggers.interval import IntervalTrigger
from starlette.middleware.cors import CORSMiddleware
path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.abspath(os.path.dirname(path))
sys.path.append(project_path)
# print(project_path)
# 提前加载文件路径
from utils import file_util
# print(file_util.temp_file_parent_file)
# print(file_util.upload_file_parent_dir)
from typing import Union
import uvicorn
from fastapi import FastAPI, Request, Query, Header, Body, HTTPException, UploadFile, File, Form, Depends
import json
import yaml
from pydantic import BaseModel, Field
from typing import List

from app.api.model.common.response_model import MessageItem
from app.api.model.common.response_model import Response
from utils.loging_util import logger
from app.service.common.main import upload_file as upload
from app.service.common.main import upload_images as upload_images
from app.service.common.main import download_file as download
from app.api.model.common.upload_file_model import UploadResponse
from app.api.model.common.upload_file_model import UploadImagesResponse
from app.api.model.common.download_file_model import Input
import traceback
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.schedule.job_engine import register_all_jobs


# 读取yml文件
with open(f"{project_path}/config/router/router.yaml", "r") as file:
    router_data = yaml.safe_load(file)
scheduler = AsyncIOScheduler()
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动调度器....")
    scheduler.start()
    register_all_jobs(scheduler)
    # scheduler.add_job(
    #     pms_report_job.scheduled_task,
    #     trigger=IntervalTrigger(seconds=5),
    #     id="interval_task",
    #     replace_existing=True
    # )
    yield
    # 关闭时
    logger.info("关闭调度器...")
    scheduler.shutdown()

cms_app = FastAPI(lifespan=lifespan)
cms_app.state.scheduler=scheduler
cms_app.state.project_path=project_path
# 启用 CORS
cms_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.200.172:4000"],  # 允许所有域名，生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


@cms_app.post("/common/uploadImages", response_model=UploadImagesResponse)
async def upload_file(files: List[UploadFile] = File(...)):
    try:
        return upload_images(files)
    except Exception as e:
        logger.error(traceback.format_exc())


@cms_app.post("/common/upload", response_model=UploadResponse)
async def upload_file(files: List[UploadFile] = File(...)):
    try:
        return upload(files)
    except Exception as e:
        logger.error(traceback.format_exc())


@cms_app.post("/common/download")
async def download_file(data: Input = Body(...)):
    try:
        return download(data.fileList)
    except Exception as e:
        logger.error(traceback.format_exc())


def _annotation_kind(annotation):
    """剥掉 Optional/泛型外壳后返回字段类别：list/dict/int/float/bool/str"""
    import typing
    origin = typing.get_origin(annotation)
    if origin is typing.Union:
        non_none = [arg for arg in typing.get_args(annotation) if arg is not type(None)]
        if len(non_none) == 1:
            return _annotation_kind(non_none[0])
    if annotation is list or origin is list:
        return "list"
    if annotation is dict or origin is dict:
        return "dict"
    if annotation is int:
        return "int"
    if annotation is float:
        return "float"
    if annotation is bool:
        return "bool"
    return "str"


def _build_model_from_form(model_cls, values, upload_field=None):
    """表单参数 -> Input 模型实例（upload 配置驱动）。

    values: {字段名: 值}；字符串按模型注解转换（list/dict 走 JSON 解析、int/float/bool 显式转换），
    已由 FastAPI Form 声明解析出的原生类型直接透传；None 跳过让模型默认值生效，最后经 pydantic 校验。
    """
    data = {}
    for name, field in model_cls.model_fields.items():
        raw = values.get(name)
        if raw is None:
            continue
        if isinstance(raw, str):
            kind = _annotation_kind(field.annotation)
            if kind in ("list", "dict"):
                data[name] = json.loads(raw)
            elif kind == "int":
                data[name] = int(raw)
            elif kind == "float":
                data[name] = float(raw)
            elif kind == "bool":
                data[name] = raw.lower() in ("true", "1")
            else:
                data[name] = raw
        else:
            data[name] = raw
    return model_cls(**data)


for service in router_data.keys():
    for target in router_data[service].keys():
        method = str(router_data[service][target]["method"]).lower()
        function = router_data[service][target]["function"]
        function_package = str(function).rsplit(".", 1)[0]
        path = f"/{service}/{target}"
        in_model = router_data[service][target].get("input-model")
        out_model = router_data[service][target].get("output-model")
        # 可选配置：response-model（默认通用 Response）、tags、operation-id
        response_model = router_data[service][target].get("response-model", "Response")
        if response_model != "Response":
            exec(f"import {str(response_model).rsplit('.', 1)[0]}")
        tags = router_data[service][target].get("tags")
        operation_id = router_data[service][target].get("operation-id")
        exec(f"import {function_package}")
        if in_model:
            exec(f"import {str(in_model).rsplit('.', 1)[0]}")
        if out_model:
            exec(f"import {str(out_model).rsplit('.', 1)[0]}")
            response_type = eval(out_model)

        decorator_str = f"""@cms_app.{method}("{path}", response_model={response_model}"""
        if tags:
            decorator_str += f", tags={tags!r}"
        if operation_id:
            decorator_str += f', operation_id="{operation_id}"'
        decorator_str += ")"

        # GET 请求无请求体：不声明 data body 参数；配置了 input-model 时作为查询参数（Depends 注入），
        # 服务函数统一按 (data, request) 调用（无查询参数的 GET 传入 data=None）
        if method == "get":
            if in_model:
                params_str = "request: Request,data: eval(in_model) = Depends()"
                data_log_str = 'logger.info("request data:"+str(data.model_dump()))'
                call_str = "data"
            else:
                params_str = "request: Request"
                data_log_str = 'logger.info("request data: None")'
                call_str = "None"
        else:
            # 可选配置：upload（文件参数名）——multipart 文件上传端点：
            # 文件以 UploadFile 接收，其余表单字段按 input-model 注解组装后调用 service(data, request, *files)
            # 可选配置：upload-required（默认 true）——false 时文件选传（File(None)），适合"可重新上传覆盖"类端点
            # upload 支持单个参数名或列表（如 upload: [file, filePdf]，多文件按列表顺序位置传给 service）
            upload_fields = router_data[service][target].get("upload")
            upload_required = router_data[service][target].get("upload-required", True)
            if upload_fields and in_model:
                upload_fields = upload_fields if isinstance(upload_fields, list) else [upload_fields]
                # 按模型字段生成 Form 参数声明（进 OpenAPI 文档 + FastAPI 类型校验），
                # list/dict 以 JSON 字符串接收，int/float/bool 由 FastAPI 原生解析
                model_cls = eval(in_model)
                form_params = []
                for name, field in model_cls.model_fields.items():
                    kind = _annotation_kind(field.annotation)
                    py_type = {"int": "int", "float": "float", "bool": "bool"}.get(kind, "str")
                    default = "..." if field.is_required() else "None"
                    form_params.append(f"{name}: {py_type} = Form({default})")
                file_default = "..." if upload_required else "None"
                params_parts = ["request: Request"] + form_params + \
                               [f"{name}: UploadFile = File({file_default})" for name in upload_fields]
                params_str = ",".join(params_parts)
                value_dict = "{" + ",".join(f'"{name}": {name}' for name in model_cls.model_fields) + "}"
                files_call = ",".join(upload_fields)
                upload_function_str = f"""{decorator_str}
async def {str(function).split(".")[-1]}({params_str}):
            try:
               response = Response
               logger.info("Request URL:"+str(request.url))
               logger.info("Request URL:"+str(request.headers))
               try:
                   data = _build_model_from_form(eval("{in_model}"), {value_dict}, "{upload_fields[0]}")
               except Exception:
                   logger.error(traceback.format_exc())
                   return eval("{response_model}")(code="-1", msg="参数错误: 表单字段不匹配模型要求", data=None)
               logger.info("request data:"+str(data.model_dump()))
               response = eval("{function}")(data,request,{files_call})
               return response
            except Exception as e:
               logger.error(traceback.format_exc())
            """
                exec(upload_function_str)
                continue
            params_str = "data: eval(in_model),request: Request"
            data_log_str = 'logger.info("request data:"+str(data.model_dump()))'
            call_str = "data"

        function_str = f"""{decorator_str}
async def {str(function).split(".")[-1]}({params_str}):
            try:
               response = Response
               logger.info("Request URL:"+str(request.url))
               logger.info("Request URL:"+str(request.headers))
               {data_log_str}
               response = eval("{function}")({call_str},request)
               return response
            except Exception as e:
               logger.error(traceback.format_exc())
            """
        exec(function_str)

if __name__ == '__main__':
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    with open(f"{path}/config/fastapi/config.yaml") as file:
        config_data = yaml.safe_load(file)
    host = config_data['fastapi-config']['host']
    port = int(config_data['fastapi-config']['port'])
    uvicorn.run("run_cms_app:cms_app", host=host, port=port, reload=True)
