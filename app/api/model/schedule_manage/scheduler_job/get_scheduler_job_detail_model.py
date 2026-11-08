#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_scheduler_job_detail_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """查询任务详情（按 id 定位）"""
    model_config = ConfigDict(title="SchedulerJobDetailQuery")

    id: int = Field(..., title="任务ID")


if __name__ == '__main__':
    exit(0)
