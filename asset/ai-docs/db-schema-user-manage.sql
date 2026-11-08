-- ============================================================================
-- 用户管理模块数据库结构（MySQL 5.7, InnoDB, utf8mb4）
-- 与 Soybean Admin 前端契约对齐：
--   Api.SystemManage.User   → sys_user + sys_user_role + sys_role
--   Api.SystemManage.Role   → sys_role
--   Api.SystemManage.Menu   → sys_menu（含 buttons JSON）
--   Api.Auth.UserInfo       → 登录时由 sys_user/sys_role/sys_menu 汇总
--
-- 字段命名：库内 snake_case，API 输出 camelCase（Pydantic to_camel 别名转换）
-- id 为 BIGINT，API 层按前端类型输出：User.id -> number, UserInfo.userId -> string
-- status / userGender 库内 TINYINT，API 层序列化为字符串 '1'/'2'（前端是字符串字面量类型）
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. 用户表
-- ----------------------------------------------------------------------------
CREATE TABLE `sys_user` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `user_name`   VARCHAR(30)  NOT NULL                COMMENT '用户名（登录账号，唯一）',
  `password`    VARCHAR(100) NOT NULL                COMMENT '密码哈希（bcrypt，永不返回给前端）',
  `user_gender` TINYINT      NULL DEFAULT NULL       COMMENT '性别 1:男 2:女 NULL:未设置',
  `nick_name`   VARCHAR(30)  NOT NULL DEFAULT ''     COMMENT '昵称',
  `user_phone`  VARCHAR(20)  NULL DEFAULT NULL       COMMENT '手机号（空须存 NULL 而不是空串，否则唯一索引冲突）',
  `user_email`  VARCHAR(100) NULL DEFAULT NULL       COMMENT '邮箱（同上）',
  `status`      TINYINT      NOT NULL DEFAULT 1      COMMENT '状态 1:启用 2:禁用（登录时校验）',
  `create_by`   VARCHAR(30)  NOT NULL DEFAULT ''     COMMENT '创建人',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by`   VARCHAR(30)  NOT NULL DEFAULT ''     COMMENT '更新人',
  `update_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_name`  (`user_name`),
  UNIQUE KEY `uk_user_phone` (`user_phone`),
  UNIQUE KEY `uk_user_email` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户表';

-- ----------------------------------------------------------------------------
-- 2. 角色表
-- ----------------------------------------------------------------------------
CREATE TABLE `sys_role` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `role_name`   VARCHAR(30)  NOT NULL                COMMENT '角色名称',
  `role_code`   VARCHAR(50)  NOT NULL                COMMENT '角色编码（如 R_SUPER，前端 userRoles 存的就是它）',
  `role_desc`   VARCHAR(255) NOT NULL DEFAULT ''     COMMENT '角色描述',
  `status`      TINYINT      NOT NULL DEFAULT 1      COMMENT '状态 1:启用 2:禁用',
  `create_by`   VARCHAR(30)  NOT NULL DEFAULT '',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by`   VARCHAR(30)  NOT NULL DEFAULT '',
  `update_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色表';

-- ----------------------------------------------------------------------------
-- 3. 用户-角色关联表
--    前端编辑用户抽屉提交 userRoles: string[]（roleCode 数组），
--    后端先按 role_code 查 id，再整表替换该用户的关联记录（先删后插，事务内）
-- ----------------------------------------------------------------------------
CREATE TABLE `sys_user_role` (
  `user_id`     BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `role_id`     BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `role_id`),
  KEY `idx_role_id` (`role_id`),
  CONSTRAINT `fk_user_role_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_role_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户角色关联表';

