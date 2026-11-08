#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2023/10/5 00:57
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : cms_service_util.py
# @Project : HSGTool

import configparser
import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine

from utils import mysql_util
# from utils import oracle_util
from utils import config_util
import utils.config_util

dirname = os.path.dirname(__file__)
project_path = os.path.dirname(dirname)
from utils.loging_util import logger
from utils.loging_util import looger_exception

import traceback

def connect_cms_db():
    try:
        conf = configparser.ConfigParser()
        dbConfig = project_path + os.sep + "config" + os.sep + 'database' + os.sep +"cms_service.cnf"
        logger.debug(dbConfig)
        if os.path.exists(dbConfig):
            conf.read(dbConfig)
            logger.debug("teset4")
            confName = conf.get("database", "db_config")
            database_info=config_util.get_mysql_config(confName)
            db_type = conf.get("database", "db_type")
            #不使用mysql.init_connect(confName=confName),为了后续可能使用oracle预留
            if db_type=="mysql":
                mysql=mysql_util.MySQL()
                conf = {}
                conf['host'] = database_info['host']
                conf['port'] = database_info['port']
                conf['user'] = database_info['user']
                conf['password'] = database_info['password']
                conf['schema'] = database_info['schema']
                mysql.init_connect(conf)
                service_conn=mysql.db
                encoded_password = quote_plus(database_info['password'])
                engine = create_engine(f"mysql+pymysql://{database_info['user']}:{encoded_password}@{ database_info['host']}:{database_info['port']}/{database_info['schema']}")
            else:
                service_conn=None
                engine=None
            return [service_conn,engine]
        else:
            return None
    except Exception as e:
        looger_exception(traceback)
        return None

def connect_mysql_db(confName):
    try:
        mysql = mysql_util.MySQL()
        mysql.init_connect(confName=confName)
        return mysql.db
    except Exception as e:
        looger_exception(traceback)
        return None
def connect_ext_db(ext_db_name):
    ext_db_router_path = project_path + os.sep + "config" + os.sep + "database" + os.sep + "ext_db_router.yaml"
    db_router_yaml = config_util.get_yaml_config(ext_db_router_path)
    db_type = db_router_yaml[ext_db_name]["db_type"]
    db_config = db_router_yaml[ext_db_name]["db_config"]
    logger.debug(db_type)
    logger.debug(db_config)
    if db_type=='mysql':
       return connect_mysql_db(db_config)


def colse_conn(conn):
    conn.close()



if __name__ == '__main__':
    exit(0)
