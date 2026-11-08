# 前端开发提示词：合同管理模块（可直接复制给 CMS-Frontend 的 AI 会话）

> 用法：把本文件全文粘贴给 CMS-Frontend 工程的 AI 会话即可。后端已完成并冒烟通过，前端按本提示词实现界面。

---

## 任务

在 CMS-Frontend（Soybean Admin 架构）中开发"合同管理"模块界面：1 个主列表页 + 2 个全屏明细弹窗（收款明细、开票明细）。后端（CMS-Backend，FastAPI）18 个接口已就绪，数据库与 mock 数据已就绪。

需求决议与字段行为详见后端仓库文档（如可访问）：
- `asset/ai-docs/contract-manage-requirement.md`（需求原文 + 已确认决议）
- `asset/ai-docs/db-schema-contract-manage.md`（表结构与 API 清单）

## 路由与菜单（seed 已入库 sys_menu id 86/87）

| 项 | 值 |
|---|---|
| 目录菜单 | 合同管理，route_name `contract`，path `/contract`，icon `mdi:file-signature`，i18nKey `route.contract` |
| 页面菜单 | 合同基本信息，route_name `contract_basic-info`，path `/contract/basic-info`，component `view.contract_basic-info`，i18nKey `route.contract_basic-info`，keepAlive |
| 前端需要做 | 注册 elegant 路由 + `src/views/contract/basic-info/index.vue` + i18n 文案 |

## API 约定

- Base URL：`http://<后端主机>:8004`（开发建议走前端代理，如 `/proxy-default/contractManage/...`，按工程现有代理模式配置）
- 认证：`Authorization: Bearer <accessToken>`，登录/刷新复用既有 `/auth/login`、`/auth/refreshToken`
- 响应信封：`{code, msg, data}`；`code==="0000"` 成功；`"9999"` token 过期走登出；其他 toast `msg`
- 分页结构：`{records, current, size, total}`
- 请求体：**GET** 参数走 query string；**普通 POST** 传 JSON；**带 file 的 POST** 传 multipart/form-data（其余字段为 form 字段）
- 查询参数容错：GET 空参数可直传（如 `invoiceDateStart=`、`invoiceType=` 会被后端忽略）、枚举字段兼容数字；表单端点选填金额留空传 `""` 也按未填处理
- 错误码：E3001 文件格式不符 / E3002 暂存合同失效需重新上传 / E3003 合同编号重复 / E3004 合同不存在或已作废 / E3005 合同已作废 / E3101 收款明细不存在 / E3201 开票日期晚于今天 / E3202 开票明细不存在 / E3203 未上传发票

## 界面布局（总体要求）

1. **参考"定时任务管理"页面**的布局风格：顶部查询卡片（查询条件 + 查询按钮）+ 表格卡片（新增按钮在卡片上方非操作列位置）
2. **操作列固定右侧**（`fixed: 'right'`），横向滚动不消失
3. 表格**序号列由前端按行序自动 +1 展示**，不取后端字段
4. 金额单位元、两位小数展示；readonly 字段输入框置灰

## 页面一：合同基本信息（主列表）

### 表格列（后端 records 字段，camelCase）

| 列 | 字段 | 说明 |
|---|---|---|
| 序号 | — | 前端行号 |
| 月份 | `month` | YYYY-MM |
| 区域 | `region` | 茂南区/化州市/高州市/电白区/高新区/滨海新区 |
| 企业名称 | `companyName` | |
| 项目类型 | `projectType` | |
| 合同上传 | `contractFile` | 列内展示"已上传"标识 + 下载入口 |
| 合同金额(元) | `contractAmount` | |
| 成本核算(元) 6 子列 | `costSiteAudit` `costExpertReview` `costIntermediaryFee` `costReportCommission` `costQualification` `costSalesmanCommission` | 建议表头分组"成本核算" |
| 增值税费1% | `vatTax` | **readonly** |
| 毛利润(元) | `grossProfit` | **readonly** |
| 联系人 | `contactPerson` | |
| 联系方式 | `contactPhone` | |
| 合同编号 | `contractNo` | |
| 签约日期 | `signDate` | YYYY-MM-DD |
| 余收款金额 | `remainingReceiptAmount` | **readonly**（后端计算） |
| 余开票金额 | `remainingInvoiceAmount` | **readonly** |
| 项目完成情况 | `completionStatus` | `1`完成 `2`未完成 |
| 报告上传 | `reportFile` | 上传按钮 + 已上传标识 |
| 状态 | `status` | `1`生效 `2`作废 |
| 操作列 | — | 修改/删除/作废/收款明细/开票明细，固定右侧 |

