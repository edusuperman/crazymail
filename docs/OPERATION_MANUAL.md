# tempmails.top 操作手册
# 版本：v1.0 | 2026-06-20

## ════════════════════════════════════════════
## 项目概述
## ════════════════════════════════════════════

**tempmails.top** 是一个免费临时邮箱服务，用户可以：
- 生成一次性邮箱地址
- 接收验证邮件
- 保护真实邮箱隐私

**技术栈**：
- 前端：TanStack Start + shadcn/ui
- 后端：FastAPI (Python)
- 邮件 API：Temp-Mail.io
- 部署：Vercel

---

## ════════════════════════════════════════════
## 用户操作流程
## ════════════════════════════════════════════

### 1. 访问网站

打开浏览器，访问 https://tempmails.top

### 2. 获取临时邮箱

页面加载后会自动生成一个临时邮箱地址（如 `abc123@bltiwd.com`）。

**操作按钮**：
- **Copy**：复制邮箱地址到剪贴板
- **Random**：生成新的随机邮箱
- **Change**：自定义邮箱用户名或域名
- **Delete**：删除当前邮箱

### 3. 使用邮箱

将临时邮箱地址粘贴到需要填写邮箱的网站：
- 注册账号
- 下载资源
- 接收验证码

### 4. 查看收件箱

邮件会自动显示在收件箱中：
- **Inbox** 标签：显示所有收到的邮件
- **Saved** 标签：显示已保存的邮件
- **Refresh** 按钮：手动刷新收件箱

### 5. 查看邮件详情

点击邮件列表中的邮件，可以查看：
- 发件人
- 主题
- 邮件内容

### 6. 保存邮件

点击邮件的保存按钮，将邮件移到 "Saved" 标签。

---

## ════════════════════════════════════════════
## 高级功能
## ════════════════════════════════════════════

### 自定义邮箱

点击 **Change** 按钮，可以：
1. 输入自定义用户名（如 `myname`）
2. 选择域名（如 `bltiwd.com`）
3. 点击 **Confirm** 确认

### 多语言支持

点击右上角的语言按钮，支持：
- 🇺🇸 English
- 🇨🇳 中文
- 🇯🇵 日本語
- 🇰🇷 한국어
- 🇪🇸 Español
- 🇫🇷 Français
- 🇩🇪 Deutsch

---

## ════════════════════════════════════════════
## API 文档
## ════════════════════════════════════════════

### 基础 URL
```
https://api.tempmails.top
```

### 端点

#### 1. 获取可用域名
```
GET /api/v1/email/domains
```
**响应**：
```json
{
  "domains": ["bltiwd.com", "wnbaldwy.com", ...]
}
```

#### 2. 创建邮箱
```
POST /api/v1/email/create
```
**请求体**（可选）：
```json
{
  "username": "myname",
  "domain": "bltiwd.com"
}
```
**响应**：
```json
{
  "address": "myname@bltiwd.com",
  "username": "myname",
  "domain": "bltiwd.com",
  "provider": "tempmailio"
}
```

#### 3. 获取消息
```
GET /api/v1/email/messages?email=xxx@yyy.com
```
**响应**：
```json
{
  "email": "xxx@yyy.com",
  "messages": [
    {
      "id": "uuid",
      "from_address": "sender@example.com",
      "from_name": "Sender Name",
      "subject": "Email Subject",
      "received_at": "2026-06-20T12:00:00",
      "is_read": false,
      "has_attachments": false
    }
  ],
  "total": 1
}
```

#### 4. 获取消息详情
```
GET /api/v1/email/messages/{message_id}
```

#### 5. 标记已读
```
PATCH /api/v1/email/messages/{message_id}/read
```

#### 6. 健康检查
```
GET /health
```

---

## ════════════════════════════════════════════
## 部署信息
## ════════════════════════════════════════════

### Vercel 项目

| 项目 | 域名 | 说明 |
|------|------|------|
| crazymail | tempmails.top | 前端 |
| crazymail-api | api.tempmails.top | 后端 |

### 环境变量

**前端**：
```
VITE_API_BASE=https://api.tempmails.top
```

**后端**：
```
见 .env 文件（不在代码仓库中）
```

### 部署命令

**前端**：
```bash
cd sites/site-01/frontend
vercel --prod --yes --name crazymail
```

**后端**：
```bash
vercel --prod --yes --name crazymail-api
```

---

## ════════════════════════════════════════════
## 常见问题
## ════════════════════════════════════════════

### Q: 邮件收不到？
A: 可能原因：
1. 发件方屏蔽了一次性邮箱域名
2. 邮件还在发送中（等待 30 秒）
3. 邮箱已过期（10 分钟有效期）

### Q: 如何延长邮箱有效期？
A: 当前版本不支持，Premium 功能将支持 24 小时保留。

### Q: 可以发送邮件吗？
A: 不可以，临时邮箱仅支持接收邮件。

### Q: 如何删除邮件？
A: Temp-Mail.io API 不支持删除邮件，需等待自动过期（10 分钟）。

---

## ════════════════════════════════════════════
## 联系方式
## ════════════════════════════════════════════

- 邮箱：hello@tempmail.pro
- 网站：https://tempmails.top
