#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/9/16 20:59
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : loging_util.py
# @Project : hbs_flink
import logging
import os
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("file-logger")
# 级别可用环境变量 LOG_LEVEL 覆盖（缺省 INFO）
log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
fh = TimedRotatingFileHandler(f"{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}//temp/log/consoles.log",when='D',interval=1,backupCount=7,encoding='utf-8')
fh.setLevel(log_level)
sh = logging.StreamHandler()
sh.setLevel(log_level)
formatter = logging.Formatter("[%(asctime)s][%(funcName)-28s][line:%(lineno)4d][%(levelname)-7s]: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.setLevel(log_level)

# apscheduler 自有 logger 接入同一文件（作业触发异常/错过触发否则无处可见）
_apscheduler_logger = logging.getLogger("apscheduler")
_apscheduler_logger.addHandler(fh)
_apscheduler_logger.setLevel(log_level)

def looger_exception(traceback):
    err_msg_list = str(traceback.format_exc()).split("\n")
    for msg in err_msg_list:
        logger.error(msg)
if __name__ == '__main__':
    exit(0)
