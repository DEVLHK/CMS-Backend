#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/11/24 10:53
# @Author  : KenLin
# @Email   : kenlin@hisunglobal.com
# @File    : http_util
from app.api.model.common.response_model import Response
from utils.loging_util import logger


def response_error(msg_code):
    """错误响应：-1 为系统异常；其余 code 原样返回（旧 message_code_info 查询已随 oms 模块移除）"""
    logger.debug(f"message_code:{msg_code}")
    message = "系统出错,请联系系统管理员！" if msg_code == -1 else str(msg_code)
    return Response(code=str(msg_code), message=message, data={})


def response_success(data=None):
    data = {} if data is None else data.model_dump()
    logger.debug(data)
    return Response(code="0", message="", data=data)


if __name__ == '__main__':
    exit(0)
