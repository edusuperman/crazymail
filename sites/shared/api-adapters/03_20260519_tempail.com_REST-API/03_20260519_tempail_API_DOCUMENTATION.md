# Tempail.com 临时邮箱 REST API 文档

## 概述

Tempail.com 是一个提供临时邮箱服务的网站，使用基于会话的认证机制。本文档详细说明了其API的使用方法。

**基础URL**: `https://tempail.com`

**语言支持**: 支持多语言路径（如 `/ru/`, `/en/` 等）

## 认证机制

### 会话管理

Tempail.com 使用Cookie进行会话管理：

1. **PHPSESSID**: PHP会话ID
2. **oturum**: 会话标识符（土耳其语"会话"）
3. **tarih**: 时间戳（土耳其语"日期"）

### 获取会话

访问主页时，服务器会自动设置这些Cookie：

```http
GET https://tempail.com/ru/
```

响应头中会包含：
```
Set-Cookie: PHPSESSID=xxx; path=/
Set-Cookie: oturum=xxx; expires=...; path=/
```

## API端点

### 1. 检查新邮件

**端点**: `POST /ru/api/kontrol/`

**描述**: 检查是否有新邮件到达

**请求参数**:
```
oturum: 会话ID（从Cookie获取）
tarih: 时间戳（Unix时间戳）
geri_don: 返回URL（通常是inbox URL）
```

**请求示例**:
```http
POST /ru/api/kontrol/ HTTP/1.1
Host: tempail.com
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=xxx; oturum=2nnkJb

oturum=2nnkJb&tarih=1779200084&geri_don=https%3A%2F%2Ftempail.com%2Fru%2F
```

**响应**:
- 成功时返回HTML片段，包含邮件列表
- 304状态码表示没有新邮件
- 200状态码表示有更新

**轮询间隔**: 10秒

### 2. 读取邮件

**端点**: `POST /ru/api/oku/`

**描述**: 读取特定邮件的内容

**请求参数**:
```
oturum: 会话ID
veri[0]: 邮件ID（第一个参数）
veri[1]: 邮件序号（第二个参数）
```

**请求示例**:
```http
POST /ru/api/oku/ HTTP/1.1
Host: tempail.com
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=xxx; oturum=2nnkJb

oturum=2nnkJb&veri[0]=mail_id&veri[1]=mail_index
```

**响应**: 返回HTML格式的邮件内容

### 3. 删除邮件

**端点**: `POST /ru/api/sil/`

**描述**: 删除指定的邮件

**请求参数**:
```
oturum: 会话ID
veri[0]: 邮件ID
veri[1]: 邮件序号
```

**请求示例**:
```http
POST /ru/api/sil/ HTTP/1.1
Host: tempail.com
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=xxx; oturum=2nnkJb

oturum=2nnkJb&veri[0]=mail_id&veri[1]=mail_index
```

### 4. 销毁邮箱

**端点**: `POST /ru/api/yoket/`

**描述**: 永久删除当前临时邮箱

**请求参数**:
```
oturum: 会话ID
```

**请求示例**:
```http
POST /ru/api/yoket/ HTTP/1.1
Host: tempail.com
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=xxx; oturum=2nnkJb

oturum=2nnkJb
```

**响应**: JSON格式
```json
{
  "hata": "yok"  // "yok"表示成功
}
```

### 5. 获取QR码

**端点**: `POST /ru/api/sifre/`

**描述**: 获取邮箱地址的QR码

**请求参数**:
```
oturum: 会话ID
```

**响应**: JSON格式
```json
{
  "url_kare_kod": "QR码图片URL",
  "url": "邮箱地址URL"
}
```

### 6. 联系表单

**端点**: `POST /ru/api/iletisim/`

**描述**: 发送联系消息

**请求参数**:
```
oturum: 会话ID
veri[0]: 姓名
veri[1]: 邮箱
veri[2]: 主题
veri[3]: 消息内容
captcha: reCAPTCHA响应
```

**响应**: JSON格式
```json
{
  "durum": "1",  // 1=成功, 0=失败
  "bilgi": "消息文本"
}
```

## 工作流程

### 初始化会话

1. 访问主页获取会话Cookie
2. 从页面提取邮箱地址和会话信息
3. 保存 `oturum` 和 `PHPSESSID` 用于后续请求

### 检查邮件

1. 每10秒调用 `/api/kontrol/` 端点
2. 解析返回的HTML获取邮件列表
3. 提取邮件ID、发件人、主题、时间等信息

