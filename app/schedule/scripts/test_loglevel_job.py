#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用日志级别任务：DEBUG 和 INFO 各输出一行，验证级别注入"""
from utils.script_logger import get_script_logger

logger = get_script_logger("test_loglevel_job")
logger.debug("this is DEBUG line")
logger.info("this is INFO line")
