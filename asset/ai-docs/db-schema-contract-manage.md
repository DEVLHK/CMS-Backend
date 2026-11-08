# 合同管理表结构设计

> 状态：**已确认（2026-11-08）**。需求决议见 `asset/ai-docs/contract-manage-requirement.md` 第 6 章（明细 key = 合同编号+日期+序号）。
> 目标库：cms（192.168.201.89）。字符集与工程一致：`utf8mb4 / utf8mb4_general_ci`，引擎 InnoDB。
> 通用审计列与工程现有表保持一致：`create_by/create_time/update_by/update_time`。

## 1. 表清单

| 表名 | 说明 | 关系 |
|---|---|---|
| `contract_info` | 合同基本信息（主表） | 1 个合同 ↔ N 收款 / N 开票 |
| `contract_receipt_detail` | 合同收款明细 | contract_no 关联主表 |
| `contract_invoice_detail` | 合同开票明细 | contract_no 关联主表 |

不落表的字段（前端展示/查询时计算）：
- **序号**：前端顺序生成
- **余收款金额** = contract_amount − SUM(receipt_amount)
- **余开票金额** = contract_amount − SUM(invoice_amount)
- **毛利润**、**增值税费**：落表，见 2.1 说明

## 2. 表结构

### 2.1 contract_info 合同基本信息

