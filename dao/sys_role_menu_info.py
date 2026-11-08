#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 16:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : sys_role_menu_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SysRoleMenuDao:
    def __init__(self):
        self.table = "sys_role_menu"
        self.role_id = "role_id"
        self.menu_id = "menu_id"
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
        新增授权，data: {role_id: .., menu_id: ..}
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def bulk_insert(self, data_list):
        """
        批量新增授权，data_list: [{role_id: .., menu_id: ..}, ...]
        """
        if self.conn is None or not data_list:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, params = mysql.generate_bulk_insert_sql(self.table, data_list)
        return self._dml(sql, params)

    def replace_role_menus(self, role_id, menu_ids):
        """
        事务内整体替换某角色的菜单授权（先删后插），供角色菜单授权保存使用；
        menu_ids 应已由调用方补全祖先链（目录节点）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"delete from {self.table} where {self.role_id}=%s", (role_id,))
            if menu_ids:
                cursor.executemany(
                    f"insert into {self.table} ({self.role_id}, {self.menu_id}) values (%s, %s)",
                    [(role_id, menu_id) for menu_id in menu_ids]
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
        删除授权，where_fields: {列名: 值}（等值条件）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"delete from {self.table} where {where_clause}"
        return self._dml(sql, tuple(where_fields.values()))

    def delete_by_role(self, role_id):
        """
        删除某角色的全部菜单授权
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.role_id}=%s"
        return self._dml(sql, (role_id,))


if __name__ == '__main__':
    exit(0)
