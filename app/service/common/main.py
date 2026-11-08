# -*- coding: utf-8 -*-
# @Function: 公共服务
# @Author: Jamie
# @Time : 2024/12/18 15:25
import io
import os
import random
import shutil
import time
import traceback
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import quote

from fastapi import Request, UploadFile, File
from fastapi.responses import StreamingResponse
from app.api.model.common import get_selection_value_model, upload_file_model, copy_file_model
from app.api.model.common.upload_file_model import Resource
from utils import file_util
from dao.selection_info import SelectionInfoDao
from utils import http_util
from utils.loging_util import logger


def upload_images(files: List[UploadFile] = File(...)):
    def create_dest_file_dir(temp_file_day_dir: Path) -> tuple[Path, str]:
        """
        创建文件存储的目标目录
        :param temp_file_day_dir: 日期目录
        :return: 目标目录路径和时间戳+随机数
        """
        time_stamp = time.strftime("%H%M%S", time.localtime(time.time()))  # 时间戳
        six_random_number = str(random.randint(100000, 999999))  # 6位随机数
        temp_file_dir = time_stamp + six_random_number
        dest_file_dir_path = temp_file_day_dir / temp_file_dir
        file_util.ensure_path_exists(str(dest_file_dir_path))
        return dest_file_dir_path, temp_file_dir

    try:
        response_data = upload_file_model.UploadImagesResponse()
        response_list = []
        current_date = datetime.now().strftime('%Y%m%d')
        temp_file_parent_dir = file_util.temp_file_parent_file  # 父目录
        temp_file_day_dir = temp_file_parent_dir / current_date
        file_util.ensure_path_exists(str(temp_file_day_dir))  # 在父目录下面创建每天对应日期的目录
        if not files:
            logger.warning(f"files:[]文件为空")
        else:
            for file in files:
                # 创建唯一的文件目录
                dest_file_dir_path, temp_file_dir = create_dest_file_dir(temp_file_day_dir)
                # 保存文件到目标路径
                dest_file_path = os.path.join(str(dest_file_dir_path), file.filename)
                with open(dest_file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                url = f"http://192.168.200.172:5000/uploads/{current_date}/{temp_file_dir}/{file.filename}"
                id = current_date + temp_file_dir
                resource = upload_file_model.ResourceForUploadImages(
                    fileName=file.filename,
                    id=id,
                    url=url,
                )
                response_list.append(resource)
        output = upload_file_model.OutputForUploadImages(fileList=response_list)
        response_data.data = output
        return response_data.model_dump()
    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list:
            logger.error(msg)
        return http_util.response_error(-1)


def upload_file(files: List[UploadFile] = File(...)):
    def create_dest_file_dir(temp_file_day_dir: Path) -> tuple[Path, str]:
        """
        创建文件存储的目标目录
        :param temp_file_day_dir: 日期目录
        :return: 目标目录路径和时间戳+随机数
        """
        time_stamp = time.strftime("%H%M%S", time.localtime(time.time()))  # 时间戳
        six_random_number = str(random.randint(100000, 999999))  # 6位随机数
        temp_file_dir = time_stamp + six_random_number
        dest_file_dir_path = temp_file_day_dir / temp_file_dir
        file_util.ensure_path_exists(str(dest_file_dir_path))
        return dest_file_dir_path, temp_file_dir

    try:
        response_data = upload_file_model.UploadResponse()
        response_list = []
        current_date = datetime.now().strftime('%Y%m%d')
        temp_file_parent_dir = file_util.temp_file_parent_file  # 父目录
        temp_file_day_dir = temp_file_parent_dir / current_date
        file_util.ensure_path_exists(str(temp_file_day_dir))  # 在父目录下面创建每天对应日期的目录
        if not files:
            logger.warning(f"files:[]文件为空")
        else:
            for file in files:
                # 创建唯一的文件目录
                dest_file_dir_path, temp_file_dir = create_dest_file_dir(temp_file_day_dir)
                # 保存文件到目标路径
                dest_file_path = os.path.join(str(dest_file_dir_path), file.filename)
                with open(dest_file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                resource = upload_file_model.Resource(
                    fileName=file.filename,
                    id=current_date + temp_file_dir
                )
                response_list.append(resource)
        output = upload_file_model.Output(fileList=response_list)
        response_data.data = output
        logger.debug(response_data.model_dump())
        return http_util.response_success(response_data.data)
    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list:
            logger.error(msg)
        return http_util.response_error(-1)


def download_file(data: List[Resource]):
    # 获取文件的函数
    def get_file_path_by_id_and_name(file_id: str, file_name: str):
        # 这里假设你根据 file_id 和 file_name 找到实际的文件路径
        # 你需要根据实际的文件存储逻辑进行更改
        if file_id.isdigit():
            current_date = file_id[0:8]
            temp_file_dir = file_id[8:]
            temp_file_path = file_util.temp_file_parent_file / current_date / temp_file_dir / file_name
            if not temp_file_path.exists():
                logger.warning(f"要下载的文件{temp_file_path}，无法在系统上面找到")
                return None
            logger.info(f"download_file--->temp_file_path:{temp_file_path}")
            return temp_file_path
        else:
            upload_file_path = file_util.upload_file_parent_dir / Path(file_id) / file_name
            if not upload_file_path.exists():
                logger.warning(f"要下载的文件{upload_file_path}，无法在系统上面找到")
                return None
            logger.info(f"download_file--->upload_file_path:{upload_file_path}")
            return upload_file_path

    # 文件压缩的函数
    def create_zip_file(file_paths: List[str]) -> io.BytesIO:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in file_paths:
                if os.path.exists(file_path):  # 确保文件存在
                    file_name = os.path.basename(file_path)
                    with open(file_path, 'rb') as f:
                        zip_file.writestr(file_name, f.read())
                else:
                    logger.warning(f"文件 {file_path} 不存在，跳过压缩")
        zip_buffer.seek(0)
        return zip_buffer

    try:
        if not data:
            logger.error("要下载文件的入参为空")
            return http_util.response_success()
        # 收集文件路径
        file_paths = []
        for file in data:
            file_path = get_file_path_by_id_and_name(file.id, file.fileName)
            if file_path:
                file_paths.append(file_path)

        # 如果 fileList 中只有一个文件，直接返回该文件
        if len(file_paths) == 1:
            with open(file_paths[0], 'rb') as f:
                file_content = f.read()
                if not file_content:
                    logger.warning(f"文件 {file_paths[0]} 的内容为空")
                    # 这里可以返回一个默认响应，提示文件内容为空
                    return {"code": 0, "message": "文件内容为空", "data": {}}
                # 处理中文文件名
                filename = os.path.basename(file_paths[0])
                encoded_filename = quote(filename)  # 对文件名进行 URL 编码
                return StreamingResponse(io.BytesIO(file_content), media_type="application/octet-stream", headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
                })

        # 如果 fileList 中有多个文件，打包成一个 zip 文件
        elif len(file_paths) > 1:
            # 创建一个基于当前时间的文件名
            zip_filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".zip"
            zip_buffer = create_zip_file(file_paths)
            return StreamingResponse(zip_buffer, media_type="application/zip",
                                     headers={"Content-Disposition": f"attachment; filename*=UTF-8''{zip_filename}"})

        # 如果没有文件找到，返回 404 错误
        else:
            return {"code": 0, "message": "", "data": {}}
    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list:
            logger.error(msg)
        return http_util.response_error(-1)


def get_selection_value(data: get_selection_value_model.Input, request: Request):
    def get_children_selection(sub_type, project_id):
        result = []
        if sub_type:
            list = [sub_type]
            selection_info_res = selection_info.selection_query(list, project_id)
            for index, row in selection_info_res["data"].iterrows():
                inner_in_dict = {}
                inner_in_dict["value"] = row.to_dict()["code"]
                inner_in_dict["cnLabel"] = row.to_dict()["cn_description"]
                inner_in_dict["enLabel"] = row.to_dict()["en_description"]
                # 递归获取子selection
                inner_in_dict["children"] = get_children_selection(row.to_dict()["sub_type"], project_id)
                result.append(inner_in_dict)
        return result

    try:
        project_id = request.headers.get("Current-Project")
        print(f"请求project_id=====>{project_id}")
        # project_id = "orb"
        selection_info = SelectionInfoDao()
        selection_info_res = selection_info.selection_query(data.types, project_id)
        response_data = get_selection_value_model.Output()
        print(response_data.selectionValues)
        selection_df = selection_info_res["data"]
        if selection_df is not None and not selection_df.empty:  # 确保selection_df先判断
            for type in data.types:
                selection_type_children = selection_df.loc[selection_df["type"] == type]
                # print(selection_type_children)
                response_data.selectionValues[type] = []
                print(response_data.selectionValues)
                for index, row in selection_type_children.iterrows():
                    print(f"{row.to_dict()}")
                    inner_dict = {}
                    inner_dict["value"] = row.to_dict()["code"]
                    inner_dict["cnLabel"] = row.to_dict()["cn_description"]
                    inner_dict["enLabel"] = row.to_dict()["en_description"]
                    inner_dict["children"] = get_children_selection(row.to_dict()["sub_type"], project_id)
                    response_data.selectionValues[type].append(inner_dict)
                    # print(response_data.selectionValues)
            # print(response_data.selectionValues)
        else:
            return http_util.response_error(-1)
        return http_util.response_success(response_data)

    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list:
            logger.error(msg)
        return http_util.response_error(-1)


def copy_file(data: copy_file_model.Input, request: Request):
    def get_temp_file_part_dir_path():
        time_stamp = time.strftime("%H%M%S", time.localtime(time.time()))  # 时间戳
        six_random_number = str(random.randint(100000, 999999))  # 6位随机数
        temp_file_dir = time_stamp + six_random_number
        return temp_file_dir

    try:
        file_infos = data.fileInfo
        response_data = copy_file_model.Output()
        response_data.fileInfo = []
        for file_info in file_infos:
            id = file_info.id
            file_name = file_info.fileName
            resource = copy_file_model.Resource()
            if id.isdigit():  # id是纯数字
                current_date = id[0:8]
                temp_file_dir_part_name = id[8:]
                temp_file_path = file_util.temp_file_parent_file / current_date / temp_file_dir_part_name / file_name
                if not temp_file_path.exists():
                    logger.error(f"{temp_file_path}复制temp文件失败，文件不存在")
                    return http_util.response_success()
                # 文件存在
                new_temp_file_dir_part_name = get_temp_file_part_dir_path()
                current_date = datetime.now().strftime('%Y%m%d')
                new_temp_dir = file_util.temp_file_parent_file / current_date / new_temp_file_dir_part_name
                # 创建新目录
                file_util.ensure_path_exists(str(new_temp_dir))
                # 将文件复制到新目录下面
                new_temp_file_path = new_temp_dir / file_name
                shutil.copy(temp_file_path, new_temp_file_path)
                resource.fileName = file_name
                resource.id = current_date + new_temp_file_dir_part_name
            else:
                upload_file_path = file_util.upload_file_parent_dir / id / file_name
                if not upload_file_path.exists():
                    logger.error(f"{upload_file_path}复制upload文件失败，文件不存在")
                    return http_util.response_success()
                # 文件存在
                # parts = list(Path(id).parts)
                # current_time = datetime.now()
                # random_number = random.randint(10, 99)
                # resource_id = "RES-" + current_time.strftime("%Y%m%d%H%M%S") + "-" + str(random_number)
                # parts[0] = resource_id
                # new_upload_file_dir_path = file_util.upload_file_parent_dir / Path(*parts)
                # file_util.ensure_path_exists(new_upload_file_dir_path)
                # new_upload_file_path = new_upload_file_dir_path / file_name
                # shutil.copy(upload_file_path, new_upload_file_path)
                # resource.fileName = file_name
                # resource.id = str(Path(*parts))
                # 文件存在
                new_temp_file_dir_part_name = get_temp_file_part_dir_path()
                current_date = datetime.now().strftime('%Y%m%d')
                new_temp_dir = file_util.temp_file_parent_file / current_date / new_temp_file_dir_part_name
                # 创建新目录
                file_util.ensure_path_exists(str(new_temp_dir))
                # 将文件复制到新目录下面
                new_temp_file_path = new_temp_dir / file_name
                shutil.copy(upload_file_path, new_temp_file_path)
                resource.fileName = file_name
                resource.id = current_date + new_temp_file_dir_part_name
            response_data.fileInfo.append(resource)
        return http_util.response_success(response_data)
    except Exception as e:
        err_msg_list = str(traceback.format_exc()).split("\n")
        for msg in err_msg_list:
            logger.error(msg)
        return http_util.response_error(-1)


if __name__ == '__main__':
    exit(0)