### 读取邮件

1. 使用邮件ID和序号调用 `/api/oku/`
2. 解析返回的HTML获取邮件正文
3. 提取附件信息（如果有）

### 删除邮件

1. 调用 `/api/sil/` 删除指定邮件
2. 邮件从列表中移除

## HTML解析

### 邮件列表格式

```html
<li id="mail_123" class="mail-item">
  <div class="gonderen">发件人</div>
  <div class="baslik">主题</div>
  <div class="tarih">时间</div>
</li>
```

### 邮件内容格式

```html
<div id="eposta_oku">
  <div class="mail-header">
    <div class="from">发件人</div>
    <div class="subject">主题</div>
    <div class="date">日期</div>
  </div>
  <div class="mail-body">
    邮件正文（HTML或纯文本）
  </div>
</div>
```

## 错误处理

### HTTP状态码

- **200**: 成功
- **304**: 未修改（没有新邮件）
- **400**: 错误请求
- **500**: 服务器错误

### 错误响应

当发生错误时，JavaScript会显示错误消息并可能重定向到主页。

## 安全注意事项

1. **会话过期**: 会话在1小时后过期
2. **Cookie安全**: 使用HTTPS传输Cookie
3. **CSRF保护**: 使用会话ID作为CSRF令牌
4. **Cloudflare保护**: 网站受Cloudflare保护，可能需要处理挑战

## 限制

1. **轮询频率**: 建议10秒间隔
2. **会话时长**: 1小时
3. **邮件保留**: 邮件在一定时间后自动删除
4. **并发限制**: 未明确说明

## 技术栈

- **后端**: PHP
- **前端**: jQuery
- **CDN**: Cloudflare
- **分析**: Google Analytics, Yandex Metrica

## 示例代码

### JavaScript示例

```javascript
// 检查邮件
function kontrol() {
  $.post(url_api_kontrol, {
    oturum: oturum,
    tarih: tarih,
    geri_don: url_inbox
  }, function(data) {
    $('#epostalar').html(data);
  });
}

// 读取邮件
function mail_oku(mail_id, mail_index) {
  var veri = [mail_id, mail_index];
  $.post(url_api_oku, {
    oturum: oturum,
    veri: veri
  }, function(data) {
    $('#eposta_oku').html(data);
  });
}

// 删除邮件
function sil_posta(mail_id, mail_index) {
  var veri = [mail_id, mail_index];
  $.post(url_api_sil, {
    oturum: oturum,
    veri: veri
  }, function(data) {
    anasayfa();
  });
}
```

### cURL示例

```bash
# 获取会话
curl -c cookies.txt https://tempail.com/ru/

# 检查邮件
curl -b cookies.txt -X POST \
  https://tempail.com/ru/api/kontrol/ \
  -d "oturum=2nnkJb&tarih=1779200084&geri_don=https://tempail.com/ru/"

# 读取邮件
curl -b cookies.txt -X POST \
  https://tempail.com/ru/api/oku/ \
  -d "oturum=2nnkJb&veri[0]=mail_id&veri[1]=1"

# 删除邮件
curl -b cookies.txt -X POST \
  https://tempail.com/ru/api/sil/ \
  -d "oturum=2nnkJb&veri[0]=mail_id&veri[1]=1"

# 销毁邮箱
curl -b cookies.txt -X POST \
  https://tempail.com/ru/api/yoket/ \
  -d "oturum=2nnkJb"
```

## 与其他服务对比

| 特性 | Tempail.com | TemporaryMail.com | Tempimail.org |
|------|-------------|-------------------|---------------|
| 认证方式 | Cookie会话 | 自定义密钥 | Laravel会话+CSRF |
| 轮询间隔 | 10秒 | 5秒 | 20秒 |
| API格式 | 表单数据 | JSON | 表单数据 |
| 响应格式 | HTML | JSON | HTML |
| 会话时长 | 1小时 | 无限制 | 2小时 |
| 邮件保留 | 未知 | 未知 | 未知 |

## 更新日志

- **2026-05-19**: 初始文档创建
  - 分析了主要API端点
  - 记录了认证机制
  - 提供了示例代码

## 参考资源

- 官方网站: https://tempail.com
- JavaScript源码: https://tempail.com/js/main.min.js
- 隐私政策: https://tempail.com/privacy/

---

**注意**: 此文档基于逆向工程分析，仅供学习和研究目的。使用时请遵守网站的服务条款。