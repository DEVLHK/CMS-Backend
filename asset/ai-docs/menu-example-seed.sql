-- ============================================================================
-- 示例菜单补充种子脚本（MySQL 5.7）
-- 生成时间: 2026-10-17
-- 来源: src/router/elegant/routes.ts（example 分支合并后的完整路由）+ zh-cn.ts 文案
-- 内容:
--   1. 新增 44 条 sys_menu（alova / function 补齐 / iframe-page / plugin 全部 / pro-naive 全部 / user-center）
--   2. 刷新 16 条存量菜单的 route_props 等（与 routes.ts meta 对齐，parent_id 不动）
--   3. R_SUPER 授予全部新增菜单（KenLin=R_SUPER，登录即可见）
--   4. function_toggle-auth 补充演示按钮码 B_CODE1/2/3
-- 前置: 已执行 db-schema-user-manage.sql + mock-data-seed.sql
-- 幂等: 新增用 INSERT IGNORE（route_name 唯一键兜底），更新/授权可重复执行
-- 注意: exception 组(5/6/7/8, 异常页)与 login 路由保持原状不动
-- ============================================================================

-- ------------------------------------------------------------------
-- 1. 新增菜单
-- ------------------------------------------------------------------
INSERT IGNORE INTO `sys_menu` (`id`,`parent_id`,`menu_type`,`menu_name`,`route_name`,`route_path`,`component`,`icon`,`icon_type`,`route_props`,`buttons`,`status`) VALUES
(22,0,1,'alova示例','alova','/alova','layout.base','carbon:http',1,'{"i18nKey":"route.alova","order":7}',NULL,1),
(23,22,2,'alova请求','alova_request','/alova/request','view.alova_request','',1,'{"i18nKey":"route.alova_request","order":1}',NULL,1),
(24,22,2,'场景化请求','alova_scenes','/alova/scenes','view.alova_scenes','cbi:scene-dynamic',1,'{"i18nKey":"route.alova_scenes","order":3}',NULL,1),
(25,2,1,'隐藏子菜单','function_hide-child','/function/hide-child',NULL,'material-symbols:filter-list-off',1,'{"i18nKey":"route.function_hide-child","order":2}',NULL,1),
(26,25,2,'隐藏子菜单','function_hide-child_one','/function/hide-child/one','view.function_hide-child_one','material-symbols:filter-list-off',1,'{"i18nKey":"route.function_hide-child_one","hideInMenu":true,"activeMenu":"function_hide-child"}',NULL,1),
(27,25,2,'菜单三','function_hide-child_three','/function/hide-child/three','view.function_hide-child_three','',1,'{"i18nKey":"route.function_hide-child_three","hideInMenu":true,"activeMenu":"function_hide-child"}',NULL,1),
(28,25,2,'菜单二','function_hide-child_two','/function/hide-child/two','view.function_hide-child_two','',1,'{"i18nKey":"route.function_hide-child_two","hideInMenu":true,"activeMenu":"function_hide-child"}',NULL,1),
(29,2,2,'请求','function_request','/function/request','view.function_request','carbon:network-overlay',1,'{"i18nKey":"route.function_request","order":3}',NULL,1),
(30,2,2,'超级管理员可见','function_super-page','/function/super-page','view.function_super-page','ic:round-supervisor-account',1,'{"i18nKey":"route.function_super-page","order":5}',NULL,1),
(31,2,2,'切换权限','function_toggle-auth','/function/toggle-auth','view.function_toggle-auth','ic:round-construction',1,'{"i18nKey":"route.function_toggle-auth","order":4}',NULL,1),
(32,0,2,'外链页面','iframe-page','/iframe-page/:url','layout.base$view.iframe-page','',1,'{"i18nKey":"route.iframe-page","keepAlive":true,"hideInMenu":true}',NULL,1),
(33,0,1,'插件示例','plugin','/plugin','layout.base','clarity:plugin-line',1,'{"i18nKey":"route.plugin","order":7}',NULL,1),
(34,33,2,'条形码','plugin_barcode','/plugin/barcode','view.plugin_barcode','ic:round-barcode',1,'{"i18nKey":"route.plugin_barcode"}',NULL,1),
(35,33,1,'图表','plugin_charts','/plugin/charts',NULL,'mdi:chart-areaspline',1,'{"i18nKey":"route.plugin_charts"}',NULL,1),
(36,35,2,'AntV','plugin_charts_antv','/plugin/charts/antv','view.plugin_charts_antv','hugeicons:flow-square',1,'{"i18nKey":"route.plugin_charts_antv"}',NULL,1),
(37,35,2,'ECharts','plugin_charts_echarts','/plugin/charts/echarts','view.plugin_charts_echarts','simple-icons:apacheecharts',1,'{"i18nKey":"route.plugin_charts_echarts"}',NULL,1),
(38,35,2,'VChart','plugin_charts_vchart','/plugin/charts/vchart','view.plugin_charts_vchart','visactor',2,'{"i18nKey":"route.plugin_charts_vchart"}',NULL,1),
(39,33,2,'剪贴板','plugin_copy','/plugin/copy','view.plugin_copy','mdi:clipboard-outline',1,'{"i18nKey":"route.plugin_copy"}',NULL,1),
(40,33,1,'编辑器','plugin_editor','/plugin/editor',NULL,'icon-park-outline:editor',1,'{"i18nKey":"route.plugin_editor"}',NULL,1),
(41,40,2,'MD 编辑器','plugin_editor_markdown','/plugin/editor/markdown','view.plugin_editor_markdown','ri:markdown-line',1,'{"i18nKey":"route.plugin_editor_markdown"}',NULL,1),
(42,40,2,'富文本编辑器','plugin_editor_quill','/plugin/editor/quill','view.plugin_editor_quill','mdi:file-document-edit-outline',1,'{"i18nKey":"route.plugin_editor_quill"}',NULL,1),
(43,33,2,'Excel','plugin_excel','/plugin/excel','view.plugin_excel','ri:file-excel-2-line',1,'{"i18nKey":"route.plugin_excel","keepAlive":true}',NULL,1),
(44,33,1,'甘特图','plugin_gantt','/plugin/gantt',NULL,'ant-design:bar-chart-outlined',1,'{"i18nKey":"route.plugin_gantt"}',NULL,1),
(45,44,2,'dhtmlxGantt','plugin_gantt_dhtmlx','/plugin/gantt/dhtmlx','view.plugin_gantt_dhtmlx','',1,'{"i18nKey":"route.plugin_gantt_dhtmlx"}',NULL,1),
(46,44,2,'VTableGantt','plugin_gantt_vtable','/plugin/gantt/vtable','view.plugin_gantt_vtable','visactor',2,'{"i18nKey":"route.plugin_gantt_vtable"}',NULL,1),
(47,33,2,'图标','plugin_icon','/plugin/icon','view.plugin_icon','custom-icon',2,'{"i18nKey":"route.plugin_icon"}',NULL,1),
(48,33,2,'地图','plugin_map','/plugin/map','view.plugin_map','mdi:map',1,'{"i18nKey":"route.plugin_map"}',NULL,1),
(49,33,2,'PDF 预览','plugin_pdf','/plugin/pdf','view.plugin_pdf','uiw:file-pdf',1,'{"i18nKey":"route.plugin_pdf"}',NULL,1),
(50,33,2,'拼音','plugin_pinyin','/plugin/pinyin','view.plugin_pinyin','entypo-social:google-hangouts',1,'{"i18nKey":"route.plugin_pinyin"}',NULL,1),
(51,33,2,'打印','plugin_print','/plugin/print','view.plugin_print','mdi:printer',1,'{"i18nKey":"route.plugin_print"}',NULL,1);

