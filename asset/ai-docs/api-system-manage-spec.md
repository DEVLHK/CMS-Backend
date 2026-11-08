# 用户 / 角色 / 菜单管理接口规范（systemManage 模块）

> 供后端（FastAPI, MySQL 5.7）实现用户管理模块的增删改查接口。
> 数据库结构见 `db-schema-user-manage.sql`（sys_user / sys_role / sys_user_role / sys_menu / sys_role_menu）。
> 所有格式与 Soybean Admin 前端类型 `Api.SystemManage.*`（src/typings/api/system-manage.d.ts）逐字段对齐。
> 通用信封与错误码约定同 `api-login-spec.md`：`{code, msg, data}`，成功码 `"0000"`，业务错误返回 HTTP 200。

---

## 0. 通用约定

- 认证：除标注外均需 Header `Authorization: Bearer <token>`
- 命名：JSON 字段 camelCase；`id` 输出 number；`status`/`userGender`/`menuType`/`iconType` 输出**字符串** `'1'/'2'`（前端为字符串字面量联合类型）
- 时间：`createTime`/`updateTime` 输出 `"YYYY-MM-DD HH:mm:ss"` 字符串
- 分页响应结构（`PaginatingQueryRecord`）：

```json
{ "records": [], "current": 1, "size": 10, "total": 100 }
```

- 建议错误码（均为业务错误，HTTP 200 + `code` + `msg`，`data: null`）：

| code  | 场景                     | msg 示例                                   |
| ----- | ------------------------ | ------------------------------------------ |
| E1001 | 用户名已存在             | 用户名 {userName} 已存在                   |
| E1002 | 手机号/邮箱已被占用      | 手机号已被使用                             |
| E1003 | 角色编码已存在           | 角色编码 {roleCode} 已存在                 |
| E1004 | 角色已分配用户，禁止删除 | 该角色已分配用户，请先移除用户身上的该角色 |
| E1005 | 路由名已存在             | 路由名称 {routeName} 已存在                |
| E1006 | 存在子菜单，禁止删除     | 请先删除子菜单                             |

- 路由注册统一 `tags=["systemManage"]`，operationId 用驼峰（如 `userAdd`）

---

## 1. 用户接口

### 1.1 GET /systemManage/getUserList（分页查询）

Query 参数（全部可空，空则不过滤）：

| 参数       | 类型    | 说明              |
| ---------- | ------- | ----------------- |
| current    | number  | 页码，默认 1      |
| size       | number  | 每页条数，默认 10 |
| userName   | string  | 模糊匹配          |
| nickName   | string  | 模糊匹配          |
| userGender | '1'/'2' | 精确              |
| userPhone  | string  | 精确              |
| userEmail  | string  | 精确              |
| status     | '1'/'2' | 精确              |

响应 `data`：

```json
{
  "records": [
    {
      "id": 1,
      "userName": "SuperAdmin",
      "userGender": "1",
      "nickName": "Soybean",
      "userPhone": "13800138000",
      "userEmail": "soybean@example.com",
      "userRoles": ["R_SUPER"],
      "status": "1",
      "createBy": "system",
      "createTime": "2026-10-17 10:00:00",
      "updateBy": "system",
      "updateTime": "2026-10-17 10:00:00"
    }
  ],
  "current": 1,
  "size": 10,
  "total": 1
}
```

实现：`sys_user` 分页 + `sys_user_role`/`sys_role` 汇总 `userRoles`（`GROUP_CONCAT(role_code)` 后 split），`user_gender`/`user_phone`/`user_email` 为 NULL 时输出 `null`（前端渲染 null 不显示标签）。

### 1.2 POST /systemManage/addUser（新增用户）

请求（`password` 必填，明文传输依赖 HTTPS，入库前 bcrypt）：

```json
{
  "userName": "zhangsan",
  "password": "123456",
  "userGender": "1",
  "nickName": "张三",
  "userPhone": "13800138000",
  "userEmail": "zhangsan@example.com",
  "userRoles": ["R_USER"],
  "status": "1"
}
```

响应：`{"code": "0000", "msg": "", "data": null}`

实现要点：

- 校验 userName 唯一（E1001）、phone/email 唯一（E1002）；**空字符串 phone/email 转 NULL 入库**
- `userRoles` 为 roleCode 数组：事务内插 `sys_user` → 按 role_code 查 id → 批量插 `sys_user_role`；不存在的 roleCode 直接忽略或报错（建议报错，E0001 风格）

