#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 16:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : sys_user_role_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SysUserRoleDao:
    def __init__(self):
        self.table = "sys_user_role"
        self.user_id = "user_id"
        self.role_id = "role_id"
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
        @param fields: {列名: (操作符, 值)}，如 {self.user_id: ("=", 1)}
        @param clauses: 附加子句，如 "order by user_id"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def insert(self, data):
        """
        新增关联，data: {user_id: .., role_id: ..}
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def bulk_insert(self, data_list):
        """
        批量新增关联，data_list: [{user_id: .., role_id: ..}, ...]
        """
        if self.conn is None or not data_list:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, params = mysql.generate_bulk_insert_sql(self.table, data_list)
        return self._dml(sql, params)

    def replace_user_roles(self, user_id, role_ids):
        """
        事务内整体替换某用户的角色关联（先删后插），供编辑用户使用
        @param user_id: 用户ID
        @param role_ids: 角色ID列表
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"delete from {self.table} where {self.user_id}=%s", (user_id,))
            if role_ids:
                cursor.executemany(
                    f"insert into {self.table} ({self.user_id}, {self.role_id}) values (%s, %s)",
                    [(user_id, role_id) for role_id in role_ids]
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
        删除关联，where_fields: {列名: 值}（等值条件），如 {user_id: 1} 或 {user_id: 1, role_id: 2}
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"delete from {self.table} where {where_clause}"
        return self._dml(sql, tuple(where_fields.values()))

    def delete_by_role(self, role_id):
        """
        删除某角色的全部用户关联（角色删除前清理，避免外键 RESTRICT）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.role_id}=%s"
        return self._dml(sql, (role_id,))


if __name__ == '__main__':
    exit(0)