INSERT IGNORE INTO `sys_menu` (`id`,`parent_id`,`menu_type`,`menu_name`,`route_name`,`route_path`,`component`,`icon`,`icon_type`,`route_props`,`buttons`,`status`) VALUES
(52,33,2,'Swiper','plugin_swiper','/plugin/swiper','view.plugin_swiper','simple-icons:swiper',1,'{"i18nKey":"route.plugin_swiper"}',NULL,1),
(53,33,1,'表格','plugin_tables','/plugin/tables',NULL,'icon-park-outline:table',1,'{"i18nKey":"route.plugin_tables"}',NULL,1),
(54,53,2,'VTable','plugin_tables_vtable','/plugin/tables/vtable','view.plugin_tables_vtable','visactor',2,'{"i18nKey":"route.plugin_tables_vtable"}',NULL,1),
(55,33,2,'打字机','plugin_typeit','/plugin/typeit','view.plugin_typeit','mdi:typewriter',1,'{"i18nKey":"route.plugin_typeit"}',NULL,1),
(56,33,2,'视频','plugin_video','/plugin/video','view.plugin_video','mdi:video',1,'{"i18nKey":"route.plugin_video"}',NULL,1),
(57,0,1,'Pro Naive UI 示例','pro-naive','/pro-naive','layout.base','material-symbols-light:demography-outline-rounded',1,'{"i18nKey":"route.pro-naive","order":7}',NULL,1),
(58,57,1,'表单','pro-naive_form','/pro-naive/form',NULL,'fluent:form-28-regular',1,'{"i18nKey":"route.pro-naive_form"}',NULL,1),
(59,58,2,'基础表单','pro-naive_form_basic','/pro-naive/form/basic','view.pro-naive_form_basic','',1,'{"i18nKey":"route.pro-naive_form_basic"}',NULL,1),
(60,58,2,'查询表单','pro-naive_form_query','/pro-naive/form/query','view.pro-naive_form_query','',1,'{"i18nKey":"route.pro-naive_form_query"}',NULL,1),
(61,58,2,'分步表单','pro-naive_form_step','/pro-naive/form/step','view.pro-naive_form_step','',1,'{"i18nKey":"route.pro-naive_form_step"}',NULL,1),
(62,57,1,'表格','pro-naive_table','/pro-naive/table',NULL,'mynaui:table',1,'{"i18nKey":"route.pro-naive_table"}',NULL,1),
(63,62,2,'远程加载','pro-naive_table_remote','/pro-naive/table/remote','view.pro-naive_table_remote','',1,'{"i18nKey":"route.pro-naive_table_remote"}',NULL,1),
(64,62,2,'行编辑','pro-naive_table_row-edit','/pro-naive/table/row-edit','view.pro-naive_table_row-edit','',1,'{"i18nKey":"route.pro-naive_table_row-edit"}',NULL,1),
(65,0,2,'个人中心','user-center','/user-center','layout.base$view.user-center','',1,'{"i18nKey":"route.user-center","hideInMenu":true}',NULL,1);

