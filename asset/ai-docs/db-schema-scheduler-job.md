# 定时任务表 scheduler_job 表结构说明

> 用于登记 APScheduler 定时任务（对应 `app/schedulerJob/` 下的脚本）：任务名称、脚本文件、执行周期，并回写最近一次执行时间与状态。
> 库：oms（MySQL 5.7），命名与审计字段同现有业务表约定。管理接口见第 6 节。

---

## 1. 建表 SQL

```sql
CREATE TABLE `scheduler_job` (
  `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '序号（自增主键）',
  `job_name`        VARCHAR(100)  NOT NULL COMMENT '定时任务名称（唯一）',
  `script_name`     VARCHAR(200)  NOT NULL COMMENT '脚本文件名（相对仓库路径，如 app/schedulerJob/pms_scheduler/jobs/task_analytical_status_job.py）',
  `description`     VARCHAR(500)  NOT NULL DEFAULT '' COMMENT '脚本描述',
  `period_type`     VARCHAR(20)   NOT NULL COMMENT '周期类型 second:秒 minute:分 hour:小时 day:天 week:周 month:月 quarter:季 year:年',
  `period_interval` INT UNSIGNED  NOT NULL DEFAULT 1 COMMENT '周期间隔（配合 period_type，如 每2小时 = hour + interval 2）',
  `first_run_date`  DATE          NULL DEFAULT NULL COMMENT '计划首次执行日期（配置项，与 first_run_time 组成首次执行时间点）',
  `first_run_time`  TIME          NULL DEFAULT NULL COMMENT '计划首次执行时刻（配置项，如 06:30:00，当天该时刻首次触发）',
  `last_run_time`   DATETIME      NULL DEFAULT NULL COMMENT '最近一次执行时间（任务回写，未执行为 NULL）',
  `last_run_date`   DATE          NULL DEFAULT NULL COMMENT '最近一次执行日期（任务回写，按天粒度，判断当日是否已执行）',
  `last_run_status` TINYINT       NOT NULL DEFAULT 0 COMMENT '最近一次执行状态 0:未执行 1:成功 2:失败',
  `create_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by`       VARCHAR(30)   NOT NULL DEFAULT '' COMMENT '创建人（登录账号）',
  `update_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_by`       VARCHAR(30)   NOT NULL DEFAULT '' COMMENT '更新人（登录账号）',
  `ts`              TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '时间戳（数据库自动维护，插入/更新均刷新，外部不可写入）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_job_name` (`job_name`),
  UNIQUE KEY `uk_script_name` (`script_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='定时任务表';
```

## 2. 字段说明

| 字段             | 类型            | 空   | 默认                | 说明                                            |
| ---------------- | --------------- | ---- | ------------------- | ----------------------------------------------- |
| id               | BIGINT UNSIGNED | 否   | 自增                | 序号，主键                                      |
| job_name         | VARCHAR(100)    | 否   | —                   | 定时任务名称，唯一键 `uk_job_name`              |
| script_name      | VARCHAR(200)    | 否   | —                   | 脚本文件名（建议存仓库相对路径），唯一键 `uk_script_name`（一脚本一任务） |
| description      | VARCHAR(500)    | 否   | `''`                | 脚本描述                                        |
| period_type      | VARCHAR(20)     | 否   | —                   | 周期类型，字符串枚举见下表                       |
| period_interval  | INT UNSIGNED    | 否   | `1`                 | 周期间隔，单位由 period_type 决定                |
| first_run_date   | DATE            | 是   | `NULL`              | 计划首次执行日期（配置项）                       |
| first_run_time   | TIME            | 是   | `NULL`              | 计划首次执行时刻（配置项，如 `06:30:00`）        |
| last_run_time    | DATETIME        | 是   | `NULL`              | 最近执行时间，由调度器回写                       |
| last_run_date    | DATE            | 是   | `NULL`              | 最近执行日期（天粒度），与 last_run_time 一并回写 |
| last_run_status  | TINYINT         | 否   | `0`                 | 最近执行状态，枚举见下表                         |
| create_time      | DATETIME        | 否   | `CURRENT_TIMESTAMP` | 创建时间                                        |
| create_by        | VARCHAR(30)     | 否   | `''`                | 创建人账号                                      |
| update_time      | DATETIME        | 否   | `CURRENT_TIMESTAMP` | 更新时间，自动维护                               |
| update_by        | VARCHAR(30)     | 否   | `''`                | 更新人账号                                      |
| ts               | TIMESTAMP      | 否   | `CURRENT_TIMESTAMP` | 时间戳，数据库自动维护（插入/更新均刷新）        |

## 3. 枚举定义

**period_type 周期类型（字符串枚举）**

| 值        | 单位 | 触发方式（APScheduler）                          |
| --------- | ---- | ------------------------------------------------ |
| second    | 秒   | IntervalTrigger(seconds=interval)                |
| minute    | 分   | IntervalTrigger(minutes=interval)                |
| hour      | 小时 | IntervalTrigger(hours=interval)                  |
| day       | 天   | IntervalTrigger(days=interval)                   |
| week      | 周   | IntervalTrigger(weeks=interval)                  |
| month     | 月   | CronTrigger(day=1, hour=0)（每 interval 月一次） |
| quarter   | 季   | CronTrigger(month='*/3', day=1, hour=0)          |
| year      | 年   | CronTrigger(month=1, day=1, hour=0)              |

> 月/季/年为日历周期，APScheduler 无原生 interval，建议转 CronTrigger；`period_interval` 对月/季/年表示"每 interval 个周期"（如每 2 月）。

**last_run_status 执行状态（建议值，待确认）**

| 值 | 含义 |
| -- | ---- |
| 0  | 未执行 |
| 1  | 成功 |
| 2  | 失败 |

## 4. 设计说明

- `job_name`、`script_name` 均唯一：一脚本只配置一个任务，任务名称与脚本均可作为业务标识。
- `period_type + period_interval + first_run_date + first_run_time` 共同定义调度计划：首次触发时间点 = `first_run_date` 当天的 `first_run_time` 时刻，之后按 `period_type/period_interval` 推进；`first_run_*` 为空时默认任务注册后立即按周期执行（管理端写入，调度器只读）。
- `last_run_time/last_run_date/last_run_status` 由调度器在每次执行后回写，管理端只读；`ts` 由数据库自动维护（插入/更新均刷新），外部不传入。

## 5. 已定设计

1. `last_run_status`：0 未执行 / 1 成功 / 2 失败（TINYINT，API 输出字符串）。
2. `ts`：`TIMESTAMP` 类型，`DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`，数据库自动维护。
3. 暂不设 `enabled` 启停字段（如需再加）。

## 6. 管理接口（scheduleManage/schedulerJob，已实现）

| 接口 | 方法 | 说明 |
| ---- | ---- | ---- |
| /scheduleManage/getSchedulerJobList | GET | 分页；`jobName`/`scriptName` 模糊查询；排序 id |
| /scheduleManage/getSchedulerJobDetail | GET | 按 id 查询单条，不存在报 E1009 |
| /scheduleManage/addSchedulerJob | POST | `create_by` 取 token；`firstRunDate`/`firstRunTime` 可空 |
| /scheduleManage/updateSchedulerJob | POST | 按 id 部分更新；`firstRun*` 传空串=清除；`last_run_*` 不可改 |
| /scheduleManage/deleteSchedulerJob | POST | 按 id 删除 |

`periodType` 前端提交字符串枚举（second/minute/hour/day/week/month/quarter/year）；`periodInterval ≥ 1`；`firstRunDate` 格式 `YYYY-MM-DD`、`firstRunTime` 格式 `HH:mm:ss`（正则校验）。

错误码：

| code  | 场景           | msg 示例                      |
| ----- | -------------- | ----------------------------- |
| E1007 | 任务名称已存在 | 任务名称已存在: xxx           |
| E1008 | 脚本已配置任务 | 脚本已配置任务: xxx.py        |
| E1009 | 任务不存在     | 任务不存在: 1                 |
