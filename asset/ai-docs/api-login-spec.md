# 登录模块 API 格式规范（对齐 Soybean Admin 前端）

> 本文档供后端（FastAPI, localhost:8001）修改登录接口使用。
> 所有格式要求来自 Soybean Admin 前端的实际代码约定，前端不做任何改动，后端需按本文档对齐。
> 前端依据文件：`src/service/api/auth.ts`、`src/service/request/index.ts`、`src/service/request/shared.ts`、`src/typings/api/auth.d.ts`、`src/typings/app.d.ts`、`src/store/modules/auth/index.ts`、`.env`

---

## 1. 登录链路总览

```
POST /login/user-login     → 登录，返回 token + refreshToken
GET  /auth/getUserInfo     → 登录后立刻调用，返回用户信息（roles/buttons 驱动权限）
POST /auth/refreshToken    → token 过期后前端自动调用刷新
```

- 登录后的所有请求通过 Header 携带：`Authorization: Bearer <token>`
- 前端按响应信封中的 `code` 判断成功/失败，**业务错误也返回 HTTP 200**，用 code 区分

---

## 2. 通用响应信封（字段名固定，不可更改）

```json
{
  "code": "0000",
  "msg": "",
  "data": {}
}
```

| 字段   | 类型           | 说明                                             |
| ------ | -------------- | ------------------------------------------------ |
| `code` | string         | `"0000"` = 成功；其他 = 失败（见下方码表）       |
| `msg`  | string         | 提示消息，成功为 `""`，失败时前端直接 toast 显示 |
| `data` | object \| null | 业务数据，失败时为 `null`（不要返回 `{}`）       |

**注意：是 `msg`，不是 `message`**（前端 4 处硬编码取 `data.msg`）。

### code 码表（与前端 `.env` 一一对应）

| 类别         | 码值                   | 前端行为                                 |
| ------------ | ---------------------- | ---------------------------------------- |
| 成功         | `0000`                 | 取 `data` 继续业务                       |
| 登出码       | `8888`, `8889`         | 静默登出，跳回登录页                     |
| 弹窗登出码   | `7777`, `7778`         | 弹错误对话框后登出                       |
| token 过期码 | `9999`, `9998`, `3333` | 自动调 `/auth/refreshToken` 后重放原请求 |
| 其他任意码   | 如 `E0001`             | toast 显示 `msg`                         |

---

## 3. POST /login/user-login

### 请求

- Content-Type: `application/json`
- 字段命名 camelCase；**是 `userName`（大写 N），不是 `username`**（前端 `fetchLogin(userName, password)`）
- 两个字段必填（minLength=1），缺失时应返回 422 校验错误，而不是走到业务逻辑返回"用户名或密码错误"

```json
{
  "userName": "admin",
  "password": "123456"
}
```

### 成功响应（200）

`data` 必须是 `LoginToken` 结构，`token` 与 `refreshToken` 缺一不可：

```json
{
  "code": "0000",
  "msg": "",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "a8f3d2e1-..."
  }
}
```

### 失败响应（200，业务错误）

```json
{
  "code": "E0001",
  "msg": "用户名或密码错误",
  "data": null
}
```

**注意：登录失败不要使用 `8888/7777` 系列登出码**，否则前端会执行登出流程；普通业务错误码走 toast 即可。

---

## 4. GET /auth/getUserInfo（登录后前端必调）

- Method: `GET`，无请求 body
- 通过 Header `Authorization: Bearer <token>` 识别当前用户（不需要传 userName）
- `data` 必须是 `UserInfo` 结构：

```json
{
  "code": "0000",
  "msg": "",
  "data": {
    "userId": "1",
    "userName": "Soybean",
    "roles": ["R_SUPER"],
    "buttons": ["B_AUTH::BTN_ADD", "B_AUTH::BTN_DELETE"]
  }
}
```

| 字段       | 类型     | 说明                                             |
| ---------- | -------- | ------------------------------------------------ |
| `userId`   | string   | 用户 ID                                          |
| `userName` | string   | 展示用用户名                                     |
| `roles`    | string[] | 角色码；静态路由模式超管角色固定为 `R_SUPER`     |
| `buttons`  | string[] | 按钮权限码；无按钮权限返回空数组 `[]`，不要 null |

> 后端现有 `/login/get-user-role` 可改造为此接口：改 GET、去 userName 入参改用 token、补 `buttons` 与 `userId`。

