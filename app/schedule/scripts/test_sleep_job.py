#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用长跑任务：睡 300 秒，用于验证超时/终止"""
import time

print("sleep job started")
time.sleep(300)
print("should not reach here when killed")
