# Tempail.com 临时邮箱 API 逆向工程

## 📋 项目概述

本项目是对 [Tempail.com](https://tempail.com) 临时邮箱服务的完整API逆向工程，包含详细的API文档和功能完整的Python客户端实现。

**完成日期**: 2026-05-19  
**API类型**: REST API (PHP + Cookie会话)  
**状态**: ✅ 完成

## 📁 文件结构

```
20260519_tempail.com_REST-API/
├── README.md                          # 本文件
├── tempail_api_documentation.md       # 完整API文档（398行）
├── tempail_client.py                  # Python客户端（545行）
├── example_usage.py                   # 使用示例（304行）
└── tempail_main.json                  # 原始JavaScript代码
```

## 🎯 核心功能

### API端点

1. **检查邮件** - `POST /ru/api/kontrol/`
   - 检查收件箱中的新邮件
   - 10秒轮询间隔
   - 返回HTML格式的邮件列表

2. **读取邮件** - `POST /ru/api/oku/`
   - 读取指定邮件的完整内容
   - 支持HTML和纯文本格式
   - 包含附件信息

3. **删除邮件** - `POST /ru/api/sil/`
   - 删除指定的邮件
   - 立即生效

4. **销毁邮箱** - `POST /ru/api/yoket/`
   - 永久删除当前临时邮箱
   - 清除所有会话信息

5. **获取QR码** - `POST /ru/api/sifre/`
   - 生成邮箱地址的QR码
   - 便于移动设备访问

6. **联系表单** - `POST /ru/api/iletisim/`
   - 发送联系消息
   - 需要reCAPTCHA验证

## 🔐 认证机制

Tempail.com 使用基于Cookie的会话管理：

```python
# 会话Cookie
PHPSESSID: PHP会话ID
oturum: 会话标识符（土耳其语"会话"）
tarih: 时间戳
```

### 初始化流程

1. 访问主页获取会话Cookie
2. 从页面提取邮箱地址
3. 保存会话信息用于后续请求

## 🚀 快速开始

### 安装依赖

```bash
pip install requests beautifulsoup4
```

### 基础使用

```python
from tempail_client import TempailClient

# 创建客户端
client = TempailClient(language="ru")

# 初始化并获取邮箱
info = client.initialize()
print(f"邮箱地址: {info['email']}")

# 检查收件箱
emails = client.check_inbox()
for email in emails:
    print(f"发件人: {email['from']}")
    print(f"主题: {email['subject']}")

# 读取第一封邮件
if emails:
    content = client.read_email(emails[0]['id'], emails[0]['id'])
    print(f"正文: {content['body_text']}")
```

### 运行示例

```bash
# 运行主客户端
python tempail_client.py

# 运行使用示例
python example_usage.py
```

## 📖 详细文档

完整的API文档请查看 [`tempail_api_documentation.md`](./tempail_api_documentation.md)，包含：

- 所有API端点的详细说明
- 请求/响应格式
- 认证机制
- HTML解析方法
- 错误处理
- 安全注意事项
- 与其他服务的对比

## 💡 使用示例

### 示例1: 等待新邮件

```python
client = TempailClient()
info = client.initialize()
print(f"邮箱: {info['email']}")

# 等待新邮件（60秒超时）
new_email = client.wait_for_email(timeout=60, interval=10)
if new_email:
    print(f"收到: {new_email['subject']}")
```

### 示例2: 持续监控

```python
def on_new_email(emails):
    for email in emails:
        print(f"新邮件: {email['subject']}")

client = TempailClient()
client.initialize()

# 持续监控（按Ctrl+C停止）
client.monitor_inbox(callback=on_new_email, interval=10)
```

### 示例3: 获取QR码

```python
client = TempailClient()
client.initialize()

qr_info = client.get_qr_code()
print(f"QR码: {qr_info['qr_code_url']}")
```

### 示例4: 销毁邮箱

```python
client = TempailClient()
client.initialize()

# 使用完毕后销毁
if client.destroy_mailbox():
    print("邮箱已销毁")
```

## 🔍 技术特点

### 优势

✅ **Cookie会话管理** - 简单可靠的认证方式  
✅ **10秒轮询** - 平衡的检查频率  
✅ **多语言支持** - 支持多种界面语言  
✅ **QR码功能** - 便于移动设备访问  
✅ **邮箱销毁** - 可主动删除邮箱  
✅ **Cloudflare保护** - 增强安全性  

### 限制

⚠️ **会话时长** - 1小时后过期  
⚠️ **HTML响应** - 需要解析HTML获取数据  
⚠️ **无API密钥** - 依赖Cookie会话  

## 📊 API对比

| 特性 | Tempail.com | TemporaryMail.com | Tempimail.org |
|------|-------------|-------------------|---------------|
| 认证方式 | Cookie会话 | 密钥系统 | CSRF Token |
| 轮询间隔 | 10秒 | 5秒 | 20秒 |
| 响应格式 | HTML | JSON | HTML |
| 会话时长 | 1小时 | 无限制 | 2小时 |
| QR码 | ✅ | ❌ | ❌ |
| 邮箱销毁 | ✅ | ❌ | ❌ |

## 🛠️ 开发信息

### 技术栈

- **后端**: PHP
- **前端**: jQuery
- **CDN**: Cloudflare
- **分析**: Google Analytics, Yandex Metrica

### API端点模式

所有API端点遵循以下模式：
```
https://tempail.com/{language}/api/{action}/
```

其中：
- `{language}`: 语言代码（ru, en, de等）
- `{action}`: 操作名称（kontrol, oku, sil等）

### 请求格式

```http
POST /ru/api/kontrol/ HTTP/1.1
Host: tempail.com
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=xxx; oturum=xxx

oturum=xxx&tarih=xxx&geri_don=xxx
```

## ⚠️ 注意事项

1. **遵守使用条款** - 仅用于合法目的
2. **速率限制** - 建议10秒轮询间隔
3. **会话管理** - 注意1小时过期时间
4. **错误处理** - 实现适当的重试机制
5. **Cloudflare** - 可能需要处理挑战

## 🔧 故障排除

### 问题1: 会话过期

**症状**: 请求返回错误或重定向到主页  
**解决**: 重新调用 `initialize()` 获取新会话

### 问题2: 无法解析邮件列表

**症状**: `check_inbox()` 返回空列表  
**解决**: 检查HTML结构是否变化，更新解析逻辑

### 问题3: Cloudflare挑战

**症状**: 请求被Cloudflare拦截  
**解决**: 使用真实浏览器User-Agent，或实现挑战解决

## 📈 性能优化

1. **复用会话** - 避免频繁初始化
2. **批量操作** - 一次性处理多封邮件
3. **缓存结果** - 减少重复请求
4. **异步处理** - 使用异步IO提高效率

## 🔐 安全建议

1. **不要存储敏感信息** - 临时邮箱不安全
2. **定期销毁邮箱** - 使用完毕后清理
3. **验证邮件来源** - 警惕钓鱼邮件
4. **保护会话Cookie** - 避免泄露

## 📝 更新日志

### 2026-05-19
- ✅ 完成API逆向工程
- ✅ 创建Python客户端
- ✅ 编写完整文档
- ✅ 提供使用示例

## 🤝 贡献

发现问题或有改进建议？欢迎：
- 报告Bug
- 提交Pull Request
- 分享使用经验

## 📄 许可

本项目仅用于教育和研究目的。使用时请遵守 Tempail.com 的服务条款。

## 🔗 相关链接

- [Tempail.com 官网](https://tempail.com)
- [API文档](./tempail_api_documentation.md)
- [Python客户端](./tempail_client.py)
- [使用示例](./example_usage.py)

---

**免责声明**: 本项目通过逆向工程获得，仅供学习研究。使用本项目产生的任何后果由使用者自行承担。