### 1.3 POST /systemManage/updateUser（编辑用户）

请求（**不含 password**；`id` 必填； userName 通常不允许改，若改需重新校验唯一）：

```json
{
  "id": 2,
  "userName": "zhangsan",
  "userGender": "2",
  "nickName": "张三丰",
  "userPhone": null,
  "userEmail": "zsf@example.com",
  "userRoles": ["R_USER", "R_AUDIT"],
  "status": "1"
}
```

响应：`data: null`。实现：事务内更新 `sys_user` + **先删后插** 该用户的 `sys_user_role`。

### 1.4 POST /systemManage/deleteUser（删除单个）

请求：`{ "id": 2 }` → 响应 `data: null`
`sys_user_role`/`sys_refresh_token` 由外键 CASCADE 自动清理；建议同时吊销该用户 token（登出）。

### 1.5 POST /systemManage/batchDeleteUser（批量删除）

请求：`{ "ids": [2, 3, 4] }` → 响应 `data: null`

---

## 2. 角色接口

### 2.1 GET /systemManage/getRoleList（分页查询）

Query：`current`、`size`、`roleName`（模糊）、`roleCode`（模糊）、`status`（精确），均可空。

响应 `data.records[]`：

```json
{
  "id": 1,
  "roleName": "超级管理员",
  "roleCode": "R_SUPER",
  "roleDesc": "拥有全部权限",
  "status": "1",
  "createBy": "system",
  "createTime": "2026-10-17 10:00:00",
  "updateBy": "system",
  "updateTime": "2026-10-17 10:00:00"
}
```

### 2.2 GET /systemManage/getAllRoles（全部启用角色，下拉用）

无参数。响应 `data`：

```json
[{ "id": 1, "roleName": "超级管理员", "roleCode": "R_SUPER" }]
```

只返回 `status=1` 的角色。

### 2.3 POST /systemManage/addRole

```json
{ "roleName": "审计员", "roleCode": "R_AUDIT", "roleDesc": "只读审计", "status": "1" }
```

roleCode 唯一（E1003）。

### 2.4 POST /systemManage/updateRole

```json
{ "id": 2, "roleName": "审计员", "roleCode": "R_AUDIT", "roleDesc": "只读审计+导出", "status": "1" }
```

roleCode 修改需校验与其他角色不冲突；R_SUPER 为内置超管角色，建议禁止修改/删除。

### 2.5 POST /systemManage/deleteRole

请求：`{ "id": 2 }`
若 `sys_user_role` 中仍有引用 → E1004（外键 RESTRICT，捕获后转友好提示）。

### 2.6 POST /systemManage/batchDeleteRole

请求：`{ "ids": [2, 3] }`，删除前逐个校验 E1004。

---

## 3. 菜单接口

### 3.1 GET /systemManage/getMenuList/v2（菜单管理表格）

Query：`current`/`size` 可选（不传则返回全量，`total = records.length`）。
响应 `data.records[]`（**路由属性拍平在前端 Menu 对象上**，库内 `route_props`/`buttons` JSON 由后端解包）：

```json
{
  "id": 1,
  "parentId": 0,
  "menuType": "2",
  "menuName": "系统管理",
  "routeName": "manage",
  "routePath": "/manage",
  "component": "layout.base$view.manage",
  "icon": "mdi:manage-accounts",
  "iconType": "1",
  "buttons": [{ "code": "B_USER::BTN_ADD", "desc": "新增用户" }],
  "i18nKey": "route.manage",
  "keepAlive": false,
  "constant": false,
  "order": 3,
  "href": null,
  "hideInMenu": false,
  "activeMenu": null,
  "multiTab": false,
  "fixedIndexInTab": null,
  "query": null,
  "status": "1",
  "createBy": "system",
  "createTime": "2026-10-17 10:00:00",
  "updateBy": "system",
  "updateTime": "2026-10-17 10:00:00"
}
```

records 按 `parent_id` + `order` 排序返回平铺列表（前端表格自行组树），或直接返回树（前端两者兼容，建议平铺+排序）。

### 3.2 GET /systemManage/getAllPages（全部页面路由名）

无参数。响应 `data`：`["home", "manage", "manage_user", "manage_role"]`
实现：`SELECT DISTINCT route_name FROM sys_menu WHERE menu_type = '2' AND status = '1'`。

### 3.3 GET /systemManage/getMenuTree（菜单树，授权弹窗用）

