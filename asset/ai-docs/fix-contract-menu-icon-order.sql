-- ============================================================================
-- 合同管理菜单修正脚本（cms 库）
-- 内容:
--   1. 图标修正: mdi:file-signature 在 Iconify MDI 图标集中不存在（not_found），
--      运行时拉取 404 导致菜单图标空白；换成真实存在的 mdi:file-sign
--   2. 菜单位置: route_props.order 11 -> 2，排在"首页"(order=1)正下方
-- 幂等: UPDATE，可重复执行；生效需重新登录（菜单在登录时下发）
-- ============================================================================

UPDATE `sys_menu`
SET `icon` = 'mdi:file-sign',
    `route_props` = '{"i18nKey":"route.contract","order":2}'
WHERE `id` = 86 AND `route_name` = 'contract';

-- 执行后验证：
--   SELECT id, menu_name, icon, route_props FROM sys_menu WHERE id = 86;
--   预期: icon = mdi:file-sign，order = 2
--   重新登录后：菜单图标正常显示，位置在"首页"下方第一位
