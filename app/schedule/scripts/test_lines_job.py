#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用多行输出任务：输出 300 行编号日志后退出"""
for i in range(1, 301):
    print(f"log line {i:03d} - some runtime detail for paging test")
