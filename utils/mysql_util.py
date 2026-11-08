#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2023/10/5 00:57
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : mysql_util.py
# @Project : hbs_flink
import os
from urllib.parse import quote_plus

import pymysql
import numpy
import pandas
import yaml
import traceback

from utils import config_util
from utils.loging_util import logger
from sqlalchemy import create_engine, text


def _to_pandas(cursor, datas):
    """
    将表数据数据成dataform
    @param cursor:表游标
    @param datas:表数据
    @return:dataform格式的表数据
    """
    if len(datas) == 0:
        return None
    else:
        columns = cursor.description
        column_names = []
        logger.debug(columns)
        for (column_name, t1, t2, t3, t4, t5, t6) in columns:
            column_names.append(column_name)
        # logger.debug(datas)
        np = numpy.array(datas)
        logger.debug(np)
        df = pandas.DataFrame(np, columns=column_names)
        logger.debug(df.columns)
        logger.debug(df.dtypes)
    return df


class MySQL:
    db = None  # conn实例
    engine = None  # engine实例
    schema = ""
    is_connected = False

    def init_connect(self, conf=None,confName=None):
        host, port, user, password, schema = None, None, None, None, None
        if not conf:
            if confName:
                logger.debug("conf:" + str(confName))
                conf=config_util.get_mysql_config(confName)
        if conf:
            host, port, user, password, schema = conf['host'], conf['port'], conf['user'], conf['password'], conf[
            'schema']
        self.schema = schema
        if not self.is_connected:
            logger.debug("connecting mysql....")
            self.db = pymysql.connect(
                host=host,
                port=port,
                user=user,
                passwd=password,
                db=schema,
                charset='utf8')
            logger.debug("connected success！")
            encoded_password = quote_plus(password)
            self.engine = create_engine(f'mysql+pymysql://user:{encoded_password}@{host}:{port}/{schema}')
        self.is_connected = True

    def close_connect(self):
        if self.is_connected:
            self.db.close()
            self.is_connected = False

    def query(self, conn, sql, condition=None):
        """
        根据sql查询表,并返回dataform格式数据
        @param conn: 数据库连接
        @param sql:sql statement
        @return:
        """
        try:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql, condition)
                datas = cursor.fetchall()
                # logger.debug(datas)
                df = _to_pandas(cursor, datas)
                cursor.close()
            else:
                df = None
            return df
        except Exception as e:
            logger.error(e)
            logger.error(sql)
            logger.error(condition)
            exit(-1)

    def query_with_param(self, conn, table, fields=None, clauses=None):
        if fields is None :
            fields = {}
        sql = f"select * from {table} where 1=1"
        values = [ ]
        for field_name in fields.keys() :
            operator = fields[ field_name ][ 0 ]
            field_value = fields[ field_name ][ 1 ]
            if operator !="in" and operator !="not in":
                sql += f" and {field_name} {operator} %s"
                values.append(field_value)
            else:
                placeholders = ','.join([ '%s' ] * len(field_value))
                sql += f" and {field_name} {operator} ({placeholders})"
                for val in field_value:
                    values.append(val)
        if clauses is not None:
            sql = sql + f' {clauses}'
        # 执行查询
        df = self.query(conn, sql, tuple(values))
        return df

    # def execute_dml(self,sql):
    #     try:
    #         cursor = self.db.cursor()
    #         cursor.execute(sql)
    #         self.db.commit()
    #         return (0,"")
    #     except Exception as e:
    #         print(e)
    #         ret=str(e).replace('(',"").replace(')',"").split(",",1)
    #         return tuple(ret)

    def execute_dml(self, conn, sql, condition=None):
        try:
            cursor = conn.cursor()
            if isinstance(condition, list) and len(condition) >= 1:
                cursor.executemany(sql, condition)
            else:
                cursor.execute(sql, condition)
            conn.commit()
            return (0, "")
        except Exception as e:
            logger.error(f"execute_dml failed: {sql} | params={condition} | error={e}")
            print(e)
            ret = str(e).replace('(', "").replace(')', "").split(",", 1)
            return tuple(ret)

    def generate_insert_sql(self, table_name, data):
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
        return sql, tuple(data.values())

    def generate_bulk_insert_sql(self, table_name, data_list):
        if not data_list:
            return "", []

        # 获取字段名（假设所有记录的字段名一致）
        fields = ", ".join(data_list[0].keys())

        # 为每条记录生成占位符
        placeholders = ", ".join(["%s"] * len(data_list[0]))

        # 创建 SQL 语句
        sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

        # 取所有记录的值
        params = [tuple(record.values()) for record in data_list]

        return sql, params

    # def generate_bulk_duplicate_update_sql(self, table_name, data_list,duplicate_update_fields):
    #     if not data_list:
    #         return "", []
    #
    #     # 获取字段名（假设所有记录的字段名一致）
    #     fields = ", ".join(data_list[0].keys())
    #     update_field_list=[]
    #     for field in duplicate_update_fields:
    #         update_field_list.append(f"{field}=VALUES({field})")
    #     update_fields=", ".join(update_field_list)
    #     # 为每条记录生成占位符
    #     placeholders = ", ".join(["%s"] * len(data_list[0]))
    #
    #     # 创建 SQL 语句
    #     sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_fields}"
    #
    #     # 获取所有记录的值
    #     params = [tuple(record.values()) for record in data_list]
    #
    #     return sql, params




    def upsert_to_sql(self,df,engine,table_name, key_columns) :
        """
        自定义UPSERT：存在则更新，不存在则插入

        参数:
        df: DataFrame
        table_name: 表名
        engine: SQLAlchemy引擎
        key_columns: 主键列名列表
        """
        with engine.connect() as conn :
            # 构建INSERT ... ON DUPLICATE KEY UPDATE语句
            columns = ', '.join([ f'`{col}`' for col in df.columns ])
            placeholders = ', '.join([ f':{col}' for col in df.columns ])

            # 构建UPDATE部分
            update_cols = [ f'`{col}` = VALUES(`{col}`)'
                            for col in df.columns if col not in key_columns ]
            update_clause = ', '.join(update_cols)

            sql = f"""
            INSERT INTO {table_name} ({columns}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
            """
            logger.debug(sql)
            # 转换为字典列表
            data = df.to_dict('records')
            conn.execute(text(sql), data)
            conn.commit()

            print(f"成功UPSERT {len(data)} 条记录")




if __name__ == '__main__':
    exit(0)
