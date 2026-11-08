-- ============================================================================
-- sys_menu 按钮权限补丁（MySQL 5.7）
-- 按 Soybean 前端架构为系统管理菜单补充按钮权限码：
--   定义处：菜单管理 buttons JSON（MenuButton {code, desc}）
--   消费处：useAuth().hasAuth('B_XXX::BTN_XXX')（v-if 控制按钮显隐）
--
-- 按页面实际操作设计：
--   manage_user  (17) 用户新增/编辑/删除/批量删除
--   manage_role  (18) 角色新增/编辑/删除/批量删除/菜单授权/按钮授权
--   manage_menu  (19) 菜单新增/添加子菜单/编辑/删除/批量删除
-- 其余菜单（首页/功能/异常页/多级菜单/关于/用户详情）无页面级操作按钮，保持 NULL
--
-- 本脚本为 UPDATE，可安全重复执行（幂等）；id 与 route_name 双重校验
-- 注意：覆盖 menu 17 现有的两个测试按钮（B_USER::BTN_ADD/BTN_DELETE 为其子集）
-- ============================================================================

-- 用户管理
UPDATE `sys_menu`
SET `buttons` = '[
  {"code": "B_USER::BTN_ADD", "desc": "新增用户"},
  {"code": "B_USER::BTN_EDIT", "desc": "编辑用户"},
  {"code": "B_USER::BTN_DELETE", "desc": "删除用户"},
  {"code": "B_USER::BTN_BATCH_DELETE", "desc": "批量删除用户"}
]'
WHERE `id` = 17 AND `route_name` = 'manage_user';

-- 角色管理
UPDATE `sys_menu`
SET `buttons` = '[
  {"code": "B_ROLE::BTN_ADD", "desc": "新增角色"},
  {"code": "B_ROLE::BTN_EDIT", "desc": "编辑角色"},
  {"code": "B_ROLE::BTN_DELETE", "desc": "删除角色"},
  {"code": "B_ROLE::BTN_BATCH_DELETE", "desc": "批量删除角色"},
  {"code": "B_ROLE::BTN_MENU_AUTH", "desc": "菜单授权"},
  {"code": "B_ROLE::BTN_BUTTON_AUTH", "desc": "按钮授权"}
]'
WHERE `id` = 18 AND `route_name` = 'manage_role';

-- 菜单管理
UPDATE `sys_menu`
SET `buttons` = '[
  {"code": "B_MENU::BTN_ADD", "desc": "新增菜单"},
  {"code": "B_MENU::BTN_ADD_CHILD", "desc": "添加子菜单"},
  {"code": "B_MENU::BTN_EDIT", "desc": "编辑菜单"},
  {"code": "B_MENU::BTN_DELETE", "desc": "删除菜单"},
  {"code": "B_MENU::BTN_BATCH_DELETE", "desc": "批量删除菜单"}
]'
WHERE `id` = 19 AND `route_name` = 'manage_menu';

-- ============================================================================
-- 执行后验证：
--   SELECT route_name, buttons FROM sys_menu WHERE buttons IS NOT NULL;
--   应返回 3 行（manage_user / manage_role / manage_menu）
--
-- 权限语义提醒：
--   1. 各管理页面目前尚未用 hasAuth() 控制按钮显隐（所有按钮仍可见），
--      本补丁提供的是授权数据；页面接入 v-if="hasAuth('B_USER::BTN_ADD')" 后生效
--   2. 未做过按钮授权的角色 = 默认拥有全部按钮（sys_role_button 无记录全给）
-- ============================================================================
