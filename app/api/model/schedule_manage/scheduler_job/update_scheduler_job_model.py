#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 11:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_scheduler_job_model.py
# @Project : Soybean-backend
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """修改定时任务（按 id 定位，业务字段仅传需要修改的；last_run_* 不可改）"""
    model_config = ConfigDict(title="SchedulerJobUpdateInput")

    id: int = Field(..., title="任务ID（定位条件）")
    jobName: Optional[str] = Field(None, title="定时任务名称（唯一）")
    scriptName: Optional[str] = Field(None, title="脚本文件名（唯一）")
    description: Optional[str] = Field(None, title="脚本描述")
    periodType: Optional[Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"]] = Field(
        None, title="周期类型")
    periodInterval: Optional[int] = Field(None, ge=1, title="周期间隔")
    firstRunDate: Optional[str] = Field(
        None, title="计划首次执行日期（None=不修改，空串=清除）", pattern=r"^(\d{4}-\d{2}-\d{2})?$")
    firstRunTime: Optional[str] = Field(
        None, title="计划首次执行时刻（None=不修改，空串=清除）", pattern=r"^(\d{2}:\d{2}:\d{2})?$")
    logLevel: Optional[str] = Field(
        None, title="脚本日志级别",
        description="DEBUG/INFO/WARNING/ERROR/CRITICAL，None=不修改；非法值运行时按 INFO 处理")
    params: Optional[dict[str, Any]] = Field(
        None, title="脚本入参（key=参数名，value=用户输入值字符串；None=不修改，传值=整体覆盖）",
        description="执行时按 --参数名 值 拼入命令行；mandatory=true 的参数必须提供非空值")


if __name__ == '__main__':
    exit(0)
