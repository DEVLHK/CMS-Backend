#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/20 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : scheduler_job_run_log_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SchedulerJobRunLogDao:
    def __init__(self):
        self.table = "scheduler_job_run_log"
        self.id = "id"
        self.job_id = "job_id"
        self.script_name = "script_name"
        self.trigger_type = "trigger_type"
        self.status = "status"
        self.start_time = "start_time"
        self.end_time = "end_time"
        self.pid = "pid"
        self.output = "output"
        [self.conn, self.engine] = database_connect_util.connect_cms_db()

    def query(self, fields=None, clauses=None):
        """
        条件查询，返回 DataFrame
        @param fields: {列名: (操作符, 值)}，如 {self.job_id: ("=", 1)}
        @param clauses: 附加子句，如 "order by start_time desc limit 0,10"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def count(self, fields=None):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select count(*) as total from {self.table} where 1=1"
        values = []
        if fields:
            for field_name in fields.keys():
                operator = fields[field_name][0]
                field_value = fields[field_name][1]
                sql += f" and {field_name} {operator} %s"
                values.append(field_value)
        df = mysql.query(self.conn, sql, tuple(values))
        return {"code": 0, "data": int(df.loc[0, "total"])}

    def insert(self, data):
        """
        写入一条运行记录，data: {列名: 值}
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def query_latest_id(self, job_id):
        """某任务最新一条运行记录的 id（插入后回查用）"""
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select {self.id} from {self.table} where {self.job_id}=%s order by {self.id} desc limit 1"
        df = mysql.query(self.conn, sql, (job_id,))
        if df is None or len(df) == 0:
            return {"code": -1, "data": None}
        return {"code": 0, "data": int(df.loc[0, self.id])}

    def update_by_id(self, run_id, update_fields):
        """
        按运行记录 id 更新
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        set_clause = ",".join([f"{key} = %s" for key in update_fields.keys()])
        sql = f"update {self.table} set {set_clause} where {self.id}=%s"
        values = tuple(update_fields.values()) + (run_id,)
        return self._dml(sql, values)

    def _dml(self, sql, values=None):
        mysql = mysql_util.MySQL()
        result = mysql.execute_dml(self.conn, sql, values)
        if result[0] == 0:
            return {"code": 0, "data": None}
        return {"code": -1, "data": str(result)}


if __name__ == '__main__':
    exit(0)
