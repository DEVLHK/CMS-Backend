# -*- coding: utf-8 -*-
# @Function: 
# @Author: Jamie
# @Time : 2024/12/18 15:45
from utils import database_connect_util, mysql_util


class SelectionInfoDao:
    def __init__(self):
        self.PROJECT_ID = 'project_id'
        self.TYPE = 'type'
        self.CODE = 'code'
        self.CN_DESCRIPTION = 'cn_description'
        self.EN_DESCRIPTION = 'en_description'
        self.SUB_TYPE = 'sub_type'
        [self.conn,self.engine] = database_connect_util.connect_cms_db()

    def selection_query(self, selection_types=list, project_id=str):
        if self.conn is None:
            return {"code": -1, "data": None}
        else:
            mysql = mysql_util.MySQL()
            sql = "select * from common_selection where type in (%s) and project_id = %s"
            condition = ','.join(['%s'] * len(selection_types))
            print(condition)
            # 动态构建in里的%
            sql = sql.replace("(%s)", f"({condition})")
            print(sql)
            # 组装实际参数值
            params = tuple(selection_types) + (project_id,)
            df = mysql.query(self.conn, sql, params)
            return {"code": 0, "data": df}

    def close_conn(self):
        if self.conn:
            self.conn.close()
