# 闲鱼自动回复管理系统 - 安全加固版

[![GitHub](https://img.shields.io/badge/GitHub-Otis0408%2Fxianyu--auto--reply--security--fix-blue?logo=github)](https://github.com/Otis0408/xianyu-auto-reply-security-fix)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-源码构建-blue?logo=docker)](#-快速开始)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://www.python.org/)
[![Usage](https://img.shields.io/badge/Usage-仅供学习-red.svg)](#-版权声明与使用条款)

---

## 安全修复说明

本项目基于 [GuDong2003/xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix) 进行安全加固，共修复 **12个安全漏洞**。

> 原项目存在多个严重安全问题，包括将用户Cookie明文发送到第三方服务器、硬编码后门密钥、混淆代码exec执行等。**强烈建议使用本安全加固版本。**

### 漏洞修复清单

| 等级 | 漏洞描述 | 修复方式 |
|:----:|---------|---------|
| **P0** | Cookie通过HTTP明文发送到第三方IP `119.29.64.68` | 禁用该接口，阻止凭据外泄 |
| **P1** | 硬编码API密钥 `xianyu_api_secret_2024` | 改为环境变量配置 |
| **P1** | 测试密钥后门 `zhinina_test_key` 可绕过认证 | 删除后门 |
| **P1** | 默认弱密码 `admin123` 且前端明文展示 | 未配置时自动生成随机密码 |
| **P1** | 系统设置接口普通用户可修改 | 加管理员权限校验 |
| **P1** | 备份导入存在SQL注入（列名拼接） | 正则验证 + 引号包裹列名 |
| **P1** | 自动更新存在路径穿越漏洞 | resolve()路径边界检查 |
| **P1** | 两个文件含混淆代码通过exec()执行，无法审计 | 替换为安全占位实现 |
| **P2** | X-Forwarded-For可伪造，绕过速率限制 | 改用直连IP |
| **P2** | 默认绑定0.0.0.0，直接暴露公网 | 改为127.0.0.1 |
| **P2** | /health端点泄露CPU、内存等系统信息 | 仅返回健康状态 |
| **P2** | 硬编码第三方回调URL `116.196.116.76` | 默认值改为空 |

详细技术分析请参阅 [SECURITY_FIXES.md](SECURITY_FIXES.md)。

### 开箱即用

无需手动配置密码和密钥，系统首次启动时会自动生成随机值，并以醒目的方式回显到终端：

```
==========================================================
       闲鱼管理系统 - 安全加固版 已启动
==========================================================
  访问地址:     http://127.0.0.1:8090
  管理员账号:   admin
  管理员密码:   aB3xK9mP_qR7wZ2y
  API 密钥:     dF5hJ8nQ...tV4x
----------------------------------------------------------
  提示: 可通过环境变量 ADMIN_PASSWORD 自定义密码
  提示: 首次登录后建议在管理界面修改密码
==========================================================
```

如需自定义，可通过环境变量覆盖：

```bash
# 可选配置（不设置则自动生成随机值）
export ADMIN_PASSWORD="你的强密码"                          # 管理后台登录密码
export JWT_SECRET_KEY="$(openssl rand -base64 32)"          # 会话签名密钥
export XIANYU_API_SECRET_KEY="$(openssl rand -base64 32)"   # QQ机器人等外部系统调用发消息接口的认证密钥，不用可忽略
```

---

## 项目概述

一个功能完整的闲鱼管理系统，采用现代化的技术架构，支持多用户、多账号管理，具备智能回复、自动发货、自动确认发货、商品管理等企业级功能。系统基于Python异步编程，使用FastAPI提供RESTful API，SQLite数据库存储，支持Docker一键部署。

> **重要提示：本项目仅供学习研究使用，严禁商业用途！使用前请仔细阅读[版权声明](#-版权声明与使用条款)。**

## 技术架构

### 核心技术栈
- **后端框架**: FastAPI + Uvicorn + Python 3.11+ 异步编程
- **数据库**: SQLite 3 + 多用户数据隔离 + 自动迁移
- **前端**: Bootstrap 5 + Vanilla JavaScript + Chart.js + 响应式设计
- **通信协议**: WebSocket + SSE + RESTful API + 实时通信
- **自动化能力**: Playwright + DrissionPage + 浏览器自动化
- **部署方式**: Docker + Docker Compose + Nginx（可选）+ 一键部署
- **日志系统**: Loguru + 文件轮转 + 实时收集
- **安全认证**: Bearer Token + 图形验证码 + 邮箱验证 + 权限控制

### 系统架构特点
- **模块化架构**: 按账号、订单、发货、通知、日志等模块拆分，易于维护和扩展
- **异步处理**: 基于 asyncio 的高性能异步处理
- **多用户隔离**: 完整的数据隔离和权限控制
- **容器化部署**: Docker 容器化部署，支持一键启动
- **实时监控**: WebSocket + SSE 实时通信和状态监控
- **稳定性保障**: 自动重连、异常恢复、自动迁移、日志轮转

## 核心特性

### 多用户系统
- **用户注册登录** - 支持邮箱验证码注册、用户名/邮箱登录和图形验证码保护
- **数据完全隔离** - 每个用户的数据独立存储，互不干扰
- **权限管理** - 严格的用户权限控制和 Bearer Token 认证
- **安全保护** - 防暴力破解、会话管理、安全日志

### 多账号管理
- **多账号支持** - 每个用户可管理多个闲鱼账号
- **独立运行** - 每个账号独立启用、停用和刷新
- **实时状态** - 账号连接状态和运行配置可实时查看

### 智能回复系统
- **关键词匹配** - 支持通用关键词和商品专属关键词回复
- **AI智能回复** - 支持上下文理解和多种兼容模型接口
- **图片关键词** - 支持图片关键词和图片自动发送
- **优先级策略** - 指定商品回复 > 商品专用关键词 > 通用关键词 > 默认回复 > AI回复

### 自动发货功能
- **智能匹配** - 基于商品信息自动匹配发货规则
- **多规格支持** - 支持同一商品的不同规格自动匹配
- **多种发货方式** - 支持文字、批量数据、API、图片等发货方式
- **防重复处理** - 智能防重复发货和防重复确认

### 商品管理
- **自动收集** - 消息触发时自动收集商品信息
- **商品搜索** - 基于 Playwright 获取真实闲鱼商品数据
- **多规格配置** - 支持多规格商品配置和管理

### 系统监控
- **实时日志** - 完整的操作日志记录、查看和导出
- **健康检查** - 服务状态健康检查
- **数据备份恢复** - 支持用户备份恢复和管理员数据库备份

## 快速开始

**推荐方式**：使用 Docker Compose 从源码构建并启动。

### 方式一：Docker Compose 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/Otis0408/xianyu-auto-reply-security-fix.git
cd xianyu-auto-reply-security-fix

# 2. 启动服务（密码和密钥会自动生成，查看日志获取）
docker compose up -d --build

# 3. 查看自动生成的管理员密码
docker compose logs | grep "管理员密码"

# 4. 访问系统
# http://localhost:9000
```

国内用户使用国内构建配置：
```bash
docker compose -f docker-compose-cn.yml up -d --build
# http://localhost:8000
```

### 方式二：本地运行

```bash
# 1. 克隆项目
git clone https://github.com/Otis0408/xianyu-auto-reply-security-fix.git
cd xianyu-auto-reply-security-fix

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium
playwright install-deps chromium  # 仅 Linux 需要

# 5. 启动系统（密码会自动生成，查看终端输出获取）
python Start.py

# 6. 访问系统
# http://localhost:8090
```

> 管理员账号：`admin`，密码在启动日志中显示。也可通过 `ADMIN_PASSWORD` 环境变量自定义。

> 本地运行请确保已安装 Node.js，否则 `PyExecJS` 相关功能无法正常使用。

### 环境要求

- **Python**: 3.11+
- **Node.js**: 16+（用于 PyExecJS 执行 JavaScript）
- **系统**: Windows / Linux / macOS
- **架构**: x86_64 (amd64) / ARM64 (aarch64)
- **Docker**: 20.10+（Docker 部署）
- **Docker Compose**: 2.0+（Docker 部署）
- **浏览器依赖**: Playwright Chromium（本地运行需要安装）
- **资源建议**: 建议 2GB+ 内存，预留 10GB+ 存储空间

### 环境变量配置

```bash
# Web 服务（安全加固后默认仅本地访问）
API_HOST=127.0.0.1     # 如需外部访问，请配合反向代理使用
API_PORT=8090

# 安全相关（可选，不设置则自动生成随机值，启动时回显到终端）
ADMIN_PASSWORD=你的强密码              # 管理后台登录密码
JWT_SECRET_KEY=随机密钥                # 会话Token签名密钥
XIANYU_API_SECRET_KEY=API密钥          # 外部系统（如QQ机器人）调用发消息接口的认证密钥，不用可忽略

# 数据存储
DB_PATH=/app/data/xianyu_data.db

# SQL 日志
SQL_LOG_ENABLED=true
SQL_LOG_LEVEL=INFO

# 敏感信息加密
SECRET_ENCRYPTION_KEY=your-secret-key
```

> 其他运行参数（如 WebSocket、心跳、自动回复等）主要在 `global_config.yml` 和 Web 管理界面中配置。

### 访问系统

部署完成后：

- **Web管理界面**：
  - Docker Compose 默认配置: http://localhost:9000
  - Docker Compose 国内配置: http://localhost:8000
  - 本地运行: http://localhost:8090
- **管理员账号**：`admin`，密码查看启动日志或环境变量 `ADMIN_PASSWORD`
- **API文档**: 对应地址 + `/docs`

## 系统架构

```text
┌─────────────────────────────────────────┐
│       Web 界面 (FastAPI + Static)        │
│          用户管理 + 功能界面               │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│             CookieManager               │
│           多账号任务与状态管理             │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│          XianyuLive (多实例)             │
│        WebSocket 连接 + 消息处理          │
└──────────────┬──────────────┬───────────┘
               │              │
┌──────────────▼───────┐ ┌────▼──────────────┐
│    AIReplyEngine     │ │ FileLogCollector  │
│     AI 回复与上下文    │ │   实时日志与统计    │
└──────────────┬───────┘ └────┬──────────────┘
               │              │
┌──────────────▼──────────────▼───────────┐
│              SQLite 数据库               │
│      用户数据 + 商品信息 + 配置数据         │
└─────────────────────────────────────────┘
```

## 常见问题

### 1. 端口被占用
- **Docker Compose**：修改 `docker-compose.yml` 或 `docker-compose-cn.yml` 中的端口映射
- **本地运行**：修改 `API_PORT` 环境变量，或调整 `global_config.yml` 中的 `AUTO_REPLY.api.port`

### 2. 数据库连接失败
检查 `data/` 目录和数据库文件权限，确保应用有读写权限；如使用自定义路径，确认 `DB_PATH` 配置正确。

### 3. WebSocket连接失败
检查网络和防火墙设置，并确认闲鱼账号 Cookie 仍然有效。

### 4. Docker容器启动失败
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 特别鸣谢

本项目参考了以下开源项目：

- **[XianYuApis](https://github.com/cv-cat/XianYuApis)** - 提供了闲鱼API接口的技术参考
- **[XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent)** - 提供了自动化处理的实现思路
- **[myfish](https://github.com/Kaguya233qwq/myfish)** - 提供了扫码登录的实现思路

## 版权声明与使用条款

### 项目来源

- **原始项目**：[zhinianboke-new/xianyu-auto-reply](https://github.com/zhinianboke-new/xianyu-auto-reply)
- **二开项目**：[GuDong2003/xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix)
- **安全加固版（本仓库）**：[Otis0408/xianyu-auto-reply-security-fix](https://github.com/Otis0408/xianyu-auto-reply-security-fix)

### 使用限制

- **禁止商业使用** - 不得将本项目或其衍生内容用于商业用途
- **禁止违法使用** - 不得将本项目用于任何违法违规活动
- **禁止滥用服务** - 不得利用本项目进行骚扰、欺诈或其他不当行为

### 免责声明

本项目按"现状"提供，不提供任何明示或暗示的保证；因使用本项目产生的风险、损失或责任，由使用者自行承担。本安全加固版仅修复了代码审计中发现的已知漏洞，不保证涵盖所有安全问题。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Otis0408/xianyu-auto-reply-security-fix&type=Date)](https://www.star-history.com/#Otis0408/xianyu-auto-reply-security-fix&Date)
