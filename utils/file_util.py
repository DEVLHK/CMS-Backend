# -*- coding: utf-8 -*-
# @Function: 
# @Author: Jamie
# @Time : 2024/12/27 17:38
import os
import shutil
from pathlib import Path

import yaml

from utils.loging_util import logger


# def get_file_dir_path(key):
#     current_file = Path(__file__).resolve()  # 当前脚本路径
#     project_root = current_file.parent.parent  # utils/ -> 项目根  # ../app
#     dest_dir = project_root / "config" / "fastapi" / "config.yaml"
#     print(dest_dir)
#     with open(dest_dir, "r") as f:
#         config = yaml.safe_load(f)
#     return Path(config["fastapi-config"][key])

def get_file_dir_path(key):
    current_file = Path(__file__).resolve()  # 当前脚本路径
    project_root = current_file.parent.parent  # utils/ -> 项目根  # 获取项目根路径
    dest_dir = project_root / "config" / "fastapi" / "config.yaml"
    # print(dest_dir)
    with open(dest_dir, "r") as f:
        config = yaml.safe_load(f)
    path = project_root.parent / config["fastapi-config"][key]
    logger.info(f"上传文件目录路径path==>{path}")
    return path


def ensure_path_exists(*path_parts: str):
    # 拼接路径
    path = Path(*path_parts)

    # 检查路径是否存在，不存在则创建
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        # path.chmod(0o777)  # 针对linux
        logger.info(f"Path '{path}' has been created.")
    else:
        logger.info(f"Path '{path}' already exists.")


temp_file_parent_file = get_file_dir_path("tempFileDir")
upload_file_parent_dir = get_file_dir_path("uploadFileDir")


def delete_old_files(dest_dir, file_names):
    origin_file_names = [file.name for file in dest_dir.iterdir() if file.is_file()]
    save_file_name_list = file_names.split(",")
    missing_file_names = [name for name in origin_file_names if name not in save_file_name_list]
    # 删除文件
    file_path = ""
    try:
        if missing_file_names:
            return
        for missing_file_name in missing_file_names:
            file_path = dest_dir / missing_file_name
            file_path.unlink()
            logger.info(f"Old File '{missing_file_name}' has been deleted.")
    except FileNotFoundError:
        logger.debug(f"文件 {file_path} 未找到。")
    except PermissionError:
        logger.debug(f"权限错误：无法删除文件 {file_path}。")
    except Exception as e:
        logger.debug(f"删除文件时发生错误: {e}")


def save_file_by_id(resource_id, resource_index, index="", ids=None, file_names=""):
    dest_file_dir_path = upload_file_parent_dir / str(resource_id) / str(resource_index)
    dest_dir = dest_file_dir_path
    if index:
        dest_dir = dest_file_dir_path / str(index)  # index 对应表格里第一条记录，每条记录中可能会上传多个文件 针对保存配置文件
    ensure_path_exists(str(dest_dir))
    if ids and isinstance(ids, list):
        for id in ids:
            if id.isdigit():
                current_date = id[0:8]
                temp_file_dir = id[8:]
                temp_file_dir_path = os.path.join(temp_file_parent_file, current_date, temp_file_dir)
                # 将temp_file_dir_path文件夹下面的所有文件复制到dest_file_dir_path路径下
                for filename in os.listdir(temp_file_dir_path):
                    src_file = os.path.join(temp_file_dir_path, filename)
                    dest_file = os.path.join(str(dest_dir), filename)
                    # 如果是文件，将临时目录中的文件复制到目录目录下 如果同名就会被覆盖
                    if os.path.isfile(src_file):
                        shutil.copy(src_file, dest_file)
            # id不是纯数字 表示已经存过该文件了 不做任何处理

    # 曾经上传过的文件，后来在前端去掉，删除旧的垃圾文件
    delete_old_files(dest_dir, file_names)

    # 删除临时文件
    # delete_temp_files(ids)


def delete_directory(temp_file_dir_path):
    try:
        if temp_file_dir_path.exists() and temp_file_dir_path.is_dir():
            shutil.rmtree(temp_file_dir_path)  # 删除目录及其内容
            logger.info(f"目录 {temp_file_dir_path} 删除成功。")
        else:
            logger.warning(f"目录 {temp_file_dir_path} 不存在或不是目录。")
    except Exception as e:
        logger.debug(f"删除目录 {temp_file_dir_path} 时发生错误: {e}")


def delete_temp_files(ids):
    """删除临时文件的主函数"""
    if isinstance(ids, list):
        for id in ids:
            if id.isdigit():  # 确保 id 是数字字符串
                current_date = id[0:8]  # 取前8个字符作为日期
                temp_file_dir = id[8:]  # 剩余部分作为目录名

                # 使用 Path 来拼接路径，确保跨平台兼容性
                temp_file_dir_path = Path(temp_file_parent_file) / current_date / temp_file_dir

                # 调用删除函数
                delete_directory(temp_file_dir_path)


if __name__ == '__main__':
    get_file_dir_path("tempFileDir")
