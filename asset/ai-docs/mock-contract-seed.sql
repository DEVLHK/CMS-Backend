-- ============================================================================
-- 合同管理 mock 数据种子脚本（cms 库）
-- 内容:
--   1. 3 份合同（1 份对应真实样例文档 20261030-1安预XY，1 份作废状态）
--   2. 收款明细 4 笔（含同日期两笔验证 seq 序号）
--   3. 开票明细 3 笔（1 笔带发票图片 mock）
-- 配套文件（非 SQL，由脚本/手工放置）:
--   temp/contracts/20261030-1安预XY/contract.doc       （样例合同）
--   temp/contracts/20261030-1安预XY/invoices/1.png     （发票图片 mock）
--   temp/contracts/20261105-2安预XY/contract.doc       （复制样例文档作占位）
-- 幂等: INSERT IGNORE（按主键 id）；重复执行前如需重置可先 TRUNCATE 三张 contract 表
-- ============================================================================

-- 1. 合同基本信息（vat_tax/gross_profit 为生成列，不插入）
INSERT IGNORE INTO `contract_info`
(`id`,`contract_no`,`contract_month`,`region`,`company_name`,`project_type`,`contract_file`,`contract_amount`,
 `cost_site_audit`,`cost_expert_review`,`cost_intermediary_fee`,`cost_report_commission`,`cost_qualification`,`cost_salesman_commission`,
 `contact_person`,`contact_phone`,`sign_date`,`completion_status`,`status`,`report_file`,`create_by`,`update_by`) VALUES
(1,'20261030-1安预XY','2026-10','茂南区','茂名市信邦建材有限公司','生产安全事故应急预案','temp/contracts/20261030-1安预XY/contract.doc',5000.00,
 500.00,800.00,0.00,300.00,200.00,400.00,
 '张义勇','18814289999','2026-10-30',2,1,'temp/contracts/20261030-1安预XY/report.pdf','KenLin','KenLin'),
(2,'20261105-2安预XY','2026-11','化州市','化州市同庆建材贸易有限公司','生产安全事故应急预案','temp/contracts/20261105-2安预XY/contract.doc',8000.00,
 0.00,1200.00,500.00,400.00,300.00,600.00,
 '李大明','13800138000','2026-11-05',2,1,NULL,'KenLin','KenLin'),
(3,'20261020-1安预XY','2026-10','高州市','高州市潭头五金加工厂','安全评价报告','temp/contracts/20261020-1安预XY/contract.doc',3000.00,
 0.00,0.00,0.00,0.00,0.00,0.00,
 '陈小霞','13911112222','2026-10-20',1,2,NULL,'KenLin','KenLin');

-- 2. 收款明细（合同1 三笔：2026-11-05 同日两笔验证 seq；合同2 一笔）
INSERT IGNORE INTO `contract_receipt_detail`
(`id`,`contract_no`,`receipt_date`,`seq`,`receipt_amount`,`create_by`,`update_by`) VALUES
(1,'20261030-1安预XY','2026-11-01',1,3000.00,'KenLin','KenLin'),
(2,'20261030-1安预XY','2026-11-05',1,1000.00,'KenLin','KenLin'),
(3,'20261030-1安预XY','2026-11-05',2,1000.00,'KenLin','KenLin'),
(4,'20261105-2安预XY','2026-11-06',1,2000.00,'KenLin','KenLin');

-- 3. 开票明细（合同1 两笔：第 1 笔带发票图片；合同2 两笔：同日两笔验证 seq）
INSERT IGNORE INTO `contract_invoice_detail`
(`id`,`contract_no`,`invoice_type`,`invoice_date`,`seq`,`invoice_amount`,`invoice_file`,`create_by`,`update_by`) VALUES
(1,'20261030-1安预XY',1,'2026-11-03',1,5000.00,'temp/contracts/20261030-1安预XY/invoices/1.png','KenLin','KenLin'),
(2,'20261030-1安预XY',2,'2026-11-06',1,NULL,NULL,'KenLin','KenLin'),
(3,'20261105-2安预XY',1,'2026-11-07',1,1500.00,NULL,'KenLin','KenLin'),
(4,'20261105-2安预XY',2,'2026-11-07',2,800.00,NULL,'KenLin','KenLin');

-- 执行后验证：
--   SELECT contract_no, contract_amount, vat_tax, gross_profit FROM contract_info;          -- 生成列自动计算：50/2800、80/5000、30/3000
--   SELECT contract_no, receipt_date, seq, receipt_amount FROM contract_receipt_detail;     -- 合同1 余收款 = 5000-5000 = 0
--   SELECT contract_no, invoice_date, seq, invoice_file FROM contract_invoice_detail;       -- 合同1 余开票 = 5000-5000 = 0