无参数。响应 `data`：

```json
[
  {
    "id": 1,
    "label": "系统管理",
    "pId": 0,
    "children": [{ "id": 2, "label": "用户管理", "pId": 1, "children": null }]
  }
]
```

字段名必须是 `label`/`pId`（前端 MenuTree 类型），`label` 取 `menu_name`；仅返回 `status=1`。

### 3.4 POST /systemManage/addMenu

请求（结构同 3.1 单条记录，去掉 `id`/审计字段）：

```json
{
  "parentId": 0,
  "menuType": "2",
  "menuName": "用户管理",
  "routeName": "manage_user",
  "routePath": "/manage/user",
  "component": "layout.base$view.manage_user",
  "icon": "mdi:account",
  "iconType": "1",
  "buttons": [{ "code": "B_USER::BTN_ADD", "desc": "新增用户" }],
  "i18nKey": "route.manage_user",
  "keepAlive": false,
  "constant": false,
  "order": 1,
  "href": null,
  "hideInMenu": false,
  "activeMenu": null,
  "multiTab": false,
  "fixedIndexInTab": null,
  "query": null,
  "status": "1"
}
```

`routeName` 唯一（E1005）；后端把 `i18nKey/keepAlive/order/href/hideInMenu/activeMenu/multiTab/fixedIndexInTab/query` 打包进 `route_props` JSON，`buttons` 直接入 `buttons` JSON。

### 3.5 POST /systemManage/updateMenu

同 3.4 加 `id`。`routeName` 变更需重查唯一。

### 3.6 POST /systemManage/deleteMenu（删除菜单）

请求：`{ "id": 5 }`
存在子菜单（`parent_id = id` 有记录）→ E1006；`sys_role_menu` 授权记录随外键 CASCADE 删除。

---

## 4. 角色菜单授权（角色页"菜单授权"弹窗）

> 需先给 `sys_role` 加一列存角色首页：
> `ALTER TABLE sys_role ADD COLUMN home VARCHAR(100) NOT NULL DEFAULT 'home' COMMENT '角色首页路由名';`

### 4.1 GET /systemManage/getRoleMenuAuth?roleId=1（回显）

响应 `data`：

```json
{ "home": "home", "menuIds": [1, 2, 3, 4, 5] }
```

- `menuIds`：该角色在 `sys_role_menu` 的全部 menu_id（含目录节点）
- `home`：sys_role.home

### 4.2 POST /systemManage/updateRoleMenuAuth（保存）

```json
{ "roleId": 2, "home": "manage_user", "menuIds": [1, 2, 3] }
```

事务：更新 `sys_role.home` + 先删后插 `sys_role_menu`。响应 `data: null`。
注意：前端 NTree 提交的勾选项可能不含父节点，后端需把 `menuIds` 中每个节点的祖先链补全后再入库（否则目录不显示）。

---

## 5. 与登录链路的衔接

- `/auth/getUserInfo` 的 `roles` = 用户全部启用角色的 roleCode；`buttons` = 这些角色经 `sys_role_menu` 关联菜单的 `buttons` JSON 展开去重；**R_SUPER 用户直接返回全量按钮码**（超管短路）
- 动态路由模式（`VITE_AUTH_ROUTE_MODE=dynamic`）时 `/route/getUserRoutes` 也从 `sys_role_menu` 组树；当前项目是 static 模式，优先级低

## 6. 前端配套改动清单（后端就绪后）

`src/service/api/system-manage.ts` 中需新增函数并全部由 `mockRequest` 切回 `request`：
`fetchAddUser`、`fetchUpdateUser`、`fetchDeleteUser`、`fetchBatchDeleteUser`、`fetchAddRole`、`fetchUpdateRole`、`fetchDeleteRole`、`fetchBatchDeleteRole`、`fetchAddMenu`、`fetchUpdateMenu`、`fetchDeleteMenu`、`fetchGetRoleMenuAuth`、`fetchUpdateRoleMenuAuth`；
并在 `user-operate-drawer.vue` / `role-operate-drawer.vue` / `menu-operate-modal.vue` / `menu-auth-modal.vue` 的 `// request` 占位处接入。

## 7. 验收用例（用户/角色/菜单）

