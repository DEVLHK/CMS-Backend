#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/20 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_scheduler_job_run_log_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    """GET 查询参数（均可空）"""
    model_config = ConfigDict(title="SchedulerJobRunLogQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")
    jobId: Optional[int] = Field(None, title="任务ID（精确）")
    status: Optional[str] = Field(
        None,
        title="运行状态 0:运行中 1:成功 2:失败 3:超时（精确）"
    )


class SchedulerJobRunLogRecord(BaseModel):
    model_config = ConfigDict(title="SchedulerJobRunLogRecord")

    id: int = Field(..., title="运行记录ID")
    jobId: int = Field(..., title="任务ID")
    scriptName: str = Field(..., title="脚本路径")
    triggerType: str = Field(..., title="触发方式 scheduled:定时 manual:手动")
    status: str = Field("0", title="运行状态 0:运行中 1:成功 2:失败 3:超时，字符串类型")
    startTime: Optional[str] = Field(None, title="开始时间")
    endTime: Optional[str] = Field(None, title="结束时间")
    pid: Optional[int] = Field(None, title="进程ID")
    output: Optional[str] = Field(None, title="脚本输出（尾部截断）")


class Output(PageRecord):
    model_config = ConfigDict(title="SchedulerJobRunLogPageOutput")

    records: list[SchedulerJobRunLogRecord] = Field([], title="运行日志列表")


if __name__ == '__main__':
    exit(0)
