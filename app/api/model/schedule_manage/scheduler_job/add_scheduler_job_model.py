#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 11:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_scheduler_job_model.py
# @Project : Soybean-backend
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

DATE_PATTERN = r"^(\d{4}-\d{2}-\d{2})?$"
TIME_PATTERN = r"^(\d{2}:\d{2}:\d{2})?$"


class Input(BaseModel):
    """新增定时任务（create_by 取当前登录账号，last_run_* 由调度器回写）"""
    model_config = ConfigDict(title="SchedulerJobAddInput")

    jobName: str = Field(..., title="定时任务名称（唯一）")
    scriptName: str = Field(..., title="脚本文件名（唯一，建议仓库相对路径）")
    description: str = Field("", title="脚本描述")
    periodType: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(
        ..., title="周期类型")
    periodInterval: int = Field(1, ge=1, title="周期间隔")
    firstRunDate: Optional[str] = Field(
        None, title="计划首次执行日期（YYYY-MM-DD，可空=注册后立即按周期执行）", pattern=DATE_PATTERN)
    firstRunTime: Optional[str] = Field(
        None, title="计划首次执行时刻（HH:mm:ss，可空）", pattern=TIME_PATTERN)
    logLevel: str = Field(
        "INFO", title="脚本日志级别",
        description="DEBUG/INFO/WARNING/ERROR/CRITICAL，经环境变量 JOB_LOG_LEVEL 注入脚本")
    params: Optional[dict[str, Any]] = Field(
        None, title="脚本入参（key=参数名，value=用户输入值字符串；缺省 {}）",
        description="执行时按 --参数名 值 拼入命令行；mandatory=true 的参数必须提供非空值")


if __name__ == '__main__':
    exit(0)
