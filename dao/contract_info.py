#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : contract_info.py
# @Project : CMS-Backend
"""合同基本信息 DAO：vat_tax/gross_profit 为生成列，insert/update 必须排除"""
from utils import database_connect_util, mysql_util
from utils.loging_util import logger

# 应用层不可写的生成列（MySQL 自动计算）
GENERATED_COLUMNS = ("vat_tax", "gross_profit")


class ContractInfoDao:
    def __init__(self):
        self.table = "contract_info"
        self.id = "id"
        self.contract_no = "contract_no"
        self.contract_month = "contract_month"
        self.region = "region"
        self.company_name = "company_name"
        self.project_type = "project_type"
        self.contract_file = "contract_file"
        self.contract_pdf_file = "contract_pdf_file"
        self.contract_amount = "contract_amount"
        self.cost_site_audit = "cost_site_audit"
        self.cost_expert_review = "cost_expert_review"
        self.cost_intermediary_fee = "cost_intermediary_fee"
        self.cost_report_commission = "cost_report_commission"
        self.cost_qualification = "cost_qualification"
        self.cost_salesman_commission = "cost_salesman_commission"
        self.vat_tax = "vat_tax"
        self.gross_profit = "gross_profit"
        self.contact_person = "contact_person"
        self.contact_phone = "contact_phone"
        self.sign_date = "sign_date"
        self.completion_status = "completion_status"
        self.status = "status"
        self.report_file = "report_file"
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
        @param fields: {列名: (操作符, 值)}，如 {self.company_name: ("like", "%信邦%")}
        @param clauses: 附加子句，如 "order by id desc limit 0,10"
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        df = mysql.query_with_param(self.conn, self.table, fields, clauses)
        logger.debug(df)
        return {"code": 0, "data": df}

    def query_with_totals(self, fields=None, clauses=None, extra_conditions=None):
        """联表汇总查询：附带总收款/总开票金额（余收款=contract_amount-总收款，余开票同理）
        @param fields: {列名: (操作符, 值)}（等值/like，逐列拼接）
        @param extra_conditions: [(sql片段, 值)]，用于同一列的区间条件（如月份 >=/<=）"""
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = ("select c.*, IFNULL(r.total_receipt, 0) as total_receipt, IFNULL(i.total_invoice, 0) as total_invoice "
               "from contract_info c "
               "left join (select contract_no, sum(receipt_amount) as total_receipt from contract_receipt_detail "
               "           group by contract_no) r on r.contract_no = c.contract_no "
               "left join (select contract_no, sum(invoice_amount) as total_invoice from contract_invoice_detail "
               "           group by contract_no) i on i.contract_no = c.contract_no "
               "where 1=1")
        values = []
        if fields:
            for field_name in fields.keys():
                operator = fields[field_name][0]
                field_value = fields[field_name][1]
                sql += f" and c.{field_name} {operator} %s"
                values.append(field_value)
        for condition_sql, condition_value in extra_conditions or []:
            sql += f" and {condition_sql}"
            if isinstance(condition_value, (list, tuple)):
                values.extend(condition_value)   # IN 条件按占位符个数展开
            else:
                values.append(condition_value)
        if clauses is not None:
            sql += f" {clauses}"
        df = mysql.query(self.conn, sql, tuple(values))
        return {"code": 0, "data": df}

    def query_by_id(self, contract_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select * from {self.table} where {self.id}=%s"
        df = mysql.query(self.conn, sql, (contract_id,))
        return {"code": 0, "data": df}

    def query_by_no(self, contract_no):
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select * from {self.table} where {self.contract_no}=%s"
        df = mysql.query(self.conn, sql, (contract_no,))
        return {"code": 0, "data": df}

    def count(self, fields=None, extra_conditions=None):
        """带 c. 别名，与 query_with_totals 一致（extra_conditions 由调用方携带 c. 前缀）"""
        if self.conn is None:
            return {"code": -1, "data": None}
        mysql = mysql_util.MySQL()
        sql = f"select count(*) as total from {self.table} c where 1=1"
        values = []
        if fields:
            for field_name in fields.keys():
                operator = fields[field_name][0]
                field_value = fields[field_name][1]
                sql += f" and c.{field_name} {operator} %s"
                values.append(field_value)
        for condition_sql, condition_value in extra_conditions or []:
            sql += f" and {condition_sql}"
            if isinstance(condition_value, (list, tuple)):
                values.extend(condition_value)   # IN 条件按占位符个数展开
            else:
                values.append(condition_value)
        df = mysql.query(self.conn, sql, tuple(values))
        return {"code": 0, "data": int(df.loc[0, "total"])}

    def insert(self, data):
        """
        新增合同，data: {列名: 值}，自增 id/生成列无需传入
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        data = {k: v for k, v in data.items() if k not in GENERATED_COLUMNS}
        mysql = mysql_util.MySQL()
        sql, values = mysql.generate_insert_sql(self.table, data)
        return self._dml(sql, values)

    def update(self, update_fields, where_fields):
        """
        更新，update_fields/where_fields: {列名: 值}（where 为等值条件）
        """
        if self.conn is None:
            return {"code": -1, "data": None}
        update_fields = {k: v for k, v in update_fields.items() if k not in GENERATED_COLUMNS}
        set_clause = ",".join([f"{key} = %s" for key in update_fields.keys()])
        where_clause = " and ".join([f"{key} = %s" for key in where_fields.keys()])
        sql = f"update {self.table} set {set_clause} where {where_clause}"
        values = tuple(update_fields.values()) + tuple(where_fields.values())
        return self._dml(sql, values)

    def delete_by_id(self, contract_id):
        if self.conn is None:
            return {"code": -1, "data": None}
        sql = f"delete from {self.table} where {self.id}=%s"
        return self._dml(sql, (contract_id,))


if __name__ == '__main__':
    exit(0)
