# 成员任务监控每日快照脚本逻辑（gen_member_task_stat.py）

> 脚本：`app/schedule/scripts/gen_member_task_stat.py`
> 写入表：`task_monitor_daily_stat`（每成员每项目一条，项目 = pms_team_member 所属项目）
> 服务对象：`GET /projectManage/taskMonitor/getMemberTaskSummary`
> 用途：每日凌晨定时执行（建议 00:10），也可 `--date` 手动补算历史
>
> ⚠️ 更新逻辑前必读第 6 节"注意事项"。

---

## 1. 入参

| 参数 | 必填 | 说明 |
|---|---|---|
| `--project_ids` | 是 | 项目ID，逗号分隔（如 `1948,1982`）。决定成员名单范围 |
| `--date` | 否 | 统计日期 `YYYY-MM-DD`，**缺省=上一日**（脚本设计为次日凌晨运行，统计"当天"即运行日的上一日） |

## 2. 成员名单与团队（team）

1. 成员名单：`pms_team_member`（oms 库）中 `project_id IN (入参项目)` 的 `pms_user` 去重。**后续 bug/task 统计只覆盖该名单内人员**（按 `assignedTo/finishedBy` 匹配）
2. team（大组名）：`pms_team_member → pms_team_list.team_group_id → pms_team_group_list.team_group_name` 链路
   - 匹配优先级：`(项目, 账号)` 精确 → 账号任意项目兜底 → 空串
   - 同一账号跨项目大组不同时，取链路中最后一行（当前实现 setdefault，先到先得）
3. QA 身份：成员任一大组名 ∈ `QA_GROUP_NAMES = ("QA Team", "Testing Team")` 即认定 QA 职能（影响第 3/4 节口径分支）

## 3. completed（今日完成任务数 + completed_today_list）

`completed_today_list` 格式：`{"bug": "ID1,ID2", "task": "ID1,ID2"}`；
`completed_today_count = bug 数 + task 数`。

### 3.1 缺陷（zt_bug，数据集：deleted≠1 且 status≠closed）

按**成员职能**与**缺陷所属项目**分支（转出时间不限，只看"曾经转出过 + 当前不在其名下"）：

| 成员 | 缺陷项目 | 认定完成条件 |
|---|---|---|
| 非 QA | 1982 | 该成员曾将缺陷 resolved/assigned 转给 **QA 团队账号**（zt_action: assigned 且 extra∈QA账号，或 resolved 且缺陷当前指派人在 QA 账号中），且缺陷当前 `assignedTo ≠ 该成员` |
| 非 QA | 1948 及其他 | 同上，目标为 **QA 团队账号或 DeployRobot** |
| QA | 任意 | 该成员曾转给 **DeployRobot 或 CBL-QA**，且**缺陷最后一次被转成 resolved 之后（不限操作人）的最新一条非空评论命中 `QA Report`**（正则 `qa\s*report`，忽略大小写），且缺陷当前 `assignedTo ≠ 该成员` |

### 3.2 任务（zt_task，数据集：deleted≠1 且 status ∉ (cancel, closed)）

`finishedBy = 成员 AND DATE(finishedDate) = 统计日期`（"点成 done"，不限项目与团队）。

## 4. overdue（今日逾期任务数 + overdue_list）

`overdue_list` 格式同上；`overdue_count = bug 数 + task 数`。

数据集：同 3.1/3.2 但**不要求完成**（任务侧仍排除 cancel/closed）。判定日期基准均为统计日期：

| 成员 | 缺陷项目 | 逾期条件 |
|---|---|---|
| QA | 任意 | 该缺陷**最后一次被指派给该 QA 成员**的日期（zt_action: assigned 且 extra=该 QA）距统计日 > 宽限期（宽限期：统计日为周五 2 天，否则 1 天）；无指派记录则不计 |
| 非 QA | 1982 | `统计日期 - openedDate(日期) > 宽限期` |
| 非 QA | 1948 及其他 | `deadline` 为空，或 `deadline < 统计日期` |

任务（zt_task）：数据集同上（assignedTo∈名单，status ∉ cancel/closed），`deadline` 为空或 `deadline < 统计日期` → 逾期。

## 5. 写入与调度

- 写入：`upsert_daily_stat`（uk: stat_date+member+project_id），每成员每项目一条，project_id 取成员在 pms_team_member 中所属的真实项目
- 建议调度配置：脚本 `app/schedule/scripts/gen_member_task_stat.py`，period `day`，间隔 1，首次执行 00:10（依赖 zt_action 当日完整，且避开零点任务高峰）
- 依赖的数据新鲜度：**见第 6 节第 1 条（同步表滞后问题）**

## 6. 注意事项（更新逻辑前必读）

1. **同步表新鲜度**：聚合源 `pms_task_analytical_status` 由 `task_analytical_status_job` 从 zentao 同步。该任务当前**未在调度中注册**，表内 `finishedDate` 最新仅到 2026-06-11 → 近期日期的 completed 统计会为空。上线前必须恢复该同步任务，或改为本脚本直查 zentao 只读库（read_pms）
2. **CBL_ 外包成员 team 为空**：`CBL_*` 账号未登记在 `pms_team_member`，团队链路无法解析。补名单后重新运行本脚本即可带出
3. **`member` 存 realname**：脚本将 `assignedTo/finishedBy` 账号转为 `zt_user.realname` 后写入；汇总接口也按 realname 展示，两处一致。若 zenTao 改名，历史快照行的 member 不随动（uk 含 member，改名会断链，需人工合并）
4. **dueDate 未持久化**：1982 规则中的"dueDate=创建日期+1"仅用于逾期判定，快照表无此列；如前端要展示，需加列
5. **QA 大组名为硬编码**：`QA_GROUP_NAMES = ("QA Team", "Testing Team")`，团队改名需同步脚本常量