-- ------------------------------------------------------------------
-- 2. 刷新存量菜单 meta（icon / route_props 与 routes.ts 对齐）
-- ------------------------------------------------------------------
UPDATE `sys_menu` SET `menu_name`='关于',`component`='layout.base$view.about',`icon`='fluent:book-information-24-regular',`icon_type`=1,`route_props`='{"i18nKey":"route.about","order":10}' WHERE `id`=21;
UPDATE `sys_menu` SET `menu_name`='功能',`component`='layout.base',`icon`='icon-park-outline:all-application',`icon_type`=1,`route_props`='{"i18nKey":"route.function","order":6}' WHERE `id`=2;
UPDATE `sys_menu` SET `menu_name`='多标签页',`component`='view.function_multi-tab',`icon`='ic:round-tab',`icon_type`=1,`route_props`='{"i18nKey":"route.function_multi-tab","hideInMenu":true,"activeMenu":"function_tab","multiTab":true}' WHERE `id`=3;
UPDATE `sys_menu` SET `menu_name`='标签页',`component`='view.function_tab',`icon`='ic:round-tab',`icon_type`=1,`route_props`='{"i18nKey":"route.function_tab","order":1}' WHERE `id`=4;
UPDATE `sys_menu` SET `menu_name`='首页',`component`='layout.base$view.home',`icon`='mdi:monitor-dashboard',`icon_type`=1,`route_props`='{"i18nKey":"route.home","order":1}' WHERE `id`=1;
UPDATE `sys_menu` SET `menu_name`='系统管理',`component`='layout.base',`icon`='carbon:cloud-service-management',`icon_type`=1,`route_props`='{"i18nKey":"route.manage","order":9}' WHERE `id`=16;
UPDATE `sys_menu` SET `menu_name`='菜单管理',`component`='view.manage_menu',`icon`='material-symbols:route',`icon_type`=1,`route_props`='{"i18nKey":"route.manage_menu","order":3,"keepAlive":true}' WHERE `id`=19;
UPDATE `sys_menu` SET `menu_name`='角色管理',`component`='view.manage_role',`icon`='carbon:user-role',`icon_type`=1,`route_props`='{"i18nKey":"route.manage_role","order":2}' WHERE `id`=18;
UPDATE `sys_menu` SET `menu_name`='用户管理',`component`='view.manage_user',`icon`='ic:round-manage-accounts',`icon_type`=1,`route_props`='{"i18nKey":"route.manage_user","order":1}' WHERE `id`=17;
UPDATE `sys_menu` SET `menu_name`='用户详情',`component`='view.manage_user-detail',`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.manage_user-detail","hideInMenu":true,"activeMenu":"manage_user"}' WHERE `id`=20;
UPDATE `sys_menu` SET `menu_name`='多级菜单',`component`='layout.base',`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.multi-menu","order":8}' WHERE `id`=9;
UPDATE `sys_menu` SET `menu_name`='一级子菜单1',`component`=NULL,`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.multi-menu_first","order":1}' WHERE `id`=10;
UPDATE `sys_menu` SET `menu_name`='二级子菜单',`component`='view.multi-menu_first_child',`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.multi-menu_first_child"}' WHERE `id`=11;
UPDATE `sys_menu` SET `menu_name`='一级子菜单2',`component`=NULL,`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.multi-menu_second","order":2}' WHERE `id`=12;
UPDATE `sys_menu` SET `menu_name`='二级子菜单2',`component`=NULL,`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.multi-menu_second_child"}' WHERE `id`=14;
UPDATE `sys_menu` SET `menu_name`='三级菜单',`component`='view.multi-menu_second_child_home',`icon`='',`icon_type`=1,`route_props`='{"i18nKey":"route.multi-menu_second_child_home"}' WHERE `id`=15;

