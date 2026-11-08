#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 16:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : sys_refresh_token_info.py
# @Project : Soybean-backend
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class SysRefreshTokenDao:
    def __init__(self):
        self.table = "sys_refresh_token"
        self.id = "id"
        self.user_id = "user_id"
        self.token_hash = "token_hash"
        self.expires_at = "expires_at"
        self.revoked = "revoked"
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
        @param fields: {列名: (操作符, 值)}，如 {self.token_hash: ("=", hash)}、{self.expires_at: (">", dt)}
        @param clauses: 附加子句，如 "order by create_time desc"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def insert(self, data):
        """
        新增刷新令牌，data: {user_id: .., token_hash: .., expires_at: ..}
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

    def revoke(self, token_hash):
        """
        吊销刷新令牌（登出/轮换/强制下线）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"update {self.table} set {self.revoked}=1 where {self.token_hash}=%s"
        return self._dml(sql, (token_hash,))

    def revoke_by_user(self, user_id):
        """
        吊销某用户全部刷新令牌（删除用户/禁用用户/改密强制下线）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"update {self.table} set {self.revoked}=1 where {self.user_id}=%s"
        return self._dml(sql, (user_id,))

    def delete(self, where_fields):
        """
        删除，where_fields: {列名: 值}（等值条件）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"delete from {self.table} where {where_clause}"
        return self._dml(sql, tuple(where_fields.values()))


if __name__ == '__main__':
    exit(0)
