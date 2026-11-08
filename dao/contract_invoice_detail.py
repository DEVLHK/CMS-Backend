#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : contract_invoice_detail.py
# @Project : CMS-Backend
"""合同开票明细 DAO：业务 key = contract_no + invoice_date + seq（seq 由服务层生成）"""
from utils import database_connect_util, mysql_util
from utils.loging_util import logger


class ContractInvoiceDetailDao:
    def __init__(self):
        self.table = "contract_invoice_detail"
        self.id = "id"
        self.contract_no = "contract_no"
        self.invoice_type = "invoice_type"
        self.invoice_date = "invoice_date"
        self.seq = "seq"
        self.invoice_amount = "invoice_amount"
        self.invoice_file = "invoice_file"
        self.create_time = "create_time"
        self.create_by = "create_by"
        self.update_time = "update_time"
        self.update_by = "update_by"
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
        @param fields: {列名: (操作符, 值)}
        @param clauses: 附加子句，如 "order by invoice_date desc, seq limit 0,10"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def query_custom(self, where_sql, values, clauses=None):
        """自定义 where 查询（用于同一列的区间条件），values 与 %s 占位一一对应"""
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select * from {self.table} where {where_sql}"
        if clauses is not None:
            sql += f" {clauses}"
        df = mysql.query(self.conn, sql, tuple(values))
        return {"code": 0, "data": df}

    def count_custom(self, where_sql, values):
        """自定义 where 计数（用于同一列的区间条件）"""
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select count(*) as total from {self.table} where {where_sql}"
        df = mysql.query(self.conn, sql, tuple(values))
        return {"code": 0, "data": int(df.loc[0, "total"])}

    def query_by_id(self, detail_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select * from {self.table} where {self.id}=%s"
        df = mysql.query(self.conn, sql, (detail_id,))
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

    def next_seq(self, contract_no, invoice_date):
        """同合同同开票日期内取 MAX(seq)+1（首笔为 1）"""
        if self.conn is None:
            return None
        mysql = mysql_util.MySQL()
        sql = (f"select IFNULL(MAX({self.seq}), 0) + 1 as next_seq from {self.table} "
               f"where {self.contract_no}=%s and {self.invoice_date}=%s")
        df = mysql.query(self.conn, sql, (contract_no, invoice_date))
        if df is None or len(df) == 0:
            return None
        return int(df.loc[0, "next_seq"])

    def total_amount(self, contract_no):
        """合同总开票金额（无明细返回 0）"""
        if self.conn is None:
            return 0
        mysql = mysql_util.MySQL()
        sql = f"select IFNULL(sum({self.invoice_amount}), 0) as total from {self.table} where {self.contract_no}=%s"
        df = mysql.query(self.conn, sql, (contract_no,))
        return float(df.loc[0, "total"])

    def insert(self, data):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def update(self, update_fields, where_fields):
        if self.conn is None:
            return {"code": -1, "data": None}
        set_clause = ",".join([f"{key} = %s" for key in update_fields.keys()])
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"update {self.table} set {set_clause} where {where_clause}"
        values = tuple(update_fields.values()) + tuple(where_fields.values())
        return self._dml(sql, values)

    def delete_by_id(self, detail_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.id}=%s"
        return self._dml(sql, (detail_id,))

    def delete_by_contract_no(self, contract_no):
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.contract_no}=%s"
        return self._dml(sql, (contract_no,))


if __name__ == '__main__':
    exit(0)