| 场景                                 | 预期                                                    |
| ------------------------------------ | ------------------------------------------------------- |
| getUserList 无条件                   | 分页结构，userRoles 聚合为数组                          |
| getUserList userName=张              | 模糊命中                                                |
| addUser 重复 userName                | E1001，不入库                                           |
| addUser userRoles 含不存在编码       | 报错回滚                                                |
| updateUser 改角色                    | sys_user_role 整体替换                                  |
| deleteUser                           | 关联角色/refreshToken 级联清理                          |
| deleteRole 仍被用户引用              | E1004                                                   |
| addMenu 重复 routeName               | E1005                                                   |
| deleteMenu 有子菜单                  | E1006                                                   |
| getRoleMenuAuth / updateRoleMenuAuth | 回显准确；保存后父链补全；重新登录后按新权限出菜单/按钮 |

## 8. 按钮权限（角色级精细授权）

> 目的：把按钮权限从"菜单级"（授权菜单 = 拥有其全部按钮）细化为"按钮级"（角色可勾选某菜单下的部分按钮）。

### 8.1 新表 sys_role_button

```sql
CREATE TABLE `sys_role_button` (
  `role_id`     BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
  `menu_id`     BIGINT UNSIGNED NOT NULL COMMENT '菜单ID（按钮所属菜单）',
  `button_code` VARCHAR(100) NOT NULL COMMENT '按钮权限码（如 B_USER::BTN_ADD）',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`, `menu_id`, `button_code`),
  KEY `idx_menu_id` (`menu_id`),
  CONSTRAINT `fk_role_button_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_role_button_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色按钮权限表';
```

### 8.2 GET /systemManage/getRoleButtonAuth?roleId=2（回显）

返回该角色**已授权菜单**（sys_role_menu）中含按钮的菜单，及其按钮勾选状态。

响应 `data`：

```json
{
  "menus": [
    {
      "menuId": 17,
      "menuName": "用户管理",
      "buttons": [
        { "code": "B_USER::BTN_ADD", "desc": "新增用户" },
        { "code": "B_USER::BTN_DELETE", "desc": "删除用户" }
      ]
    }
  ],
  "checkedCodes": ["B_USER::BTN_ADD"]
}
```

- `menus`：树的数据源（菜单 → 按钮），只包含 buttons 非空且已授权给该角色的菜单；R_SUPER 角色直接返回全部含按钮菜单
- `checkedCodes`：该角色在 `sys_role_button` 中的全部 button_code
- **语义：某菜单在 sys_role_button 中没有任何记录 = 该菜单按钮全给（默认全选，兼容存量数据）**——即回显时：菜单无记录 → 该菜单全部按钮进 checkedCodes；有记录 → 只勾记录中的

### 8.3 POST /systemManage/updateRoleButtonAuth（保存）

请求：

```json
{ "roleId": 2, "buttonCodes": ["B_USER::BTN_ADD", "B_MANAGE::BTN_EXPORT"] }
```

实现要点：

- 事务内先删该角色全部 `sys_role_button`，再批量插入
- button_code → menu_id 映射：遍历该角色已授权菜单的 buttons JSON 在应用层建立（不必用 JSON_CONTAINS 查询）
- **越权处理**：buttonCodes 中不属于"该角色已授权菜单"的按钮码直接忽略（不报错），防止通过接口给未授权菜单塞按钮
- R_SUPER 保存时直接返回成功（超管始终全量，可不落库）

### 8.4 getUserInfo 聚合规则调整

`/auth/getUserInfo` 的 `buttons` 计算改为：

```
R_SUPER                     → 全部菜单的 buttons 全集
某菜单在 sys_role_button 无记录 → 该菜单 buttons 全集      （默认全给）
某菜单在 sys_role_button 有记录 → 仅该菜单被勾选的 code
最终 buttons = 上述按菜单求并集，去重
```

### 8.5 验收用例

| 场景                                             | 预期                                                          |
| ------------------------------------------------ | ------------------------------------------------------------- |
| getRoleButtonAuth 全新角色（授权了含按钮的菜单） | menus 返回该角色授权的含按钮菜单；checkedCodes = 其全部按钮码 |
| updateRoleMenuAuth 后再查按钮授权                | menus 只含新授权菜单                                          |
| updateRoleButtonAuth 勾一半按钮                  | 库中只留勾选记录                                              |
| 保存后重新登录                                   | getUserInfo.buttons 只含勾选按钮 + 未配置菜单的全量按钮       |
| 保存含未授权菜单的按钮码                         | 被忽略，不报错                                                |
| 删除角色/菜单                                    | sys_role_button 级联清理                                      |