-- ----------------------------------------------------------------------------
-- 4. 菜单表（菜单管理模块 + 动态路由 + 按钮权限码来源）
--    buttons 直接存 JSON 数组，与前端 Api.SystemManage.MenuButton[] 形状一致：
--      [{"code": "B_USER::BTN_ADD", "desc": "新增用户"}]
--    route_props 存路由元信息 JSON，与前端 MenuPropsOfRoute 对齐：
--      {"i18nKey": null, "keepAlive": true, "order": 1, "href": null,
--       "hideInMenu": false, "activeMenu": null, "multiTab": false,
--       "fixedIndexInTab": null, "query": null}
-- ----------------------------------------------------------------------------
CREATE TABLE `sys_menu` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '菜单ID',
  `parent_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0     COMMENT '父菜单ID，0=顶级',
  `menu_type`   TINYINT      NOT NULL DEFAULT 2        COMMENT '类型 1:目录 2:菜单',
  `menu_name`   VARCHAR(50)  NOT NULL                  COMMENT '菜单名称',
  `route_name`  VARCHAR(100) NOT NULL                  COMMENT '路由名称（前端 routeName，唯一）',
  `route_path`  VARCHAR(200) NOT NULL                  COMMENT '路由路径',
  `component`   VARCHAR(255) NULL DEFAULT NULL         COMMENT '组件路径（目录为 NULL）',
  `icon`        VARCHAR(100) NOT NULL DEFAULT ''       COMMENT '图标名',
  `icon_type`   TINYINT      NOT NULL DEFAULT 1        COMMENT '图标类型 1:iconify 2:本地',
  `route_props` JSON         NULL                      COMMENT '路由元信息（对应前端 MenuPropsOfRoute）',
  `buttons`     JSON         NULL                      COMMENT '按钮权限码 [{code,desc}]',
  `status`      TINYINT      NOT NULL DEFAULT 1        COMMENT '状态 1:启用 2:禁用',
  `create_by`   VARCHAR(30)  NOT NULL DEFAULT '',
  `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by`   VARCHAR(30)  NOT NULL DEFAULT '',
  `update_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_route_name` (`route_name`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='菜单表';

-- ----------------------------------------------------------------------------
-- 5. 角色-菜单关联表（决定角色能看到哪些菜单/按钮）
-- ----------------------------------------------------------------------------
CREATE TABLE `sys_role_menu` (
  `role_id`     BIGINT UNSIGNED NOT NULL,
  `menu_id`     BIGINT UNSIGNED NOT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`, `menu_id`),
  KEY `idx_menu_id` (`menu_id`),
  CONSTRAINT `fk_role_menu_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_role_menu_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色菜单关联表';

-- ----------------------------------------------------------------------------
-- 6. 刷新令牌表（可选）
--    若 /auth/refreshToken 使用 JWT 且无需服务端吊销，可省略本表。
--    保留则支持：登出吊销、refreshToken 轮换后旧 token 失效、强制下线。
--    存哈希（SHA-256）而非原 token，泄露库不泄露凭证。
-- ----------------------------------------------------------------------------
CREATE TABLE `sys_refresh_token` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`     BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `token_hash`  CHAR(64)  NOT NULL COMMENT 'refreshToken 的 SHA-256 十六进制哈希',
  `expires_at`  DATETIME  NOT NULL COMMENT '过期时间',
  `revoked`     TINYINT   NOT NULL DEFAULT 0 COMMENT '是否已吊销 0:否 1:是',
  `create_time` DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_token_hash` (`token_hash`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_refresh_token_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='刷新令牌表';

-- ============================================================================
-- 初始化数据
-- ============================================================================

-- 超级管理员角色（前端 .env: VITE_STATIC_SUPER_ROLE=R_SUPER）
INSERT INTO `sys_role` (`role_name`, `role_code`, `role_desc`, `create_by`)
VALUES ('超级管理员', 'R_SUPER', '拥有全部权限', 'system');

-- 内置管理员（密码哈希为占位，部署前用 bcrypt 生成后替换，例如：
--   python3 -c "import bcrypt;print(bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode())"
-- ）
INSERT INTO `sys_user` (`user_name`, `password`, `nick_name`, `status`, `create_by`)
VALUES ('SuperAdmin', '$2b$12$REPLACE_WITH_REAL_BCRYPT_HASH', 'Soybean', 1, 'system');

INSERT INTO `sys_user_role` (`user_id`, `role_id`)
SELECT u.`id`, r.`id` FROM `sys_user` u, `sys_role` r
WHERE u.`user_name` = 'SuperAdmin' AND r.`role_code` = 'R_SUPER';

-- ============================================================================
-- 前端接口 <-> 表 的对应关系与实现要点
-- ============================================================================
--
-- GET /systemManage/getUserList   → sys_user 分页 + LEFT JOIN sys_user_role/sys_role
--                                   汇总 userRoles（GROUP_CONCAT(role_code) 后 split），
--                                   搜索条件：userName/nickName 模糊、userGender、
--                                   userPhone/userEmail 精确、status 精确
-- GET /systemManage/getAllRoles   → sys_role WHERE status=1（仅启用角色，供下拉）
-- GET /systemManage/getRoleList   → sys_role 分页
-- GET /systemManage/getMenuList/v2、/getMenuTree → sys_menu 组树（parentId 递归）
--
-- /auth/login                     → sys_user(user_name + password + status=1 校验)
-- /auth/getUserInfo               → userId=str(id)、userName、
--                                   roles=用户全部启用角色的 role_code，
--                                   buttons=这些角色关联菜单的 buttons JSON 展开去重；
--                                   R_SUPER 用户可直接返回全量按钮码（超管短路）
--
-- 事务边界：编辑用户角色（删旧关联+插新关联）、删除角色（有关联用户时 RESTRICT 拒绝）
-- 前端空字符串处理：userPhone/userEmail 提交 '' 时后端转 NULL 再入库（唯一索引约束）
