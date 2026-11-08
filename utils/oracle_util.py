#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2023/10/4 14:12
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : oracle_util.py
# @Project : HSGTool


import cx_Oracle
from utils import config_util
def connect_db(confName):
    host, port, user, pwd, schema, client_dir=config_util.get_oracle_config(confName)
    cx_Oracle.init_oracle_client(lib_dir=client_dir)
    conn_str='%s/%s@%s:%s/%s'%(user,pwd,host,port,schema)
    conn = cx_Oracle.connect(conn_str)
    return conn

def query(conn,sql):
    cursor=conn.cursor()
    cursor.execute(sql)
    datas=cursor.fetchall()
    cursor.close()
    return datas

def update(conn,sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()

def close_conn(conn):
    conn.close()



if __name__ == '__main__':
    pass