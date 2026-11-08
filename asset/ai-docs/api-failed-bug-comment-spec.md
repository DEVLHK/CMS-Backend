# 失败缺陷点评接口规范（projectManage/failedBug 模块）

> 供后端（FastAPI, MySQL 5.7）实现"项目管理 → 缺陷管理 → 失败缺陷点评"的增删改查接口。
> 记录失败缺陷的点评与审阅信息（失败原因分类/原因描述/是否修复引入/改进建议）。同一缺陷可多次点评，按 `seq_no` 递增编号；`test_failure_date` 记录该次点评对应的复测失败日期（同一日期可有多条点评，仅作查询条件）。
> 通用约定同 `api-login-spec.md`：信封 `{code, msg, data}`、成功码 `"0000"`、业务错误 HTTP 200、`Authorization: Bearer <token>`、字段 camelCase、时间输出 `"YYYY-MM-DD HH:mm:ss"` 字符串、日期输出 `"YYYY-MM-DD"`。
> 路由注册 `tags=["projectManage"]`，operationId 用驼峰（如 `bugCommentList`）。

---

## 0. 建表 pms_failed_bug_comment

```sql
CREATE TABLE `pms_failed_bug_comment` (
  `project_id`     VARCHAR(50)   NOT NULL COMMENT '项目编号',
  `bug_id`         VARCHAR(50)   NOT NULL COMMENT '缺陷编号（如 BUG-2026-0001）',
  `seq_no`         INT UNSIGNED  NOT NULL COMMENT '点评序号，同 project_id+bug_id 内从 1 递增（后端生成）',
  `test_failure_date` DATE       NOT NULL COMMENT '该次点评对应的复测失败日期',
  `action_id`      VARCHAR(10)   NULL DEFAULT NULL COMMENT '来源动作ID（zt_action.id，同步脚本写入，API 暂不维护）',
  `last_resolver`  VARCHAR(50)   NOT NULL DEFAULT '' COMMENT '缺陷最后解决人（点评时快照）',
  `qa_owner`       VARCHAR(50)   NOT NULL DEFAULT '' COMMENT '缺陷QA人员（点评时快照）',
  `failure_reason_category` TINYINT NULL DEFAULT NULL COMMENT '失败原因分类（字典 1-11，见枚举表；空=待点评，同步脚本占位）',
  `failure_reason` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '失败原因描述',
  `is_caused_by_fixing` TINYINT NOT NULL DEFAULT 0 COMMENT '是否因修复其他缺陷引入 1:是 0:否',
  `suggestion`     VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '改进建议',
  `comment_date`   DATETIME      NULL DEFAULT NULL COMMENT '点评时间（新增时后端取当前时间）',
  `commented_by`   VARCHAR(30)   NOT NULL DEFAULT '' COMMENT '点评人（登录账号，新增时取 token）',
  `reviewer`       VARCHAR(30)   NOT NULL DEFAULT '' COMMENT '审阅人（登录账号）',
  `review_date`    DATETIME      NULL DEFAULT NULL COMMENT '审阅时间',
  `review_status`  TINYINT       NOT NULL DEFAULT 2 COMMENT '审阅状态 1:已审阅 2:未审阅',
  `create_time`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`, `bug_id`, `seq_no`),
  KEY `idx_test_failure_date` (`test_failure_date`),
  KEY `idx_review_status` (`review_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='失败缺陷点评表';
```

**主键为联合主键 `project_id + bug_id + seq_no`**（无自增 id）：`seq_no` 由后端在同 `project_id+bug_id` 内生成（`MAX(seq_no)+1`，并发冲突由主键兜底并重试），前端不传。接口层以该组合键标识单条记录（详情/修改/删除入参均用组合键）。

**枚举与类型约定（API 层输出字符串，库内 TINYINT）**

| 字段             | API 类型 | 值                | 中文            |
| ---------------- | -------- | ----------------- | --------------- |
| isCausedByFixing | boolean  | `true` / `false`  | 是否修复引入    |
| reviewStatus     | string   | `"1"` / `"2"`     | 已审阅 / 未审阅 |

`failureReasonCategory` 字典（库存 TINYINT 1-11，API 输出字符串 code，前端字典渲染中文；**NULL=待点评**——同步脚本 `app/schedule/scripts/gen_failure_bug_data.py` 生成的占位行分类为空，待人工点评补填）：

| code | 中文                             |
| ---- | -------------------------------- |
| 1    | 没有完整看完所有问题，提出新需求 |
| 2    | 没有在UAT环境做QA                |
| 3    | UI优化非功能性                   |
| 4    | 不同机型的兼容性                 |
| 5    | 补充提出其他独立问题             |
| 6    | 复测不全面                       |
| 7    | 问题没有完全修复                 |
| 8    | 解释性问题                       |
| 9    | 解释后才第一次真正提出问题       |
| 10   | 双方的发版协调                   |
| 11   | 版本问题                         |

**错误码**

| code  | 场景               | msg 示例                |
| ----- | ------------------ | ----------------------- |
| E2003 | 新增主键冲突       | 该缺陷点评记录已存在     |
| E2004 | 记录不存在         | 点评记录不存在           |

---

## 1. GET /projectManage/failedBug/getBugCommentList（分页查询）

Query 参数（均可空）：

| 参数            | 类型   | 说明                                                                      |
| --------------- | ------ | ------------------------------------------------------------------------- |
| current         | number | 页码，默认 1                                                              |
| pageSize        | number | 每页条数，默认 10                                                         |
| projectId       | string | 项目编号，模糊匹配                                                        |
| bugId           | string | 缺陷编号，模糊匹配                                                        |
| testFailureDate | number | 复测失败日期（毫秒时间戳，日期控件产出），按所选日期整天匹配（DATE 等值）  |

响应 `data`（分页结构）：

```json
{
  "records": [
    {
      "projectId": "PRJ-2026-018",
      "bugId": "BUG-2026-0001",
      "bugTitle": "登录页面偶发白屏",
      "bugStatus": "处理中",
      "seqNo": 1,
      "testFailureDate": "2026-10-12",
      "lastResolver": "王伟",
      "qaOwner": "陈晨",
      "failureReasonCategory": "6",
      "failureReason": "回归范围评估不足，未覆盖关联订单模块",
      "isCausedByFixing": false,
      "suggestion": "修复单关联模块必须纳入回归清单",
      "commentDate": "2026-10-12 18:30:00",
      "commentedBy": "qa02",
      "reviewer": "KenLin",
      "reviewDate": "2026-10-13 09:15:00",
      "reviewStatus": "1"
    }
  ],
  "current": 1,
  "size": 10,
  "total": 42
}
```

排序：`test_failure_date DESC, bug_id DESC, seq_no DESC`（最新失败在前，同缺陷按点评顺序倒序）。
`bugTitle`/`bugStatus`：按 `project_id + bug_id` 联查 `pms_failed_bug` 补充（BUG 标题 + 当前状态），**无匹配时返回 null**。

## 2. GET /projectManage/failedBug/getBugCommentDetail（查询详情）

Query 参数（组合键，均必填）：

| 参数      | 类型   | 说明             |
| --------- | ------ | ---------------- |
| projectId | string | 项目编号（精确） |
| bugId     | string | 缺陷编号（精确） |
| seqNo     | number | 点评序号（精确） |

响应 `data`：单条记录，字段同 1 的 `records[0]`（全部业务字段）。

## 3. POST /projectManage/failedBug/addBugComment（新增）

请求（`seqNo` 后端生成，前端不传）：

```json
{
  "projectId": "PRJ-2026-018",
  "bugId": "BUG-2026-0001",
  "testFailureDate": 1760198400000,
  "lastResolver": "王伟",
  "qaOwner": "陈晨",
  "failureReasonCategory": "6",
  "failureReason": "回归范围评估不足，未覆盖关联订单模块",
  "isCausedByFixing": false,
  "suggestion": "修复单关联模块必须纳入回归清单",
  "reviewer": "",
  "reviewDate": null,
  "reviewStatus": "2"
}
```

行为：

- `seqNo` = 同 `project_id+bug_id` 内 `MAX(seq_no)+1`（从 1 起），**后端生成**
- `commented_by` = 当前登录账号（从 token 解析）、`comment_date` = 当前时间，**后端生成，前端不传**
- `reviewer/reviewDate/reviewStatus` 可不传，默认未审阅（`review_status=2`）
- `failureReasonCategory` 必填，须为字典 1-11，否则参数校验不通过
- 并发新增主键冲突时后端自动重试取号，仍失败 → E2003
- 响应：`{"code": "0000", "msg": "", "data": null}`

## 4. POST /projectManage/failedBug/updateBugComment（修改）

请求：组合键定位 + 待改业务字段（均可选，仅传需要修改的）：

```json
{
  "projectId": "PRJ-2026-018",
  "bugId": "BUG-2026-0001",
  "seqNo": 1,
  "failureReasonCategory": "7",
  "failureReason": "空指针未判空，修改后回归通过",
  "isCausedByFixing": true,
  "reviewer": "KenLin",
  "reviewDate": 1760311500000,
  "reviewStatus": "1"
}
```

行为：

- 组合键 `(projectId, bugId, seqNo)` 不存在 → E2004
- **主键字段不可修改**（projectId/bugId/seqNo 仅作定位条件）
- 响应：`{"code": "0000", "msg": "", "data": null}`

## 5. POST /projectManage/failedBug/deleteBugComment（删除）

请求（组合键）：

```json
{ "projectId": "PRJ-2026-018", "bugId": "BUG-2026-0001", "seqNo": 1 }
```

行为：记录不存在 → E2004；删除成功 `data: null`。

---

## 6. 验收用例

| 场景                     | 预期                                                                     |
| ------------------------ | ------------------------------------------------------------------------ |
| 无条件查询               | 分页结构，records 字段齐全；reviewStatus/category 字符串、isCausedByFixing 布尔 |
| 同一缺陷多次点评         | 返回多行（bugId 相同、seqNo 递增），组合键各不相同                       |
| 新增自动取号             | 同 bug 首次 seqNo=1，再次为 2；并发新增不产生重号                         |
| projectId/bugId 模糊查询 | 命中编号含关键字的记录                                                   |
| testFailureDate 按天过滤 | 命中该日期的记录（DATE 等值）                                            |
| 详情按组合键查询         | 返回单条完整记录；组合键不存在时 E2004                                   |
| 新增                     | seqNo/commentedBy/commentDate 后端写入；字典外分类被校验拦截             |
| 修改（部分字段）         | 仅更新传入字段；主键字段不变；不存在 E2004                               |
| 删除                     | 组合键命中即删除；不存在 E2004                                           |

## 7. 前端配套改动（后台就绪后）

1. `src/service/api/project-manage.ts` 增加：`fetchGetBugCommentList(params)` / `fetchGetBugCommentDetail(key)` / `fetchAddBugComment(data)` / `fetchUpdateBugComment(data)` / `fetchDeleteBugComment(key)`
2. 表格 row-key 用组合键 `${projectId}-${bugId}-${seqNo}`
3. `testFailureDate` 毫秒时间戳直传；`failureReasonCategory` 下拉接字典（code→中文 11 项）；`isCausedByFixing` 用开关组件
4. 新增弹窗不展示点评人/点评时间/序号（后端生成）；审阅操作用修改接口更新 reviewer/reviewDate/reviewStatus
