-- ============================================================================
-- 项目管理菜单清理脚本（cms 库）
-- 背景:
--   CMS-Frontend 已删除 project-manage 相关页面代码（缺陷管理 failed-bug/bug-review、
--   成员任务监控 task-monitor），前端不再存在 view.project-manage_* 组件。
--   路由为 dynamic 模式、菜单由 sys_menu 驱动，若库里仍保留这些菜单行，
--   登录后路由解析 view.project-manage_* 将失败（点击报错/白屏），必须一并清理。
-- 范围:
--   1. sys_role_button 中这些菜单的按钮授权
--   2. sys_role_menu 中这些菜单的角色授权
--   3. sys_menu 菜单行（目录 + 页面，route_name LIKE 'project-manage%'）
-- 执行后需重新登录（菜单/按钮在登录时下发）
-- 注意: 本脚本为 DELETE，执行前建议备份；不影响 contract / schedule-manage / manage 等其他菜单
-- ============================================================================

-- 0. 执行前确认待删菜单（应只包含 项目管理 目录/缺陷管理/失败缺陷管理/待分析失败缺陷/成员任务监控）
SELECT `id`, `parent_id`, `menu_type`, `menu_name`, `route_name`, `route_path`
FROM `sys_menu`
WHERE `route_name` LIKE 'project-manage%';

-- 1. 清理按钮授权
DELETE `rb` FROM `sys_role_button` `rb`
JOIN `sys_menu` `m` ON `m`.`id` = `rb`.`menu_id`
WHERE `m`.`route_name` LIKE 'project-manage%';

-- 2. 清理角色-菜单授权
DELETE `rm` FROM `sys_role_menu` `rm`
JOIN `sys_menu` `m` ON `m`.`id` = `rm`.`menu_id`
WHERE `m`.`route_name` LIKE 'project-manage%';

-- 3. 删除菜单行（先子后父，避免遗留孤儿行）
DELETE FROM `sys_menu`
WHERE `route_name` LIKE 'project-manage_bug-manage%';   -- failed-bug / bug-review

DELETE FROM `sys_menu`
WHERE `route_name` IN ('project-manage_bug-manage', 'project-manage_task-monitor');

DELETE FROM `sys_menu`
WHERE `route_name` = 'project-manage';                  -- 项目管理 目录

-- 执行后验证（应全部返回 0 行）：
--   SELECT id, route_name FROM sys_menu WHERE route_name LIKE 'project-manage%';
--   SELECT rb.* FROM sys_role_button rb JOIN sys_menu m ON m.id = rb.menu_id WHERE m.route_name LIKE 'project-manage%';
--   SELECT rm.* FROM sys_role_menu rm JOIN sys_menu m ON m.id = rm.menu_id WHERE m.route_name LIKE 'project-manage%';
--   KenLin（R_SUPER）重新登录后，左侧菜单不应再出现"项目管理"
