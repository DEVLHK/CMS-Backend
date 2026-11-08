#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/6/21 11:23
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : path_util.py
# @Project : CMS-Backend
import shutil
from pathlib import Path
def get_project_root_path():
    current_file = Path(__file__).resolve()  # 当前脚本路径
    project_root = current_file.parent.parent  # 获取项目根路径
    return project_root

def get_project_parent_root_path():
    current_file = Path(__file__).resolve()  # 当前脚本路径
    project_parent_root = current_file.parent.parent.parent  # 获取项目根路径
    return project_parent_root

if __name__ == '__main__' :
    print(get_project_parent_root_path().joinpath("tempFile"))
