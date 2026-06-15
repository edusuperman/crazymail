# 问题：前端收不到邮件

## 现象

1. 后端 API `http://localhost:8000/api/v1/email/messages?email=xxx` 能正确返回邮件数据
2. 前端页面收件箱始终为空，从未显示过任何邮件
3. 前端有时会显示假的邮件数据（如来自 GitHub、Notion、Vercel 的假邮件），这些不是真实邮件

## 后端 API 返回格式（已确认正确）

### GET /api/v1/email/messages?email=xxx@yyy.com

```json
{
  "email": "xxx@yyy.com",
  "messages": [
    {
      "id": "uuid-string",
      "from_address": "sender@example.com",
      "from_name": "Sender Name",
      "subject": "Email Subject",
      "received_at": "2026-06-13T14:29:08.020184",
      "is_read": false,
      "has_attachments": false
    }
  ],
  "total": 1
}
```

### POST /api/v1/email/create

```json
{
  "address": "xxx@yyy.com",
  "username": "xxx",
  "domain": "yyy.com",
  "provider": "tempmailio"
}
```

### GET /api/v1/email/domains

```json
{
  "domains": ["bltiwd.com", "wnbaldwy.com", "bwmyga.com", "ozsaip.com", "yzcalo.com", "lnovic.com", "ruutukf.com", "gmeenramy.com"]
}
```

## 要求

1. **前端必须正确对接后端 API**，不要自己生成假数据
2. **API 失败时显示空收件箱**，不要显示 mock 数据
3. **邮箱地址必须持久化到 localStorage**，刷新页面后保持同一个邮箱
4. **每 5 秒自动刷新收件箱**，新邮件实时显示
5. **API 基础地址**：`http://localhost:8000`

## 验证方式

打开网站 → 复制显示的邮箱地址 → 从任意邮箱发一封测试邮件 → 等待 5-10 秒 → 邮件应自动显示在收件箱