### token 无效/过期时

返回过期码，前端会自动刷新 token 并重放：

```json
{ "code": "9999", "msg": "token expired", "data": null }
```

---

## 5. POST /auth/refreshToken（新增）

### 请求

```json
{
  "refreshToken": "a8f3d2e1-..."
}
```

### 成功响应

`data` 结构同登录（返回全新的 token 对）：

```json
{
  "code": "0000",
  "msg": "",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "b9e4f3a2-..."
  }
}
```

### 失败响应

**必须返回登出码（如 `8888`），不能返回 `9999/9998/3333` 过期码**，否则前端会无限循环刷新（前端 `request/index.ts:87` 注释明确要求）：

```json
{ "code": "8888", "msg": "login expired", "data": null }
```

---

## 6. 当前后端问题清单（对照 localhost:8001 现状）

| #   | 项                | 当前后端                                              | 要求                                                        |
| --- | ----------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
| 1   | 成功码            | `"0"`                                                 | `"0000"`                                                    |
| 2   | 消息字段          | `message`                                             | `msg`                                                       |
| 3   | 登录请求字段      | `username`（且未标记必填，空 body 可通过校验）        | `userName`，必填 minLength=1                                |
| 4   | 登录 data 结构    | 裸 `object`，无类型                                   | `{token, refreshToken}`                                     |
| 5   | 错误时 data       | `{}`                                                  | `null`                                                      |
| 6   | 用户信息接口      | `POST /login/get-user-role`（body 传 userName）       | `GET /auth/getUserInfo`（Bearer token，返回 roles+buttons） |
| 7   | token 传递        | 未定义                                                | `Authorization: Bearer <token>`                             |
| 8   | 刷新 token 接口   | 不存在                                                | 新增 `POST /auth/refreshToken`，失败返回 `8888`             |
| 9   | OpenAPI schema 名 | `app__api__model__login__user_login_model__Input`     | 给 Pydantic model 配 `title`，如 `UserLoginInput`           |
| 10  | operationId       | `user_login_login_user_login_post`（login 重复 3 次） | 显式指定，如 `userLogin`                                    |

---

## 7. FastAPI / Pydantic 参考实现

遵循后端工程现有代码框架与组织方式，以下仅为字段与别名的参考写法（Pydantic v2）：

```python
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """统一 camelCase 输出/输入别名基类（若工程已有类似基类则沿用）"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserLoginInput(ApiModel):
    model_config = ConfigDict(title="UserLoginInput")

    user_name: str = Field(min_length=1, description="用户登录名称或账号")
    password: str = Field(min_length=1, description="用户登录密码")


class LoginToken(ApiModel):
    model_config = ConfigDict(title="LoginToken")

    token: str
    refresh_token: str


class UserInfo(ApiModel):
    model_config = ConfigDict(title="UserInfo")

    user_id: str
    user_name: str
    roles: list[str]
    buttons: list[str]


class RefreshTokenInput(ApiModel):
    model_config = ConfigDict(title="RefreshTokenInput")

    refresh_token: str


class ApiResponse(BaseModel):
    """通用响应信封：code/msg/data 三字段名不可改"""
    model_config = ConfigDict(title="ApiResponse")

    code: str = "0000"
    msg: str = ""
    data: dict | list | None = None
```

路由注册时为接口显式指定 `operation_id` 并添加 `tags`（如 `tags=["auth"]`），便于 Swagger 分组与客户端代码生成。

---

## 8. 验收用例

| 场景         | 请求                                  | 预期                                                                   |
| ------------ | ------------------------------------- | ---------------------------------------------------------------------- |
| 正常登录     | `{"userName":"...","password":"..."}` | `{"code":"0000","msg":"","data":{"token":"...","refreshToken":"..."}}` |
| 密码错误     | 任意错误凭据                          | `code` 非 `0000`，且不是 8888/7777 系列码，`data` 为 null              |
| 空 body      | `{}`                                  | HTTP 422（字段校验拦截）                                               |
| 获取用户信息 | GET + Bearer token                    | data 含 userId/userName/roles/buttons                                  |
| token 过期   | GET getUserInfo 带过期 token          | `code` 为 9999/9998/3333                                               |
| 刷新成功     | 有效 refreshToken                     | 新 token 对                                                            |
| 刷新失败     | 无效 refreshToken                     | `code` 为 8888（非过期码）                                             |