### 查询条件

合同编号（模糊、不分大小写）、企业名称（模糊、不分大小写）、完成情况（下拉）、**月份范围（默认当月，提供"当月"快捷）** `monthStart`/`monthEnd`、**区域（下拉多选，参数英文逗号分隔：`region=茂南区,化州市`）**、**项目类型（模糊匹配）**、是否生效（下拉）。对应 GET `/contractManage/getContractList`。

### 新增流程（重点）

1. 新增弹窗内必须**先点"上传合同"按钮**（仅允许 .doc）→ `POST /contractManage/uploadContract`（multipart，字段名 `file`）
2. 返回 `data.tempKey` + 预填字段：`contractNo/companyName/contactPerson/contactPhone/projectType/contractAmount/signDate/month/region` + `missing[]`（未解析字段清单，留空手填）
3. 回填表单（全部可修正），**未上传合同前保存按钮禁用**
4. 提交 `POST /contractManage/addContract`（JSON，含 `tempKey`，字段见下）
5. 上传失败或解析部分缺失不阻断：用户补全后照常提交

### 新增/修改字段与编辑矩阵

| 字段（提交名） | 新增 | 修改 |
|---|---|---|
| `tempKey` | 必传（上传返回） | 选传（传=覆盖旧合同，配合 multipart `file`） |
| `contractNo` | 可编辑（预填可改） | **readonly 不可改**（修改接口不收此字段） |
| `month` | 可编辑（默认按签约日期推导 YYYY-MM） | 可编辑 |
| `region` | 下拉必选 | 可编辑 |
| `companyName`/`projectType` | 可编辑（预填可改）必填 | 可编辑 |
| `contractAmount` | 必填 ≥0 | 可编辑 |
| 成本 6 项 `cost*` | ≥0 选填（不传默认 0） | 可编辑 |
| `contactPerson`/`contactPhone` | 必填，手机号 `^1[3-9]\d{9}$` | 可编辑 |
| `signDate` | 必填 YYYY-MM-DD | 可编辑 |
| `completionStatus` | 下拉 `1`完成/`2`未完成 | 可编辑 |
| `vatTax`/`grossProfit`/余收款/余开票 | **不提交，后端算**，界面 readonly | 同左 |

修改：`POST /contractManage/updateContract`（multipart：表单字段 + 可选 `file` 重传合同覆盖；不传 file 则 `upload-required:false` 允许不带文件）。修改接口入参含 `id`，不含 `contractNo`。

### 其他操作

| 操作 | 接口 | 交互 |
|---|---|---|
| 删除 | `POST /contractManage/deleteContract` `{id}` | **二次确认弹窗** |
| 作废 | `POST /contractManage/voidContract` `{id}` | 仅 `status==="1"` 显示；二次确认；成功后行标记"已作废"并禁用全部维护按钮 |
| 报告上传 | `POST /contractManage/uploadReport`（multipart：`id` + `file`，允许 pdf/png/jpg/jpeg） | 覆盖式 |
| 合同下载 | `GET /contractManage/downloadContract?id=` | 文件流下载 `.doc` |

## 页面二：合同收款明细（全屏弹窗）

