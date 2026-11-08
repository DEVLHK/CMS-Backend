#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/19 10:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : scheduler_job_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SchedulerJobDao:
    def __init__(self):
        self.table = "scheduler_job"
        self.id = "id"
        self.job_name = "job_name"
        self.script_name = "script_name"
        self.description = "description"
        self.period_type = "period_type"
        self.period_interval = "period_interval"
        self.first_run_date = "first_run_date"
        self.first_run_time = "first_run_time"
        self.last_run_time = "last_run_time"
        self.last_run_date = "last_run_date"
        self.last_run_status = "last_run_status"
        self.enabled = "enabled"
        self.log_level = "log_level"
        self.params = "params"
        self.create_time = "create_time"
        self.create_by = "create_by"
        self.update_time = "update_time"
        self.update_by = "update_by"
        self.ts = "ts"
        [self.conn, self.engine] = database_connect_util.connect_cms_db()

    def _dml(self, sql, values=None):
        mysql = mysql_util.MySQL()
        result = mysql.execute_dml(self.conn, sql, values)
        if result[0] == 0:
            return {"code": 0, "data": None}
        return {"code": -1, "data": str(result)}

    def query(self, fields=None, clauses=None):
        """
        条件查询，返回 DataFrame
        @param fields: {列名: (操作符, 值)}，如 {self.job_name: ("like", "%同步%")}（job_name/script_name 模糊查询）
        @param clauses: 附加子句，如 "order by id desc limit 0,10"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def query_by_id(self, job_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select * from {self.table} where {self.id}=%s"
        df = mysql.query(self.conn, sql, (job_id,))
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
        新增定时任务，data: {列名: 值}，自增 id 无需传入
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def update(self, update_fields, where_fields):
        """
        更新，update_fields/where_fields: {列名: 值}（where 为等值条件）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        set_clause = ",".join([f"{key} = %s" for key in update_fields.keys()])
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"update {self.table} set {set_clause} where {where_clause}"
        values = tuple(update_fields.values()) + tuple(where_fields.values())
        return self._dml(sql, values)

    def delete(self, where_fields):
        """
        删除，where_fields: {列名: 值}（等值条件）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"delete from {self.table} where {where_clause}"
        return self._dml(sql, tuple(where_fields.values()))

    def delete_by_id(self, job_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.id}=%s"
        return self._dml(sql, (job_id,))


if __name__ == '__main__':
    exit(0)
