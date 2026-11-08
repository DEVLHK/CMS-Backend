#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 19:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : sys_role_button_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SysRoleButtonDao:
    def __init__(self):
        self.table = "sys_role_button"
        self.role_id = "role_id"
        self.menu_id = "menu_id"
        self.button_code = "button_code"
        self.create_time = "create_time"
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
        @param fields: {列名: (操作符, 值)}，如 {self.role_id: ("=", 1)}
        @param clauses: 附加子句，如 "order by menu_id"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def insert(self, data):
        """
        新增按钮授权，data: {role_id: .., menu_id: .., button_code: ..}
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def bulk_insert(self, data_list):
        """
        批量新增按钮授权，data_list: [{role_id: .., menu_id: .., button_code: ..}, ...]
        """
        if self.conn is None or not data_list:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, params = mysql.generate_bulk_insert_sql(self.table, data_list)
        return self._dml(sql, params)

    def replace_role_buttons(self, role_id, button_records):
        """
        事务内整体替换某角色的按钮授权（先删后插），供角色按钮授权保存使用；
        语义：某菜单无记录 = 该菜单按钮全给（调用方决定记录内容）
        @param button_records: [(menu_id, button_code), ...]
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"delete from {self.table} where {self.role_id}=%s", (role_id,))
            if button_records:
                cursor.executemany(
                    f"insert into {self.table} ({self.role_id}, {self.menu_id}, {self.button_code}) values (%s, %s, %s)",
                    [(role_id, menu_id, button_code) for menu_id, button_code in button_records]
                )
            self.conn.commit()
            cursor.close()
            return {"code": 0, "data": None}
        except Exception as e:
            self.conn.rollback()
            logger.error(e)
            return {"code": -1, "data": str(e)}

    def delete(self, where_fields):
        """
        删除按钮授权，where_fields: {列名: 值}（等值条件）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"delete from {self.table} where {where_clause}"
        return self._dml(sql, tuple(where_fields.values()))

    def delete_by_role(self, role_id):
        """
        删除某角色的全部按钮授权
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.role_id}=%s"
        return self._dml(sql, (role_id,))


if __name__ == '__main__':
    exit(0)
