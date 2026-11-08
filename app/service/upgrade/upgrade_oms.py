#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/6/21 02:28
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : upgrade_oms.py
# @Project : CMS-Backend
import shutil
import stat
import traceback
import zipfile
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import Request
from app.api.model.upgrade.oms import upgrade_oms_model
from utils import http_util, path_util
from utils.loging_util import logger
def upgrade_oms(data: upgrade_oms_model.Input, request: Request):
    try:
        for fileInfo in data.fileList:
            package_parent_path=path_util.get_project_parent_root_path().joinpath("tempFile")
            file_temp_path=package_parent_path.joinpath(str(fileInfo.id)[:8]).joinpath(str(fileInfo.id)[8:]).joinpath(fileInfo.fileName)
            logger.debug(file_temp_path)
            if os.path.exists(file_temp_path):
                extract_to = "/Users/ken.lin/WorkSpace/Git/HiSunGitLab/oms"
                extract_zip(file_temp_path, extract_to)
        return http_util.response_success()
    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list:
            logger.error(msg)
        return http_util.response_error()


def extract_zip(zip_path, extract_to) :
    # if os.path.exists(extract_to) :
    #     shutil.rmtree(extract_to)
    logger.debug(zip_path)
    logger.debug(extract_to)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref :
            for file_info in zip_ref.infolist() :
                # 跳过 .git 相关文件
                if '.git' in file_info.filename :
                    continue
                target_path = os.path.join(extract_to, file_info.filename)

                if file_info.is_dir() :
                    os.makedirs(target_path, exist_ok=True)
                    continue

                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                with zip_ref.open(file_info) as source :
                    with open(target_path, 'wb') as target :
                        target.write(source.read())

                # 设置为可写
                os.chmod(target_path, 0o644)
        macosx_path = os.path.join(extract_to, '__MACOSX')
        if os.path.exists(macosx_path) :
            shutil.rmtree(macosx_path)

        # 删除所有 .DS_Store 文件
        for root, dirs, files in os.walk(extract_to) :
            for file in files :
                if file == '.DS_Store' :
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list :
            logger.error(msg)
    return True


if __name__ == '__main__':
    zip_path="/Users/ken.lin/WorkSpace/Git/HiSunGitLab/oms/hbs-oms-backend/tempFile/20260621/110349718177/hbs-oms-backend.zip"
    extract_to="/Users/ken.lin/WorkSpace/Git/HiSunGitLab/oms//tempFile"
    # await async_extract_zip(zip_path,extract_to)
