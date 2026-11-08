#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2026/3/23 02:19
# @Author  : KenLin
# @Email   : kenlin@hisunglobal.com
# @File    : start_up
# 主程序
import subprocess
import sys
import time
import requests

# 启动 FastAPI 后台服务
process = subprocess.Popen(
    [sys.executable, "run_cms_app.py"],
    stdout=None,
    stderr=None,
    text=True
)

# 等待服务启动
time.sleep(10)

if __name__ == '__main__':
    exit(0)
