#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2023/10/5 01:10
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : config_util.py
# @Project : HSGTool

import configparser
import os

import yaml

from utils.loging_util import logger
dirname = os.path.dirname(__file__)
project_path = os.path.dirname(dirname)


def get_mysql_config(dbConfigName):
    conf = configparser.ConfigParser()
    dbConfig = project_path + os.sep + "config" +  os.sep + "database" + os.sep + "mysql" + os.sep + dbConfigName
    if os.path.exists(dbConfig):
        conf.read(dbConfig)
        host = conf.get("client", "host")
        user = conf.get("client", "user")
        password = conf.get("client", "password")
        port = conf.getint("client", "port")
        schema = conf.get("mysql", "database")
        return {"host":host,"port": port, "user":user, "password":password, "schema":schema}
    else:
        logger.debug('Config File not Find!!!')
        return {"host":"","port": "", "user":"", "password":"", "schema":""}

def get_oracle_config(dbConfigName):
    conf = configparser.ConfigParser()
    dbConfig = project_path + os.sep + "config" + os.sep + "oracle" + os.sep + dbConfigName
    print(dbConfig)
    if os.path.exists(dbConfig):
        conf.read(dbConfig)
        host = conf.get("client", "host")
        user = conf.get("client", "user")
        password = conf.get("client", "password")
        port = conf.getint("client", "port")
        schema = conf.get("oracle", "database")
        client_dir = conf.get("oracle", "client_dir")
        return host, port, user, password, schema, client_dir
    else:
        print('Config File not Find!!!')
        return "","","","","",""
def get_yaml_config(config_path):
    with open(config_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data
class PmsConfig():
    def __init__(self):
        config = configparser.ConfigParser()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        parent_dir = os.path.dirname(current_dir)
        config_dir = os.path.join(parent_dir, "services/pms/config/notification.cnf")
        print(config_dir)
        config.read(config_dir)

        # 执行的环境，会决定使用的PMS查询url和企业微信群机器人
        __project = config.get('COMMON', 'project')
        print(__project)
        # 获取pms登录信息
        self.pms_url = config.get('COMMON', 'pms_url')
        self.pms_key = config.get('COMMON', 'pms_key')
        self.pms_code = config.get('COMMON', 'pms_code')
        self.pms_user = config.get('COMMON', 'pms_user')
        self.pms_za = config.get('COMMON', 'pms_za')
        self.pms_zp = config.get('COMMON', 'pms_zp')
        # 0~6,周一到周日，决定哪一天需要发送消息
        self.working_day = list(map(str, config.get(__project, 'working_day').split(",")))
        self.pending_url = config.get(__project, 'pending_url')
        self.wecom_url = config.get(__project, 'wecom_url')
        self.pm = config.get(__project, 'pm')
        self.noti_day = int(config.get(__project, 'noti_day'))
        self.pending_bank_url = config.get(__project, 'pending_bank_url')
        print(self.pending_bank_url)
        self.mail_host = config.get(__project, 'mail_host')
        self.mail_user = config.get(__project, 'mail_user')
        self.mail_pass = config.get(__project, 'mail_pass')
        self.mail_receiver = config.get(__project, 'mail_receiver')

def get_db_config(dbConfigName):
    conf = configparser.ConfigParser()
    dbConfig = project_path + os.sep + "config" + os.sep + "mysql" + os.sep + dbConfigName
    if os.path.exists(dbConfig):
        conf.read(dbConfig)
        host = conf.get("client", "host")
        user = conf.get("client", "user")
        password = conf.get("client", "password")
        port = conf.getint("client", "port")
        schema = conf.get("mysql", "database")
        return host, port, user, password, schema
    else:
        print('Config File not Find!!!')
        exit(-1)


def get_parm_cpy_name(parmType, withSuffix):
    conf = configparser.ConfigParser()
    blob_config = project_path + os.sep + "services" + os.sep + "etl" + os.sep + "config" + os.sep+ "tableWithBlob.ini"
    print(blob_config)
    if os.path.exists(blob_config):
        conf.read((blob_config))
        cpyFile = conf.get("BptparmWithBlob", parmType.lower()).split(",")[0]
        if not withSuffix:
            cpyFile = cpyFile.split(".cpy")[0]
        return cpyFile
    return None

def get_other_cpy_name(tableName):
    conf = configparser.ConfigParser()
    blob_config = project_path + os.sep + "config" + os.sep + "tableWithBlob.ini"
    if os.path.exists(blob_config):
        conf.read((blob_config))
        cpyFile,blobName = conf.get("TableWithBlob", tableName.lower()).split(",")[0],conf.get("TableWithBlob", tableName.lower()).split(",")[1]
        return cpyFile.upper(),blobName.upper()
    return None

def get_code_and_val(parmType):
    conf = configparser.ConfigParser()
    blob_config = project_path + os.sep + "services" + os.sep + "etl" + os.sep + "config" + os.sep+ "tableWithBlob.ini"
    if os.path.exists(blob_config):
        conf.read((blob_config))
        cpyFile = conf.get("BptparmWithBlob", parmType.lower())
        print(cpyFile)
        tple = cpyFile.split(",")
    return tple[1],tple[2]

def load_parm_ini_file(parmType):
    cpyFileName = get_parm_cpy_name(parmType, False)
    ini_file = project_path + os.sep + "config" + os.sep + "parmMapping" + os.sep + cpyFileName + ".ini"
    iniFile = configparser.ConfigParser()
    iniFile.read(ini_file)
    return iniFile

def load_other_ini_file(tableName):
    ini_file = project_path + os.sep + "config" + os.sep + "otherMapping" + os.sep + tableName + ".ini"
    iniFile = configparser.ConfigParser()
    iniFile.read(ini_file)
    return iniFile

if __name__=="__main__":
    pass