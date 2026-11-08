#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 16:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : sys_menu_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SysMenuDao:
    def __init__(self):
        self.table = "sys_menu"
        self.id = "id"
        self.parent_id = "parent_id"
        self.menu_type = "menu_type"
        self.menu_name = "menu_name"
        self.route_name = "route_name"
        self.route_path = "route_path"
        self.component = "component"
        self.icon = "icon"
        self.icon_type = "icon_type"
        self.route_props = "route_props"
        self.buttons = "buttons"
        self.status = "status"
        self.create_by = "create_by"
        self.create_time = "create_time"
        self.update_by = "update_by"
        self.update_time = "update_time"
        [self.conn, self.engine] = database_connect_util.connect_cms_db()

    def _dml(self, sql, values=None):
        mysql = mysql_util.MySQL()
        result = mysql.execute_dml(self.conn, sql, values)
        if result[0] == 0:
            return {"code": 0, "data": None}
        return {"code": -1, "data": str(result)}

    def query(self, fields=None, clauses=None):
        """
        条件查询，返回 DataFrame（route_props/buttons 为 JSON 字符串，调用方自行解析）
        @param fields: {列名: (操作符, 值)}，如 {self.menu_type: ("=", 2)}
        @param clauses: 附加子句，如 "order by parent_id" / "limit 0,10"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def query_by_id(self, menu_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select * from {self.table} where {self.id}=%s"
        df = mysql.query(self.conn, sql, (menu_id,))
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
        新增菜单，data: {列名: 值}；route_props/buttons 传 JSON 字符串
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def bulk_insert(self, data_list):
        """
        批量新增，data_list: [{列名: 值}, ...]
        """
        if self.conn is None or not data_list:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, params = mysql.generate_bulk_insert_sql(self.table, data_list)
        return self._dml(sql, params)

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
        删除，where_fields: {列名: 值}（等值条件）；
        存在子菜单时业务上应先校验（E1006），sys_role_menu 授权记录随外键 CASCADE 删除
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"delete from {self.table} where {where_clause}"
        return self._dml(sql, tuple(where_fields.values()))

    def delete_many(self, column, values):
        """
        批量删除，column: 列名，values: 值列表（in 条件）
        """
        if self.conn is None or not values:
            return {"code": -1, "data": None}
        placeholders = ",".join(["%s"] * len(values))
        sql = f"delete from {self.table} where {column} in ({placeholders})"
        return self._dml(sql, tuple(values))


if __name__ == '__main__':
    exit(0)