-- ------------------------------------------------------------------
-- 3. R_SUPER 授予全部新增菜单（幂等）
-- ------------------------------------------------------------------
INSERT IGNORE INTO `sys_role_menu` (`role_id`,`menu_id`)
SELECT r.`id`, m.`id` FROM `sys_role` r JOIN `sys_menu` m ON m.`id` IN (22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65)
WHERE r.`role_code` = 'R_SUPER';

-- ------------------------------------------------------------------
-- 4. 切换权限示例页按钮码
-- ------------------------------------------------------------------
UPDATE `sys_menu` SET `buttons` = '[{"code": "B_CODE1", "desc": "超管可见按钮"}, {"code": "B_CODE2", "desc": "管理员可见按钮"}, {"code": "B_CODE3", "desc": "第三个演示按钮"}]'
WHERE `id` = 31 AND `route_name` = 'function_toggle-auth';

-- ------------------------------------------------------------------
-- 5. 文档菜单组（来自 src/router/routes/index.ts 的 customRoutes，共 11 条，id 66-76）
--    子项均为 iframe 内嵌页（route_props.props.url）或外链（route_props.href）
-- ------------------------------------------------------------------
INSERT IGNORE INTO `sys_menu` (`id`,`parent_id`,`menu_type`,`menu_name`,`route_name`,`route_path`,`component`,`icon`,`icon_type`,`route_props`,`buttons`,`status`) VALUES
(66,0,1,'文档','document','/document','layout.base','mdi:file-document-multiple-outline',1,'{"i18nKey":"route.document","order":2}',NULL,1),
(67,66,2,'Ant Design Vue文档','document_antd','/document/antd','view.iframe-page','logos:ant-design',1,'{"i18nKey":"route.document_antd","order":7,"props":{"url":"https://antdv.com/components/overview-cn"}}',NULL,1),
(68,66,2,'Naive UI文档','document_naive','/document/naive','view.iframe-page','logos:naiveui',1,'{"i18nKey":"route.document_naive","order":6,"props":{"url":"https://www.naiveui.com/zh-CN/os-theme/docs/introduction"}}',NULL,1),
(69,66,2,'Pro Naive UI文档','document_pro-naive','/document/pro-naive','view.iframe-page','logos:naiveui',1,'{"i18nKey":"route.document_pro-naive","order":6,"props":{"url":"https://naive-ui.pro-components.cn/"}}',NULL,1),
(70,66,2,'Alova文档','document_alova','/document/alova','view.iframe-page','alova',2,'{"i18nKey":"route.document_alova","order":7,"props":{"url":"https://alova.js.org"}}',NULL,1),
(71,66,2,'项目文档','document_project','/document/project','view.iframe-page','logo',2,'{"i18nKey":"route.document_project","order":1,"props":{"url":"https://docs.soybeanjs.cn/zh"}}',NULL,1),
(72,66,2,'项目文档(外链)','document_project-link','/document/project-link','view.iframe-page','logo',2,'{"i18nKey":"route.document_project-link","order":2,"href":"https://docs.soybeanjs.cn/zh"}',NULL,1),
(73,66,2,'视频教程','document_video','/document/video','view.iframe-page','logo',2,'{"i18nKey":"route.document_video","order":2,"href":"https://www.bilibili.com/video/BV1YKdRYXELC"}',NULL,1),
(74,66,2,'UnoCSS文档','document_unocss','/document/unocss','view.iframe-page','logos:unocss',1,'{"i18nKey":"route.document_unocss","order":5,"props":{"url":"https://unocss.dev/"}}',NULL,1),
(75,66,2,'Vite文档','document_vite','/document/vite','view.iframe-page','logos:vitejs',1,'{"i18nKey":"route.document_vite","order":4,"props":{"url":"https://cn.vitejs.dev/"}}',NULL,1),
(76,66,2,'Vue文档','document_vue','/document/vue','view.iframe-page','logos:vue',1,'{"i18nKey":"route.document_vue","order":3,"props":{"url":"https://cn.vuejs.org/"}}',NULL,1);

INSERT IGNORE INTO `sys_role_menu` (`role_id`,`menu_id`)
SELECT r.`id`, m.`id` FROM `sys_role` r JOIN `sys_menu` m ON m.`id` IN (66,67,68,69,70,71,72,73,74,75,76)
WHERE r.`role_code` = 'R_SUPER';

-- 执行后验证：
--   1) KenLin 重新登录，应出现 文档/alova/插件示例/Pro Naive UI 示例等菜单组
--   2) 文档组子项：内嵌项（项目文档/Vue文档等）iframe 正常加载；外链项（项目文档(外链)/视频教程）点击新开标签页
--   3) 菜单管理页应能看到全部菜单树（含隐藏菜单 iframe-page/user-center）
--   4) 角色"菜单权限"树同步出现新菜单，可授权给普通角色
--   5) SELECT COUNT(*) FROM sys_menu;  -- 应为 75
