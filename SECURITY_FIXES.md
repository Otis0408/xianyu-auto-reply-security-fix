# Security Fixes / 安全修复说明

本项目基于 [GuDong2003/xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix) 二次开发，专注于修复原项目中发现的安全漏洞。

## 修复的漏洞列表

### P0 - 严重 (Critical)

#### 1. Cookie 明文泄露到第三方服务器
- **文件**: `XianyuAutoAsync.py` (`_call_comment_api`)
- **问题**: 好评接口将用户的闲鱼Cookie通过 **HTTP明文** 发送到硬编码的第三方IP `119.29.64.68:8081`，该IP非闲鱼官方服务器
- **风险**: 攻击者（或该IP的控制者）可直接获取用户Cookie，完全接管闲鱼账号
- **修复**: 禁用该接口，返回错误提示。如需好评功能，请在本地安全实现

### P1 - 高危 (High)

#### 2. 硬编码API密钥和测试后门
- **文件**: `reply_server.py`
- **问题**:
  - `API_SECRET_KEY = "xianyu_api_secret_2024"` 硬编码密钥
  - `zhinina_test_key` 测试密钥可绕过所有认证
  - Docker Compose 中 `JWT_SECRET_KEY` 默认值为 `default-secret-key`
- **风险**: 攻击者使用已知密钥调用发消息接口，冒充卖家发送任意消息
- **修复**: 移除硬编码密钥，改为环境变量配置；移除测试密钥后门；Docker Compose 强制要求设置密钥

#### 3. 默认弱密码 admin123
- **文件**: `reply_server.py`, `db_manager.py`, `login.html`, `docker-compose*.yml`
- **问题**: 管理员默认密码为 `admin123`，并在前端登录页面明文展示
- **风险**: 任何人都可以使用默认密码登录管理后台
- **修复**: 未设置环境变量时自动生成随机密码并在启动日志中显示；Docker Compose 强制要求设置密码

#### 4. 系统设置接口缺少管理员权限校验
- **文件**: `reply_server.py` (`PUT /system-settings/{key}`)
- **问题**: 任何已登录用户（包括普通用户）都可以修改系统设置
- **风险**: 普通用户可篡改系统配置，包括API密钥等敏感设置
- **修复**: 改为 `verify_admin_token` 依赖，仅管理员可修改

#### 5. SQL注入 - 备份导入
- **文件**: `db_manager.py` (`import_backup`)
- **问题**: 备份文件中的列名直接拼接到SQL语句中，未做任何验证
- **风险**: 攻击者构造恶意备份文件，通过列名注入SQL语句，读取/修改/删除数据库任意数据
- **修复**: 添加列名正则验证（只允许 `[a-zA-Z_][a-zA-Z0-9_]*`），使用双引号包裹列名

#### 6. 路径穿越 - 自动更新
- **文件**: `auto_updater.py` (`apply_updates`)
- **问题**: 更新文件的路径直接来自远程清单，未验证是否在应用目录内
- **风险**: 恶意更新服务器可通过 `../../etc/crontab` 等路径覆盖系统任意文件
- **修复**: 添加 `resolve()` 路径规范化校验，确保目标路径在 `app_dir` 内

#### 7. 混淆代码 + exec() 执行
- **文件**: `secure_confirm_ultra.py`, `secure_freeshipping_ultra.py`
- **问题**: 文件包含多层混淆代码（hex反转 -> bytes -> base64 -> zlib -> exec()），无法审计实际执行内容
- **风险**: 可能包含恶意后门、数据窃取、远程控制等任意恶意行为
- **修复**: 完全移除混淆代码，替换为安全的占位实现。项目中已有对应的明文解密版本可用

### P2 - 中危 (Medium)

#### 8. IP地址欺骗绕过速率限制
- **文件**: `reply_server.py`
- **问题**: 使用 `X-Forwarded-For` 头作为客户端IP，该头可被攻击者任意伪造
- **风险**: 攻击者通过伪造IP绕过登录失败次数限制和IP封禁，进行暴力破解
- **修复**: 优先使用 `request.client.host` 直连IP

#### 9. 默认绑定 0.0.0.0
- **文件**: `Start.py`, `global_config.yml`
- **问题**: 服务默认监听所有网络接口，直接暴露到公网
- **风险**: 未经防火墙/反向代理保护的管理后台直接可从公网访问
- **修复**: 默认绑定 `127.0.0.1`，需外部访问请通过反向代理或显式配置

#### 10. 健康检查端点信息泄露
- **文件**: `reply_server.py` (`/health`)
- **问题**: 无认证的健康检查端点返回CPU使用率、内存信息、内部服务状态等详细信息
- **风险**: 攻击者可利用这些信息进行针对性攻击
- **修复**: 仅返回 `{"status": "healthy"}`，移除所有内部细节

#### 11. 调试端点权限不足
- **文件**: `reply_server.py` (`/debug/keywords-table-info`)
- **问题**: 调试端点仅需普通用户登录即可访问，暴露数据库表结构
- **修复**: 改为管理员权限

#### 12. 硬编码第三方回调URL
- **文件**: `config.py`
- **问题**: `YIFAN_API` 默认回调URL指向外部IP `116.196.116.76`
- **修复**: 默认值改为空，需通过配置文件显式设置

## 部署安全建议

1. **必须设置环境变量**:
   ```bash
   export ADMIN_PASSWORD="你的强密码"
   export JWT_SECRET_KEY="$(openssl rand -base64 32)"
   export XIANYU_API_SECRET_KEY="$(openssl rand -base64 32)"
   ```

2. **使用反向代理**: 不要直接将服务暴露到公网，使用 nginx 等反向代理并配置 HTTPS

3. **防火墙**: 仅开放必要端口（如 443），关闭直接访问后端服务的端口

4. **定期更新Cookie**: Cookie 是你的闲鱼身份凭证，不要分享给任何第三方服务

## 免责声明

本安全修复基于代码审计发现，可能未涵盖所有安全问题。建议在生产环境中进行专业的安全评估。
