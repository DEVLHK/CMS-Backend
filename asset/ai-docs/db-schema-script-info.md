# 脚本信息表 script_info 表结构说明

> 登记可被定时任务调度的脚本（对应 `app/schedulerJob/` 等目录下的脚本文件）：脚本名、路径、描述与**入参定义**（JSON），供任务配置/手动执行时动态渲染参数表单。
> 库：oms（MySQL 5.7），命名与审计字段同现有业务表约定。

---

## 1. 建表 SQL

```sql
CREATE TABLE `script_info` (
  `script_name` VARCHAR(100)  NOT NULL COMMENT '脚本名（主键）',
  `script_path` VARCHAR(200)  NOT NULL COMMENT '脚本路径（仓库相对路径，唯一，如 app/schedulerJob/pms_scheduler/jobs/task_analytical_status_job.py）',
  `description` VARCHAR(500)  NOT NULL DEFAULT '' COMMENT '脚本描述',
  `params`      JSON          NULL DEFAULT NULL COMMENT '脚本入参定义（JSON 数组，元素结构见第 3 节，无入参存 NULL 或 []）',
  `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by`   VARCHAR(30)   NOT NULL DEFAULT '' COMMENT '创建人（登录账号）',
  `update_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_by`   VARCHAR(30)   NOT NULL DEFAULT '' COMMENT '更新人（登录账号）',
  `ts`          TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '时间戳（数据库自动维护，插入/更新均刷新，外部不可写入）',
  PRIMARY KEY (`script_name`),
  UNIQUE KEY `uk_script_path` (`script_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='脚本信息表';
```

## 2. 字段说明

| 字段         | 类型            | 空   | 默认                | 说明                                       |
| ------------ | --------------- | ---- | ------------------- | ------------------------------------------ |
| script_name  | VARCHAR(100)    | 否   | —                   | 脚本名，主键（接口层定位记录）             |
| script_path  | VARCHAR(200)    | 否   | —                   | 脚本路径（仓库相对路径），唯一键 `uk_script_path` |
| description  | VARCHAR(500)    | 否   | `''`                | 脚本描述                                   |
| params       | JSON            | 是   | `NULL`              | 入参定义数组，见第 3 节                    |
| create_time  | DATETIME        | 否   | `CURRENT_TIMESTAMP` | 创建时间                                   |
| create_by    | VARCHAR(30)     | 否   | `''`                | 创建人账号                                 |
| update_time  | DATETIME        | 否   | `CURRENT_TIMESTAMP` | 更新时间，自动维护                         |
| update_by    | VARCHAR(30)     | 否   | `''`                | 更新人账号                                 |
| ts           | TIMESTAMP       | 否   | `CURRENT_TIMESTAMP` | 时间戳，数据库自动维护                     |

## 3. params 入参定义格式（JSON 数组）

每个元素定义一个入参：

| 属性         | JSON 类型        | 必填 | 说明                                                        |
| ------------ | ---------------- | ---- | ----------------------------------------------------------- |
| param_name   | string           | 是   | 参数名（调用脚本时透传）                                     |
| description  | string           | 是   | 参数说明                                                     |
| param_type   | string           | 是   | 参数类型：`String` / `INT`（前端下拉，可按需扩展）           |
| mandatory    | boolean          | 是   | `true`=必填，`false`=可选（缺省用 default）                  |
| default      | 任意（随类型）   | 否   | 默认值，可 `null`                                           |

存储示例：

```json
[
  {
    "param_name": "project_id",
    "description": "项目编号",
    "param_type": "string",
    "mandatory": true,
    "default": null
  },
  {
    "param_name": "days",
    "description": "回溯天数",
    "param_type": "INT",
    "mandatory": false,
    "default": 7
  }
]
```

API 层约定：`params` 原样输出为 JSON 数组（后端解析库内 JSON 列后返回），新增/修改时前端提交数组、后端校验元素结构后序列化入库。

## 4. 设计说明

- `script_name` 为主键、`script_path` 唯一：一脚本一条登记，接口层以 `scriptName` 定位记录，路径变更走修改。
- `ts` 数据库自动维护（插入/更新均刷新），外部不传入；`create_by/update_by` 由接口层从 token 写入。
- 可与 `scheduler_job` 关联：`scheduler_job.script_name` 目前存"路径型脚本名"；如需关联本表，建议后续统一以 `script_info.script_name` 为准（见待确认 3）。

## 5. 待确认项

1. `mandatory` 用 JSON 布尔 `true/false` 表达"是/否"是否符合预期（也可改存 `"yes"/"no"` 字符串）？
2. `scheduler_job.script_name` 是否改为关联 `script_info.script_name`（现为路径全名字符串，两表暂不强制外键）？

## 6. 管理接口（scheduleManage/scriptManage，已实现）

| 接口 | 方法 | 说明 |
| ---- | ---- | ---- |
| /scheduleManage/getScriptInfoList | GET | 分页；`scriptName` 模糊查询；排序 script_name |
| /scheduleManage/getScriptInfoDetail | GET | 按主键 `scriptName` 查单条，不存在报 E1012 |
| /scheduleManage/addScriptInfo | POST | **multipart**（router.yaml 配置 `upload: file` 驱动）：`file`（.py 脚本文件）+ 表单字段 `scriptName/scriptPath/description/params`（params 为 JSON 数组字符串）；文件保存到 `scriptPath` 指定路径（仓库根内，自动创建目录），文件已存在报 E1013，路径非法报 E1014 |
| /scheduleManage/updateScriptInfo | POST | 按 `scriptName` 部分更新；`params` 传空数组=清空为 `[]`；`script_name` 不可改 |
| /scheduleManage/deleteScriptInfo | POST | 按主键 `scriptName` 删除 |

`params` 元素结构由 pydantic 校验（`param_name/description/param_type/mandatory/default`），输出时解析为 JSON 数组（空输出 `[]`）。

> 迁移记录（2026-10-24）：原字段 `optional`（true=可选）全量刷表改名为 `mandatory`（取反，true=必填），存量数据已一次性转换。

错误码：

| code  | 场景           | msg 示例                      |
| ----- | -------------- | ----------------------------- |
| E1010 | 脚本名已存在   | 脚本名已存在: xxx             |
| E1011 | 脚本路径已存在 | 脚本路径已存在: xxx.py        |
| E1012 | 脚本不存在     | 脚本不存在: xxx               |
| E1013 | 脚本文件已存在 | 脚本文件已存在: xxx.py        |
| E1014 | 脚本路径非法   | 脚本路径非法: xxx（含 .. 或越出仓库目录） |
