#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/20 23:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : script_logger.py
# @Project : Soybean-backend
"""定时任务脚本日志助手

仅输出到标准错误流（由任务引擎 subprocess 捕获进 app/schedule/temp/job_logs/{日期}/{run_log_id}.log），
不写公共 consoles.log，避免多进程混写与日志切割冲突。格式与工程日志一致。
级别优先级：get_script_logger(level 参数) > 环境变量 JOB_LOG_LEVEL（引擎按任务配置注入）> INFO

用法：
    from utils.script_logger import get_script_logger
    logger = get_script_logger("gen_failure_bug_data")
    logger.info("...")
"""
import logging
import os
import sys

_FORMATTER = logging.Formatter("[%(asctime)s][%(funcName)-28s][line:%(lineno)4d][%(levelname)-7s]: %(message)s")
_LEVEL_NAMES = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def _resolve_level(level):
    level_text = str(level or os.environ.get("JOB_LOG_LEVEL") or "INFO").upper()
    return getattr(logging, level_text, logging.INFO) if level_text in _LEVEL_NAMES else logging.INFO


def get_script_logger(name, level=None):
    """获取脚本专用 logger（同名重复调用返回同一实例，不会重复挂 handler）
    @param name: 脚本名，作为 logger 实例名（如 gen_failure_bug_data）
    @param level: 日志级别 DEBUG/INFO/WARNING/ERROR/CRITICAL，缺省读环境变量 JOB_LOG_LEVEL，再缺省 INFO
    """
    resolved = _resolve_level(level)
    script_logger = logging.getLogger(f"script.{name}")
    script_logger.setLevel(resolved)
    if not script_logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(_FORMATTER)
        handler.setLevel(resolved)
        script_logger.addHandler(handler)
    script_logger.propagate = False
    return script_logger


if __name__ == '__main__':
    exit(0)
