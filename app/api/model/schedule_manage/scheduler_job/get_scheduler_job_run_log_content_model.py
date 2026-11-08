#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/20 22:30
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_scheduler_job_run_log_content_model.py
# @Project : Soybean-backend
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """GET 查询参数：按行号窗口读取运行日志文件
    - id 必填；limit 每次行数（1-1000，默认200）
    - 首次请求：不传 before/after -> 返回文件最后 limit 行
    - 向上滚动：before=上一段 startLine-1 -> 返回该行之前的 limit 行
    - 向下滚动/跟随更新：after=上一段 endLine -> 返回该行之后的 limit 行（文件在增长时可轮询）"""
    model_config = ConfigDict(title="SchedulerJobRunLogContentQuery")

    id: int = Field(..., title="运行记录ID")
    limit: int = Field(200, title="每次返回行数", description="1-1000，默认200")
    before: Optional[int] = Field(None, title="返回该行号之前的 limit 行（向上翻页）")
    after: Optional[int] = Field(None, title="返回该行号之后的 limit 行（向下翻页/跟随更新）")


class Output(BaseModel):
    model_config = ConfigDict(title="SchedulerJobRunLogContent")

    id: int = Field(..., title="运行记录ID")
    fileExists: bool = Field(..., title="日志文件是否存在", description="不存在时前端回退展示列表接口的 output 字段")
    running: bool = Field(False, title="任务是否仍在运行", description="运行中可轮询 after 端跟随更新")
    totalLines: int = Field(0, title="文件当前总行数")
    startLine: int = Field(0, title="本段起始行号（1-based，0=无内容）")
    endLine: int = Field(0, title="本段结束行号")
    lines: list = Field([], title="日志行列表（不含换行符）")
    hasMoreBefore: bool = Field(False, title="是否还有更早的行（startLine>1）")
    hasMoreAfter: bool = Field(False, title="是否还有更晚的行（endLine<totalLines）")


if __name__ == '__main__':
    exit(0)
