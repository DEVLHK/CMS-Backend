#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 11:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_scheduler_job_list_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.api.model.system_manage.page_model import PageRecord


class Input(BaseModel):
    """GET 查询参数（均可空）"""
    model_config = ConfigDict(title="SchedulerJobListQuery")

    current: int = Field(1, title="页码")
    pageSize: int = Field(10, title="每页条数")
    jobName: Optional[str] = Field(None, title="定时任务名称（模糊匹配）")
    scriptName: Optional[str] = Field(None, title="脚本文件名（模糊匹配）")


class SchedulerJobRecord(BaseModel):
    """定时任务记录（last_run_* 为调度器回写字段，接口层只读）"""
    model_config = ConfigDict(title="SchedulerJobRecord")

    id: int = Field(..., title="序号（自增主键）")
    jobName: str = Field(..., title="定时任务名称")
    scriptName: str = Field(..., title="脚本文件名")
    description: str = Field("", title="脚本描述")
    periodType: str = Field(..., title="周期类型 second/minute/hour/day/week/month/quarter/year")
    periodInterval: int = Field(1, title="周期间隔")
    firstRunDate: Optional[str] = Field(None, title="计划首次执行日期（YYYY-MM-DD）")
    firstRunTime: Optional[str] = Field(None, title="计划首次执行时刻（HH:mm:ss）")
    lastRunTime: Optional[str] = Field(None, title="最近执行时间")
    lastRunDate: Optional[str] = Field(None, title="最近执行日期")
    lastRunStatus: str = Field("0", title="最近执行状态 0:未执行 1:成功 2:失败，字符串类型")
    params: dict = Field({}, title="脚本入参（key=参数名，value=用户输入值）")
    createTime: Optional[str] = Field(None, title="创建时间")
    createBy: str = Field("", title="创建人（登录账号）")
    updateTime: Optional[str] = Field(None, title="更新时间")
    updateBy: str = Field("", title="更新人（登录账号）")
    ts: Optional[str] = Field(None, title="时间戳（数据库自动维护）")


class Output(PageRecord):
    model_config = ConfigDict(title="SchedulerJobPageOutput")

    records: list[SchedulerJobRecord] = Field([], title="定时任务记录列表")


if __name__ == '__main__':
    exit(0)
