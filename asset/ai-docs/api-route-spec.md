# 动态路由接口规范（route 模块）

> 供后端（FastAPI）实现动态菜单路由接口。前端将把 `VITE_AUTH_ROUTE_MODE` 从 `static` 切到 `dynamic`，
> 切换后菜单完全由后台 `sys_menu` + `sys_role_menu` 驱动（角色管理→菜单权限 配置即生效）。
> 通用信封（`{code, msg, data}`、成功码 `"0000"`、`Authorization: Bearer <token>`）同 `api-login-spec.md`。
> 三个接口均需登录（Bearer token），按当前用户计算。

---

## 0. MenuRoute 节点结构（getUserRoutes / getConstantRoutes 共用）

```json
{
  "id": "17",
  "name": "manage_user",
  "path": "/manage/user",
  "component": "view.manage_user",
  "props": true,
  "meta": {
    "title": "用户管理",
    "i18nKey": "route.manage_user",
    "icon": "mdi:account",
    "order": 17,
    "requiresAuth": true,
    "keepAlive": false,
    "constant": false,
    "hideInMenu": false,
    "href": null,
    "activeMenu": null,
    "multiTab": false,
    "fixedIndexInTab": null,
    "query": null
  },
  "children": []
}
```

**sys_menu 行 → MenuRoute 节点的映射规则**：

| MenuRoute 字段                                                             | 来源                                        | 说明                                                                                                                                         |
| -------------------------------------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                                                       | `sys_menu.id`                               | **转字符串**                                                                                                                                 |
| `name`                                                                     | `route_name`                                |                                                                                                                                              |
| `path`                                                                     | `route_path`                                |                                                                                                                                              |
| `component`                                                                | `component`                                 | 目录=`layout.base`；顶级页面=`layout.base$view.xxx`；子页面=`view.xxx`（库中已按此格式存储，原样返回）；iframe 内嵌文档页=`view.iframe-page` |
| `props`                                                                    | **见下方规则**                              | 优先级：`route_props.props`（对象）> 路径含参数（`:id`/`:url`）时 `true` > 省略                                                              |
| `meta.title`                                                               | `menu_name`                                 | **直接用中文菜单名**（无 i18nKey 时菜单显示 title）                                                                                          |
| `meta.i18nKey`                                                             | `route_props.i18nKey`                       | 可空；存在时前端优先用国际化文案                                                                                                             |
| `meta.icon`                                                                | `icon`                                      |                                                                                                                                              |
| `meta.order`                                                               | `route_props.order`（缺省用 `sys_menu.id`） | 决定菜单排序                                                                                                                                 |
| `meta.requiresAuth`                                                        | 固定 `true`                                 | 用户路由专属                                                                                                                                 |
| `meta.keepAlive/hideInMenu/href/activeMenu/multiTab/fixedIndexInTab/query` | `route_props` 同名字段                      | 原样透传，缺省省略或 false/null                                                                                                              |
| `children`                                                                 | 按 `parent_id` 递归组树                     | 无子节点时省略或空数组                                                                                                                       |

**补充（iframe 文档页，2026-10-18）**：`route_props` JSON 中可能含 `props` 键（对象，如 `{"url": "https://cn.vuejs.org/"}`，用于 `view.iframe-page` 内嵌页）。**getUserRoutes 组装时若 route_props 含 `props` 键，必须把它原样输出为节点的 `props` 字段（对象），并从 meta 透传字段中排除**；仅当无该键时才按"路径含参数 → true"推断。对应菜单组：`document`（文档，id 66-76，其中 8 个内嵌 + 2 个 href 外链）。

---

无参数。返回当前用户有权访问的**完整菜单树** + 该用户的首页。

响应 `data`：

```json
{
  "routes": [/* MenuRoute[]，顶级数组，parent_id=0 的菜单（及其可见子树） */],
  "home": "home"
}
```

**计算规则**：

1. 取当前用户全部**启用**角色的 `sys_role_menu` 授权 menuIds，并集（库中已含祖先链）；**R_SUPER 用户 → 全部启用菜单**
2. 只含 `status=1` 的菜单；被授权的父菜单未启用时其子树也不返回
3. 按 `parent_id` 组树，兄弟节点按 `meta.order` 升序
4. `home`：用户角色的 `sys_role.home`（多角色取第一个角色的 home）；**必须属于该用户可访问的页面**，否则回退 `"home"`
5. 按钮权限（buttons JSON）**不在此接口返回**，仅 getUserInfo 使用