- 由操作列"收款明细"按钮打开，**默认全屏 + 全屏切换按钮**
- **上方基础信息卡**：取列表响应 `data.header`（`contractNo`、`companyName` 客户信息、`contactPerson/contactPhone`、`remainingReceiptAmount` 余收款金额）
- 查询：收款日期区间 `receiptDateStart/receiptDateEnd`（默认当天 + "当天"快捷），`contractNo` 隐藏带出不可改
- 列：序号（前端行号）、收款日期 `receiptDate`、序号 `seq`（同合同同日期内流水，可展示为"当日第 N 笔"）、收款金额 `receiptAmount`（可空）、操作列（修改/删除，固定右侧）
- 新增弹窗：`POST /contractManage/addReceipt`（JSON：`contractNo` 带出只读、`receiptDate` 必填、`receiptAmount` ≥0 选填）
- 修改弹窗：`POST /contractManage/updateReceipt`（JSON：`id` + `receiptAmount`，**仅金额可改**，日期/编号只读展示）
- 删除：`POST /contractManage/deleteReceipt` `{id}`，**二次确认**

## 页面三：合同开票明细（全屏弹窗）

- 与收款弹窗同构；`data.header` 用 `remainingInvoiceAmount` 余开票金额
- 查询：开票日期区间 `invoiceDateStart/invoiceDateEnd`（默认当天）+ 开票类型 `invoiceType`（`1`专票 `2`普票）
- 列：序号（行号）、开票类型 `invoiceType`、开票日期 `invoiceDate`、seq、开票金额 `invoiceAmount`（可空）、发票 `invoiceFile`（有图显示缩略/预览/下载入口）、操作列（修改/删除/预览发票/下载发票）
- 新增：`POST /contractManage/addInvoice`（multipart：`contractNo` 带出只读、`invoiceType` 必选、`invoiceDate` 必填 **≤ 今天（日期选择器禁用未来日期）**、`invoiceAmount` ≥0 选填、`file` 发票文件选传：图片(png/jpg/jpeg/gif/bmp/webp)/pdf/doc/docx/xls/xlsx）
- 修改：`POST /contractManage/updateInvoice`（multipart：`id`、`invoiceType`、`invoiceDate`≤今天、`invoiceAmount`、`file` 选传覆盖）
- 预览：`GET /contractManage/previewInvoice?id=`（返回 image/*，弹层预览）；下载：`GET /contractManage/downloadInvoice?id=`（附件下载）
- 删除：`POST /contractManage/deleteInvoice` `{id}`，二次确认；删除会连带删发票文件

## 按钮权限码（sys_menu buttons，useAuth().hasAuth()）

`B_CONTRACT::BTN_ADD` 新增 / `BTN_EDIT` 修改 / `BTN_DELETE` 删除 / `BTN_VOID` 作废 / `BTN_RECEIPT` 收款明细 / `BTN_INVOICE` 开票明细 / `BTN_UPLOAD_REPORT` 报告上传 / `BTN_DOWNLOAD_CONTRACT` 合同下载

## Mock 数据（后端 cms 库已就绪，可直接联调）

- 合同 3 份：`20261030-1安预XY`（真实样例合同，带报告占位与发票图）、`20261105-2安预XY`、`20261020-1安预XY`（**已作废**，用于验证作废态展示）
- 收款 4 笔（含 2026-11-05 同日两笔 seq=1/2）、开票 4 笔（含 2026-11-07 同日两笔 seq=1/2；1 笔带 PNG 发票可预览/下载）
- 样例合同文件可下载：合同 1 的 `contract.doc`

## 其他注意

- 后端 CORS `allow_origins` 目前仅放行 `http://192.168.200.172:4000`；本地开发若跨域被拦，把前端实际 origin 告知后端追加
- 所有"必填/格式/日期上限"前端先本地校验，后端会再校验一遍（错误码见上）
- 中文统一走 i18n（`route.contract*`），金额千分位展示
