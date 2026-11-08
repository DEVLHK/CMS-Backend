-- ============================================================================
-- 合同管理菜单种子脚本（cms 库）
-- 内容:
--   1. 新增菜单：86 合同管理（目录）→ 87 合同基本信息（页面）
--   2. 87 配置按钮权限码（buttons JSON）：新增/修改/删除/作废/收款明细/开票明细/报告上传/合同下载
--   3. R_SUPER 授予两个菜单（幂等）
-- 幂等: INSERT IGNORE（route_name 唯一键兜底），UPDATE/授权可重复执行
-- 前端对应: CMS-Frontend 路由 contract/basic-info（view.contract_basic-info）
-- ============================================================================

-- 1. 新增菜单
-- 注意: 图标必须使用 Iconify MDI 中真实存在的名称（运行时经 api.iconify.design 拉取，
--       不存在的名称会渲染为空白，如曾用过的 mdi:file-signature 即不存在）
INSERT IGNORE INTO `sys_menu` (`id`,`parent_id`,`menu_type`,`menu_name`,`route_name`,`route_path`,`component`,`icon`,`icon_type`,`route_props`,`buttons`,`status`) VALUES
(86,0,1,'合同管理','contract','/contract','layout.base','mdi:file-sign',1,'{"i18nKey":"route.contract","order":2}',NULL,1),
(87,86,2,'合同基本信息','contract_basic-info','/contract/basic-info','view.contract_basic-info','',1,'{"i18nKey":"route.contract_basic-info","order":1,"keepAlive":true}',NULL,1);

-- 2. 合同基本信息按钮权限码
UPDATE `sys_menu`
SET `buttons` = '[
  {"code": "B_CONTRACT::BTN_ADD", "desc": "新增合同"},
  {"code": "B_CONTRACT::BTN_EDIT", "desc": "修改合同"},
  {"code": "B_CONTRACT::BTN_DELETE", "desc": "删除合同"},
  {"code": "B_CONTRACT::BTN_VOID", "desc": "作废合同"},
  {"code": "B_CONTRACT::BTN_RECEIPT", "desc": "收款明细"},
  {"code": "B_CONTRACT::BTN_INVOICE", "desc": "开票明细"},
  {"code": "B_CONTRACT::BTN_UPLOAD_REPORT", "desc": "报告上传"},
  {"code": "B_CONTRACT::BTN_DOWNLOAD_CONTRACT", "desc": "合同下载"}
]'
WHERE `id` = 87 AND `route_name` = 'contract_basic-info';

-- 3. R_SUPER 授予新菜单（幂等）
INSERT IGNORE INTO `sys_role_menu` (`role_id`,`menu_id`)
SELECT r.`id`, m.`id` FROM `sys_role` r JOIN `sys_menu` m ON m.`id` IN (86,87)
WHERE r.`role_code` = 'R_SUPER';

-- 执行后验证：
--   SELECT id, route_name, buttons FROM sys_menu WHERE id IN (86,87);
--   KenLin（R_SUPER）重新登录后应出现 合同管理/合同基本信息 菜单