**可靠性要求（重要）**：前端在登录后立即调用本接口，**失败会导致用户被直接登出**（auth store `initDynamicAuthRoute` 失败即 resetStore）。所以任何内部异常都要兜底返回 `0000` + 空树 `{"routes": [], "home": "home"}`，而不是非 0000 错误码。

### 参考响应（对应当前库中 R_SUPER 的授权数据）

```json
{
  "routes": [
    {
      "id": "1",
      "name": "home",
      "path": "/home",
      "component": "layout.base$view.home",
      "meta": {
        "title": "首页",
        "i18nKey": "route.home",
        "icon": "mdi:monitor-dashboard",
        "order": 1,
        "requiresAuth": true
      }
    },
    {
      "id": "16",
      "name": "manage",
      "path": "/manage",
      "component": "layout.base",
      "meta": {
        "title": "系统管理",
        "i18nKey": "route.manage",
        "icon": "carbon:cloud-service-management",
        "order": 5,
        "requiresAuth": true
      },
      "children": [
        {
          "id": "17",
          "name": "manage_user",
          "path": "/manage/user",
          "component": "view.manage_user",
          "meta": { "title": "用户管理", "order": 17, "requiresAuth": true }
        },
        {
          "id": "20",
          "name": "manage_user-detail",
          "path": "/manage/user-detail/:id",
          "component": "view.manage_user-detail",
          "props": true,
          "meta": { "title": "用户详情", "order": 20, "hideInMenu": true, "requiresAuth": true }
        }
      ]
    }
  ],
  "home": "home"
}
```

（示例仅节选；实际按库中授权全量返回。注意 `manage_user-detail` 带路径参数需 `props: true`，且通常 `hideInMenu: true` 不出现在菜单。）

---

## 2. GET /route/getConstantRoutes（常量路由）

无参数。返回**无需登录即可访问**的固定路由，内容固定（与前端静态定义一致），可直接硬编码：

```json
[
  {
    "name": "login",
    "path": "/login/:module(pwd-login|code-login|register|reset-pwd|bind-wechat)?",
    "component": "layout.blank$view.login",
    "props": true,
    "meta": { "title": "login", "i18nKey": "route.login", "constant": true, "hideInMenu": true }
  },
  {
    "name": "403",
    "path": "/403",
    "component": "layout.blank$view.403",
    "meta": { "title": "403", "i18nKey": "route.403", "constant": true, "hideInMenu": true }
  },
  {
    "name": "404",
    "path": "/404",
    "component": "layout.blank$view.404",
    "meta": { "title": "404", "i18nKey": "route.404", "constant": true, "hideInMenu": true }
  },
  {
    "name": "500",
    "path": "/500",
    "component": "layout.blank$view.500",
    "meta": { "title": "500", "i18nKey": "route.500", "constant": true, "hideInMenu": true }
  }
]
```

前端对本接口有**静态兜底**（失败时用本地定义），实现顺序可放低。

---

## 3. GET /route/isRouteExist?routeName=manage_user

Query：`routeName`（string，必填）。

响应 `data`：`true` / `false`。

语义：该路由名是否存在于**当前用户可访问路由 ∪ 常量路由**中。前端用它区分"跳 404"还是"跳 403"。

---

## 4. 验收用例

| 场景                                    | 预期                                                                   |
| --------------------------------------- | ---------------------------------------------------------------------- |
| SuperAdmin 登录后调 getUserRoutes       | 返回全部启用菜单组成的树，home=home                                    |
| Tester（仅授权"系统管理+用户管理"）登录 | routes 仅含其授权的子树；看不到 manage_role/manage_menu                |
| 只给角色授权了子菜单未授权父菜单        | 返回树包含补全的父级目录（库里已存祖先链）                             |
| 授权了 home 以外的角色首页              | data.home = sys_role.home                                              |
| routeName=manage_user（已授权用户）     | isRouteExist → true                                                    |
| routeName=manage_role（未授权用户）     | isRouteExist → false                                                   |
| routeName=login                         | isRouteExist → true（常量路由）                                        |
| 数据库异常/无授权数据                   | getUserRoutes 返回 0000 + `{"routes": [], "home": "home"}`，不登出用户 |

---

## 5. 前端配套改动（后台就绪后执行）

1. `src/service/api/route.ts`：`mockRequest` → `request`（已改好）
2. `.env`：`VITE_AUTH_ROUTE_MODE=static` → `dynamic`
3. 验证：登录 Tester 应只看到被授权的菜单；角色管理里改授权后重新登录生效
