#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 11:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : delete_scheduler_job_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    """删除定时任务（按 id 定位）"""
    model_config = ConfigDict(title="SchedulerJobDeleteInput")

    id: int = Field(..., title="任务ID")


if __name__ == '__main__':
    exit(0)
