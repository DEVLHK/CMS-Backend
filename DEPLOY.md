# Soybean-backend 部署运维手册

> 适用环境：Linux 服务器 / 部署用户 `hbs` / 部署目录 `/app/hbs/cms/Soybean-backend` / 监听端口 `8004`

---

## 1. 服务概述

| 项 | 说明 |
|---|---|
| 形态 | FastAPI 单进程服务（uvicorn） |
| 入口 | `app/run_cms_app.py`（`run_cms_app:cms_app`） |
| 定时任务 | APScheduler **内嵌在服务进程里**，启动时从 cms 库 `scheduler_job` 表自动重建启用任务 |
| 数据依赖 | cms 业务库（`config/database/mysql/cms.cnf`）、禅道库（`zentao.cnf`） |

**⚠ 单实例约束（最重要）**：定时任务调度器与维度表缓存都在进程内，
**禁止** `--workers N`、禁止多副本部署，否则定时任务重复执行、任务日志互踩。

---

## 2. 环境要求

- Python ≥ 3.9（开发基线 3.10；`/bin/python3` 需满足此版本）
- 端口 8004 可用且 >1024（非 root 可监听）
- 服务器可访问：GitHub（拉代码）、cms/禅道数据库、`pms.hisunglobal.com`（定时任务脚本用）

版本确认：

```bash
/bin/python3 -V                 # >= 3.9
/bin/python3 -m pip -V          # pip 与该解释器对应
```

---

## 3. 首次部署

### 3.1 目录与代码

```bash
sudo mkdir -p /app/hbs/cms
sudo chown -R hbs:hbs /app/hbs
cd /app/hbs/cms
git clone https://github.com/DEVLHK/Soybean-backend.git
cd Soybean-backend
```

Git 授权（首次 clone/pull 需要输入）：用户名填 GitHub 账号，密码填 **Personal Access Token**（GitHub → Settings → Developer settings → Personal access tokens 生成，勾选 repo 读权限）。

记住凭据，之后 pull 不再询问：

```bash
git config --global credential.helper store
# 再执行一次 git pull 输入用户名+token，凭据落盘 ~/.git-credentials
```

### 3.2 安装依赖（无 venv，装到用户目录）

```bash
cd /app/hbs/cms/Soybean-backend
python3 -m pip install --user -r requirements.txt
```

- 报 `externally-managed-environment` 时追加 `--break-system-packages`
- 验证：`python3 -c "import fastapi, pandas, pymysql, requests, lxml.etree; print('deps OK')"`

### 3.3 数据库准备

- 修改 `config/database/mysql/*.cnf` 指向**生产库**（文件在 git 内，注意别被后续 pull 覆盖回 dev 值）
- 执行未落库的表结构变更（见第 7 节），例：

```sql
ALTER TABLE task_monitor_daily_stat
  ADD COLUMN due_yesterday int NOT NULL DEFAULT 0 COMMENT '上一日逾期任务数' AFTER overdue;
```

### 3.4 systemd 服务

创建 `/etc/systemd/system/cms.service`（**root 创建**，服务进程以 `User=hbs` 运行，两者不冲突）：

```bash
sudo tee /etc/systemd/system/cms.service > /dev/null <<'EOF'
[Unit]
Description=Soybean OMS Backend
After=network.target

[Service]
User=hbs
Environment=HOME=/home/hbs
WorkingDirectory=/app/hbs/cms/Soybean-backend/app
ExecStart=/bin/python3 -m uvicorn run_cms_app:cms_app --host 0.0.0.0 --port 8004
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

> 说明：用 `python3 -m uvicorn` 而非裸 `uvicorn` 命令，不依赖 PATH 且锁定解释器；
> 同时绕开 `run_cms_app.py` 中 `__main__` 分支的 `reload=True`（开发模式）。

### 3.5 启动与验证

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cms      # 开机自启 + 立即启动

sudo systemctl status cms            # Active: active (running)
curl http://127.0.0.1:8004/docs      # 返回 Swagger 页面即服务正常
```

启动日志确认定时任务注册完成：

