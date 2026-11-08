# 失败缺陷管理接口规范（projectManage/failedBug 模块）

> 供后端（FastAPI, MySQL 5.7）实现"项目管理 → 缺陷管理 → 失败缺陷管理"页面的查询与审阅接口。
> 页面现状：Soybean 前端已完成（搜索：项目编号/复测失败时间/审阅状态；表格 8 列 + 审阅操作），目前 mock。
> 通用约定同 `api-login-spec.md`：信封 `{code, msg, data}`、成功码 `"0000"`、业务错误 HTTP 200、`Authorization: Bearer <token>`、字段 camelCase、时间输出 `"YYYY-MM-DD HH:mm:ss"` 字符串。
> 路由注册 `tags=["projectManage"]`，operationId 建议 `failedBugList` / `failedBugReview`。

---

## 0. 建表 pms_failed_bug

```sql
CREATE TABLE `pms_failed_bug` (
  `bug_id`         VARCHAR(50)  NOT NULL COMMENT '缺陷编号（如 BUG-2026-0001）',
  `project_id`     VARCHAR(50)  NOT NULL COMMENT '项目编号（搜索条件）',
  `bug_title`      VARCHAR(200) NOT NULL COMMENT '缺陷标题',
  `last_test_fail_date` DATE    NOT NULL COMMENT '最近一次复测失败日期',
  `bug_status`     VARCHAR(50)  NOT NULL DEFAULT '' COMMENT '缺陷当前状态（字符串，原样存储与返回，默认空字符串）',
  `bug_create_time` DATETIME    NOT NULL COMMENT '缺陷创建时间',
  `last_resolver`  VARCHAR(50)  NOT NULL DEFAULT '' COMMENT '缺陷最后解决人',
  `last_qa_owner`  VARCHAR(50)  NOT NULL DEFAULT '' COMMENT '缺陷最后QA人员',
  `review_status`  TINYINT      NOT NULL DEFAULT 2 COMMENT '审阅状态 1:已审阅 2:未审阅',
  `last_review_by` VARCHAR(30)  NOT NULL DEFAULT '' COMMENT '最后审阅人（登录账号）',
  `last_review_time` DATETIME   NULL DEFAULT NULL COMMENT '最后审阅时间',
  `create_time`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`, `bug_id`),
  KEY `idx_review_status` (`review_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='失败缺陷表';
```

**主键为联合主键 `project_id + bug_id`**（无自增 id）：同一项目内一个缺陷只保留一条记录，再次复测失败时按主键更新原记录，`last_` 前缀字段（最近失败日期/最后解决人/最后QA/最后审阅人/最后审阅时间）均记录**最近一次**的值。`bug_id` 跨项目可重复，**接口层以 `projectId + bugId` 标识单条记录**（前端表格 row-key 与审阅入参均用组合键）。

数据来源（同步自 PMS 或手工导入）由后台自行实现，本规范只定义查询与审阅。

**已有环境变更 SQL（旧表列改名 + 去重 + 删除自增 id、改联合主键）：**

```sql
ALTER TABLE `pms_failed_bug`
  CHANGE COLUMN `test_fail_date` `last_test_fail_date` DATE NOT NULL COMMENT '最近一次复测失败日期',
  CHANGE COLUMN `qa_owner` `last_qa_owner` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '缺陷最后QA人员',
  CHANGE COLUMN `review_by` `last_review_by` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '最后审阅人（登录账号）',
  CHANGE COLUMN `review_time` `last_review_time` DATETIME NULL DEFAULT NULL COMMENT '最后审阅时间';
-- 去重：同 (project_id, bug_id) 仅保留 last_test_fail_date 最新一行
DELETE t1 FROM `pms_failed_bug` t1
JOIN `pms_failed_bug` t2
  ON t1.`project_id` = t2.`project_id` AND t1.`bug_id` = t2.`bug_id`
 AND t2.`last_test_fail_date` > t1.`last_test_fail_date`;
ALTER TABLE `pms_failed_bug`
  DROP INDEX `uk_project_bug`,
  DROP PRIMARY KEY,
  DROP COLUMN `id`,
  ADD PRIMARY KEY (`project_id`, `bug_id`);
```

**枚举约定（API 层输出字符串，库内 TINYINT）**

`bugStatus` 为**普通字符串**（VARCHAR，默认 `""`），由上游系统/同步数据定义（如 `"处理中"`、`"待复测"`、`"已解决"`），后端原样存储与返回，不做枚举映射；前端按原文展示。

| 字段         | 值    | 中文   | 英文         |
| ------------ | ----- | ------ | ------------ |
| reviewStatus | `"1"` | 已审阅 | Reviewed     |
| reviewStatus | `"2"` | 未审阅 | Not reviewed |

---

## 1. GET /projectManage/failedBug/getBugList（分页查询）

Query 参数（均可空）：

| 参数            | 类型    | 说明                                                                                  |
| --------------- | ------- | ------------------------------------------------------------------------------------- |
| current         | number  | 页码，默认 1                                                                          |
| pageSize        | number  | 每页条数，默认 10                                                                     |
| projectId       | string  | 项目编号，模糊匹配                                                                    |
| testFailDate    | number  | 复测失败日期（毫秒时间戳，日期控件产出），按所选日期整天匹配（DATE 列 `last_test_fail_date`，直接等值比较） |
| bugReviewStatus | '1'/'2' | 审阅状态，精确                                                                        |

响应 `data`（与其他模块一致的分页结构）：

```json
{
  "records": [
    {
      "bugId": "BUG-2026-0001",
      "projectId": "PRJ-2026-018",
      "bugTitle": "登录页面偶发白屏",
      "testFailDate": "2026-10-12",
      "bugStatus": "处理中",
      "bugCreateTime": "2026-10-08 09:12:00",
      "lastResolver": "王伟",
      "qaOwner": "陈晨",
      "reviewStatus": "1"
    }
  ],
  "current": 1,
  "size": 10,
  "total": 987
}
```

排序：`last_test_fail_date DESC, bug_id DESC`（最新失败在前，可按需调整）。
字段映射（API 保持既有 camelCase，不改前端）：`testFailDate ← last_test_fail_date`、`qaOwner ← last_qa_owner`。
`projectId` 在表格"Bug ID"之后展示（130px），同时也是查询条件。

## 2. POST /projectManage/failedBug/reviewBug（审阅）

请求（按联合主键 projectId+bugId 定位）：

```json
{ "projectId": "PRJ-2026-018", "bugId": "BUG-2026-0002" }
```

行为：

- 将该记录 `review_status` 置 1，`last_review_by` = 当前登录账号（从 token 解析）、`last_review_time` = 当前时间
- 响应：`{"code": "0000", "msg": "", "data": null}`

错误码：

| code  | 场景       | msg 示例             |
| ----- | ---------- | -------------------- |
| E2001 | 记录不存在 | 缺陷记录不存在       |
| E2002 | 重复审阅   | 该缺陷已是已审阅状态 |

---

## 3. 验收用例

| 场景                         | 预期                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------- |
| 无条件查询                   | 分页结构，records 字段齐全；reviewStatus 输出字符串，bugStatus 原样返回         |
| 同一缺陷多天失败             | 仅一行，`testFailDate` 为最近一次失败日期（同步按唯一键更新 last_ 字段）           |
| projectId=PRJ 模糊           | 命中所有项目编号含 PRJ 的记录                                                   |
| testFailDate=某天时间戳      | 命中该日期的记录（DATE 等值）                                                   |
| bugReviewStatus=2            | 只返回未审阅                                                                    |
| reviewBug 按 projectId+bugId | review_status→1，last_review_by/last_review_time 写入                           |
| reviewBug 已审阅记录         | E2002                                                                           |
| reviewBug 不存在的组合键     | E2001                                                                           |
| 同步导入重复(项目+缺陷)     | 唯一键兜底（更新原记录），不产生重复行                                          |

## 4. 前端配套改动（后台就绪后）

1. 新增 `src/service/api/project-manage.ts`：`fetchGetFailedBugList(params)` / `fetchReviewBug(projectId, bugId)`（走主 `request`）
2. 页面 `fetchList` 改为调用真实接口：`testFailDate` 时间戳直传；响应做 `records → list` 映射（`{ total, list: data.records }`）
3. `handleReview` 接 `fetchReviewBug(row.projectId, row.bugId)`，成功后刷新表格；表格 row-key 改为 `${projectId}-${bugId}` 组合键
4. `bugStatus` 列直接展示后端返回的字符串（无枚举映射，当前 mock 已是此形态，无需改动）