```sql
CREATE TABLE `contract_info` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_no` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '合同编号（业务key，修改不可改）',
  `contract_month` char(7) COLLATE utf8mb4_general_ci NOT NULL COMMENT '合同签订月份 YYYY-MM（按签约日期预填，可修正）',
  `region` varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT '区域：茂南区/化州市/高州市/电白区/高新区/滨海新区',
  `company_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL COMMENT '企业名称（合同甲方，模糊查询不分大小写）',
  `project_type` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '项目类型',
  `contract_file` varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT '合同 Word 文件相对路径 temp/contracts/{contract_no}/',
  `contract_pdf_file` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'PDF 合同副本相对路径（存档/下载），NULL=未上传',
  `contract_amount` decimal(14,2) NOT NULL COMMENT '合同金额（合同技术服务费）',
  `cost_site_audit` decimal(14,2) NOT NULL DEFAULT '0.00' COMMENT '成本核算-现场核查',
  `cost_expert_review` decimal(14,2) NOT NULL DEFAULT '0.00' COMMENT '成本核算-专家评审',
  `cost_intermediary_fee` decimal(14,2) NOT NULL DEFAULT '0.00' COMMENT '成本核算-居间费用',
  `cost_report_commission` decimal(14,2) NOT NULL DEFAULT '0.00' COMMENT '成本核算-报告编制提成',
  `cost_qualification` decimal(14,2) NOT NULL DEFAULT '0.00' COMMENT '成本核算-资质费/分包费',
  `cost_salesman_commission` decimal(14,2) NOT NULL DEFAULT '0.00' COMMENT '成本核算-业务员提成',
  `vat_tax` decimal(14,2) GENERATED ALWAYS AS (`contract_amount` * 0.01) STORED COMMENT '增值税费=合同金额×1%（自动计算）',
  `gross_profit` decimal(14,2) GENERATED ALWAYS AS (`contract_amount` - (`cost_site_audit` + `cost_expert_review` + `cost_intermediary_fee` + `cost_report_commission` + `cost_qualification` + `cost_salesman_commission`)) STORED COMMENT '毛利润=合同金额-成本核算六项合计（自动计算）',
  `contact_person` varchar(30) COLLATE utf8mb4_general_ci NOT NULL COMMENT '联系人',
  `contact_phone` char(11) COLLATE utf8mb4_general_ci NOT NULL COMMENT '联系方式（手机号）',
  `sign_date` date NOT NULL COMMENT '签约日期',
  `expire_date` date NOT NULL COMMENT '合同到期日期=签约日期+1年（后端自动计算，2/29→次年2/28，前端不传）',
  `completion_status` tinyint NOT NULL DEFAULT '2' COMMENT '项目完成情况 1:完成 2:未完成',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态 1:生效 2:作废',
  `report_file` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '报告文件相对路径，NULL=未上传',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_contract_no` (`contract_no`),
  KEY `idx_month` (`contract_month`),
  KEY `idx_region` (`region`),
  KEY `idx_company_name` (`company_name`),
  KEY `idx_completion_status` (`completion_status`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='合同基本信息';
```

说明：
- `vat_tax`/`gross_profit` 用 MySQL **生成列（STORED）**，成本/金额修改后自动重算，应用层不可写（DAO 的 insert/update 需排除这两列）。如不想用生成列，可改为应用层写入的普通列，效果相同。
- 未选填的成本项落 `0.00`（前端可不填），毛利润计算天然成立。

### 2.2 contract_receipt_detail 合同收款明细

```sql
CREATE TABLE `contract_receipt_detail` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_no` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '合同编号（从主表带出，不可改）',
  `receipt_date` date NOT NULL COMMENT '收款日期（业务key之一，修改不可改）',
  `seq` int NOT NULL COMMENT '序号（同合同同收款日期内自动+1，业务key之一）',
  `receipt_amount` decimal(14,2) DEFAULT NULL COMMENT '收款金额（≥0，选填）',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_contract_receipt` (`contract_no`, `receipt_date`, `seq`),
  KEY `idx_receipt_date` (`receipt_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='合同收款明细';
```

> 业务 key = 合同编号 + 收款日期 + 序号（需求决议 Q2）。`seq` 由后端在新增时按 `(contract_no, receipt_date)` 分组取 MAX+1 自动生成；修改/删除按物理主键 `id` 定位。

### 2.3 contract_invoice_detail 合同开票明细

```sql
CREATE TABLE `contract_invoice_detail` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_no` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '合同编号（从主表带出，不可改）',
  `invoice_type` tinyint NOT NULL COMMENT '开票类型 1:专票 2:普票',
  `invoice_date` date NOT NULL COMMENT '开票日期（≤当天，业务key之一）',
  `seq` int NOT NULL COMMENT '序号（同合同同开票日期内自动+1，业务key之一）',
  `invoice_amount` decimal(14,2) DEFAULT NULL COMMENT '开票金额（≥0，选填）',
  `invoice_file` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发票图片相对路径（仅图片，选填）temp/contracts/{contract_no}/invoices/',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_contract_invoice` (`contract_no`, `invoice_date`, `seq`),
  KEY `idx_invoice_date` (`invoice_date`),
  KEY `idx_invoice_type` (`invoice_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='合同开票明细';
```

> 业务 key = 合同编号 + 开票日期 + 序号（需求决议 Q1）。`seq` 生成规则同收款明细；修改/删除按物理主键 `id` 定位。

## 3. 文件目录布局

```
temp/contracts/
├── _incoming/                  # 上传暂存区（解析用，落库后移走）
│   └── {uuid}.doc
└── {合同编号}/
    ├── contract.doc            # 合同原件（固定格式 Word，重复上传覆盖）
    ├── report.*                # 报告文件（选填，覆盖式）
    └── invoices/
        ├── {明细id}.png         # 发票图片（仅图片格式）
        └── ...
```

- 删除合同 → 同步删除 `temp/contracts/{合同编号}/` 整个目录
- 删除开票明细 → 同步删除对应发票文件

## 4. 查询条件与索引对应

| 需求查询项 | 实现 |
|---|---|
| 合同编号（模糊、不分大小写） | `contract_no LIKE %x%`（utf8mb4_general_ci 不区分大小写） |
| 企业名称（模糊、不分大小写） | `company_name LIKE %x%` |
| 完成情况 | `completion_status =` |
| 月份范围（默认当月） | `contract_month BETWEEN` |
| 区域 / 项目类型 | `=` |
| 是否生效 | `status =` |
| 收款明细：合同编号 + 日期区间 | `contract_no =` + `receipt_date BETWEEN` |
| 开票明细：合同编号 + 日期区间 + 类型 | `contract_no =` + `invoice_date BETWEEN` + `invoice_type =` |

## 5. API 清单（注册到 config/router/router.yaml，命名空间 contractManage）

| 接口 | 方法 | 说明 |
|---|---|---|
| uploadContract | POST | **先上传后解析**（需求决议 Q3）：multipart 上传 .doc → 暂存 `_incoming/` → 解析固定格式 → 返回预填字段（合同编号/企业名称/项目类型/金额/签约日期/联系人/联系方式/月份）+ 暂存文件引用 |
| getContractList | GET | 分页+查询条件，列表含余收款/余开票（联表汇总） |
| addContract | POST | 落库（file=暂存文件引用），落库后将合同移至 `temp/contracts/{编号}/contract.doc` |
| updateContract | POST | 修改（contract_no 不可改；可重新上传合同/报告覆盖） |
| deleteContract | POST | 删除（二次确认由前端做），级联删明细与文件目录 |
| voidContract | POST | 作废（status=2）；作废后主表不可改、明细禁增删改（需求决议 Q6） |
| getReceiptList | GET | 收款明细分页（含上方基础信息：编号/客户/余收款） |
| addReceipt / updateReceipt / deleteReceipt | POST | 收款维护（新增时 seq 自动生成；修改时 receipt_date 不可改；作废合同禁止） |
| getInvoiceList | GET | 开票明细分页（含余开票） |
| addInvoice / updateInvoice / deleteInvoice | POST | 开票维护（seq 自动生成；file 仅图片；作废合同禁止） |
| previewInvoice | GET | 预览发票图片 |
| downloadInvoice | GET | 下载发票图片 |

合同解析的提取依赖与正则锚点见需求文档第 8 章（antiword / textutil / libreoffice 三级兜底）。

## 6. 菜单/按钮 seed（开发完成后）

- `sys_menu` 新增：`1. 合同管理`（目录）→ `1.1 合同基本信息`（页面）
- 按钮（buttons JSON）：新增、修改、删除、作废、开票明细、收款明细
- `sys_role_menu` / `sys_role_button` 按需授权