```bash
sudo journalctl -u cms --since "5 min ago" | grep -E "scheduler jobs registered|启动调度器"
# 期望出现: scheduler jobs registered: N/N
```

---

## 4. 日常运维

### 4.1 更新发版

```bash
cd /app/hbs/cms/Soybean-backend && git reset --hard origin/main && git pull
python3 -m pip install --user -r requirements.txt   # 依赖有变时
sudo systemctl restart cms
```

重启即完成：定时任务自动重注册 + "运行中"残留运行记录自动回收，无需其他操作。

### 4.2 服务操作

```bash
sudo systemctl start cms      # 启动
sudo systemctl stop cms       # 停止（正在运行的定时任务子进程随进程结束）
sudo systemctl restart cms    # 重启
sudo journalctl -u cms -f     # 跟实时日志
```

---

## 5. 日志

| 日志 | 路径 | 轮转 |
|---|---|---|
| 服务主日志 | `<repo>/temp/log/consoles.log` | 按天切割，保留 7 天 |
| 定时任务输出 | `<repo>/app/schedule/temp/job_logs/{yyyyMMdd}/{run_log_id}.log` | 保留 30 天，引擎自动清理 |
| 任务运行历史（DB） | cms 库 `scheduler_job_run_log`（`output` 存尾部 1000 字符 + 完整日志文件路径） | — |
| systemd 标准输出 | `journalctl -u cms` | 系统 journal 管 |

---

## 6. 定时任务运维

- 配置在 cms 库 `scheduler_job` 表（脚本路径、调度周期、启停、日志级别）
- 启停：改 `enabled` 后需**重启服务**（或调用对应管理接口）生效
- 单任务超时上限 2 小时，超时强杀并记 status=3
- 任务日志级别：`scheduler_job.log_level` 注入子进程 `JOB_LOG_LEVEL`，脚本按此输出
- 脚本日志规范：统一 `from utils.script_logger import get_script_logger`

---

## 7. 数据库变更

表结构变更需在发版前于生产库执行，并在团队内同步 DDL 记录。近期变更：

| 日期 | 变更 |
|---|---|
| 2026-10-22 | `task_monitor_daily_stat` 增加 `due_yesterday int NOT NULL DEFAULT 0`（上一日逾期任务数） |

---

## 8. 配置文件清单

| 文件 | 内容 |
|---|---|
| `config/fastapi/config.yaml` | 监听地址/端口、上传目录 |
| `config/database/mysql/cms.cnf` | cms 业务库连接 |
| `config/database/mysql/zentao.cnf` | 禅道库连接（只读） |
| `config/database/ext_db_router.yaml` | 外部库路由 |
| `config/router/router.yaml` | 接口路由 → 服务函数映射 |

⚠ 以上数据库配置在 git 内：生产值与 dev 不同时，`git pull` 前确认本地差异，避免覆盖。

---

## 9. 常见问题

| 现象 | 处理 |
|---|---|
| `git pull` 每次要密码 | 见 3.1 凭据存储；token 过期（401）去 GitHub 重新生成 |
| vim 存 unit 报 `E212` | 用 `sudo vim` 或 `:w !sudo tee %` |
| pip 报 `externally-managed-environment` | 追加 `--break-system-packages` |
| 服务起不来，`journalctl` 报 `ModuleNotFoundError` | 依赖没装到运行用户的 site-packages：用 `hbs` 执行 3.2 |
| 端口被占 `Address already in use` | `ss -lntp \| grep 8004` 找到占用进程 |
| 定时任务没跑 | 确认 `scheduler_job.enabled=1` 且脚本路径存在；看 job_logs 当日目录 |
| 改了 zt_user/团队表前端没变 | 维度表缓存 TTL 300s，等 5 分钟或重启服务 |

---

## 10. 安全注意

- GitHub Token 等同密码：不进代码/聊天记录，泄露即在 GitHub 页面 Revoke
- `~/.git-credentials` 为明文，依赖服务器登录管控
- 定时任务脚本 `cbl_task_notification.py` 内 `TEST_BOT_KEY` 为测试机器人，接正式通知前替换为正式机器人 key
- 禅道库账号仅只读（read_pms），不要提权
