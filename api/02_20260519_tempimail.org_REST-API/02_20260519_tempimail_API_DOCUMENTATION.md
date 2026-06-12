# Tempimail.org API 逆向工程文档

## 基础信息

- **网站**: https://tempimail.org/
- **API 基础URL**: `https://tempimail.org`
- **API类型**: REST API
- **请求方式**: POST
- **响应格式**: JSON
- **认证方式**: CSRF Token (Laravel框架)

## API 端点

### 1. 获取邮箱和消息列表

**端点**: `/messages`

**方法**: POST

**请求头**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json, text/javascript, */*; q=0.01
X-Requested-With: XMLHttpRequest
Referer: https://tempimail.org/
Origin: https://tempimail.org
Content-Type: application/x-www-form-urlencoded
```

**请求参数**:
- `_token` (必需): CSRF token，从页面meta标签获取

**请求示例**:
```
POST /messages?{timestamp}
Content-Type: application/x-www-form-urlencoded

_token=C2KcLwmjz4qO4FXA0y70JTPjVbqBnldFaGX71VIa
```

**成功响应**:
```json
{
  "mailbox": "example@tempimail.org",
  "messages": [
    {
      "id": 123,
      "from": "发件人姓名",
      "from_email": "sender@example.com",
      "subject": "邮件主题",
      "is_seen": false
    }
  ]
}
```

**响应字段说明**:
- `mailbox`: 分配的临时邮箱地址
- `messages`: 邮件列表数组
  - `id`: 邮件唯一ID
  - `from`: 发件人显示名称
  - `from_email`: 发件人邮箱地址
  - `subject`: 邮件主题
  - `is_seen`: 是否已读

**空收件箱响应**:
```json
{
  "mailbox": "example@tempimail.org",
  "messages": []
}
```

---

### 2. 查看邮件详情

**端点**: `/view/{id}` 或 `/{lang}/view/{id}`

**方法**: GET

**URL格式**:
- 英文: `https://tempimail.org/en/view/{id}`
- 俄文: `https://tempimail.org/ru/view/{id}`
- 中文: `https://tempimail.org/zh/view/{id}`
- 默认: `https://tempimail.org/view/{id}`

**参数**:
- `id` (必需): 邮件ID

**请求示例**:
```
GET /en/view/123
```

**响应**: HTML页面，包含完整的邮件内容

---

## 技术实现细节

### CSRF Token获取

CSRF Token存储在页面的meta标签中：

```html
<meta name="csrf-token" content="C2KcLwmjz4qO4FXA0y70JTPjVbqBnldFaGX71VIa">
```

JavaScript获取方式：
```javascript
var token = $('meta[name="csrf-token"]').attr("content");
```

### 轮询机制

**轮询间隔**: 20秒（可配置）

JavaScript实现：
```javascript
var fetch_time = "20"; // 秒
var url = "https://tempimail.org/messages";

setInterval(function() {
    if (window.check_is_runing && window.check_recaptcha) {
        // 执行API调用
        fetchMessages();
    }
}, 1000 * fetch_time);
```

### 加载状态

在获取邮箱时显示加载动画：
- 初始状态: "загрузка" (俄文: 加载中)
- 动画: "загрузка." → "загрузка.." → "загрузка..." → "загрузка"

### reCAPTCHA集成

网站使用Google reCAPTCHA v2进行保护：

```javascript
window.myCallback = function(response) {
    document.getElementById("captcha-response").value = response;
    window.check_recaptcha = true;
};

// 自动执行reCAPTCHA
grecaptcha.execute();
```

---

## 使用流程

### 完整使用示例

```javascript
// 1. 获取CSRF Token
const token = document.querySelector('meta[name="csrf-token"]').content;

// 2. 请求邮箱和消息
fetch('https://tempimail.org/messages?' + Date.now(), {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: '_token=' + token
})
.then(response => response.json())
.then(data => {
    console.log('邮箱地址:', data.mailbox);
    console.log('邮件数量:', data.messages.length);
    
    // 3. 查看邮件详情
    if (data.messages.length > 0) {
        const firstEmail = data.messages[0];
        window.location.href = '/en/view/' + firstEmail.id;
    }
});

// 4. 设置定时轮询
setInterval(() => {
    // 重复步骤2
}, 20000); // 每20秒检查一次
```

---

## Python 客户端实现

### 基础客户端

```python
import requests
from bs4 import BeautifulSoup
import time
import re

class TempimailClient:
    def __init__(self):
        self.base_url = "https://tempimail.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://tempimail.org/',
            'Origin': 'https://tempimail.org'
        })
        self.csrf_token = None
        self.mailbox = None
    
    def get_csrf_token(self):
        """获取CSRF Token"""
        response = self.session.get(f"{self.base_url}/en")
        soup = BeautifulSoup(response.text, 'html.parser')
        meta = soup.find('meta', {'name': 'csrf-token'})
        if meta:
            self.csrf_token = meta.get('content')
            return self.csrf_token
        raise Exception("无法获取CSRF Token")
    
    def get_mailbox(self):
        """获取邮箱地址和消息"""
        if not self.csrf_token:
            self.get_csrf_token()
        
        url = f"{self.base_url}/messages?{int(time.time() * 1000)}"
        data = {'_token': self.csrf_token}
        
        response = self.session.post(url, data=data)
        result = response.json()
        
        self.mailbox = result.get('mailbox')
        return result
    
    def check_inbox(self):
        """检查收件箱"""
        return self.get_mailbox()
    
    def get_email_detail(self, email_id, lang='en'):
        """获取邮件详情"""
        url = f"{self.base_url}/{lang}/view/{email_id}"
        response = self.session.get(url)
        return response.text
    
    def wait_for_email(self, timeout=300, check_interval=20):
        """等待接收邮件"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.check_inbox()
            if result.get('messages'):
                return result['messages']
            time.sleep(check_interval)
        
        return None

# 使用示例
if __name__ == "__main__":
    client = TempimailClient()
    
    # 获取邮箱
    result = client.get_mailbox()
    print(f"邮箱地址: {result['mailbox']}")
    
    # 等待邮件
    print("等待接收邮件...")
    emails = client.wait_for_email(timeout=60)
    
    if emails:
        print(f"收到 {len(emails)} 封邮件")
        for email in emails:
            print(f"发件人: {email['from_email']}")
            print(f"主题: {email['subject']}")
            
            # 获取邮件详情
            detail = client.get_email_detail(email['id'])
            print(f"邮件内容长度: {len(detail)} 字符")
```

---

## 网站特性

### 1. 多语言支持

支持的语言：
- 英语 (en)
- 阿拉伯语 (ar)
- 法语 (fr)
- 日语 (ja)
- 印地语 (hi)
- 俄语 (ru)
- 葡萄牙语 (pt)
- 西班牙语 (es)
- 中文 (zh)
- 韩语 (ko)
- 德语 (de)

URL格式: `https://tempimail.org/{lang}`

### 2. 框架识别

**后端框架**: Laravel (PHP)
- CSRF Token机制
- 标准的Laravel路由结构
- Meta标签中的CSRF token

**前端框架**: jQuery
- 使用jQuery进行AJAX请求
- Bootstrap UI框架
- ClipboardJS用于复制功能

### 3. 安全特性

- ✅ CSRF保护
- ✅ reCAPTCHA验证
- ✅ Cloudflare CDN保护
- ✅ XSS防护（iframe隔离）

### 4. 性能优化

- 使用时间戳防止缓存: `?{timestamp}`
- 进度条显示加载状态
- 异步加载邮件内容

---

## 限制和约束

### 1. 速率限制
- 建议轮询间隔: 20秒
- 过快请求可能触发reCAPTCHA

### 2. 邮箱生命周期
- 邮箱地址自动生成
- 具体过期时间未明确说明
- 建议及时处理邮件

### 3. reCAPTCHA要求
- 首次访问需要完成reCAPTCHA
- 验证通过后才能获取邮箱
- 可能需要人工交互

---

## 错误处理

### 常见错误

1. **CSRF Token失效**
```json
{
  "message": "CSRF token mismatch",
  "exception": "TokenMismatchException"
}
```
解决方案: 重新获取CSRF token

2. **reCAPTCHA未验证**
- 页面会要求完成验证
- 需要等待验证完成

3. **网络错误**
- 使用重试机制
- 实现指数退避

---

## 最佳实践

### 1. CSRF Token管理
```python
# 定期刷新token
def refresh_token(self):
    if time.time() - self.token_time > 3600:  # 1小时
        self.get_csrf_token()
```

### 2. 错误重试
```python
def safe_request(self, func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)
```

### 3. 会话保持
```python
# 使用Session保持cookies
session = requests.Session()
```

---

## 注意事项

1. **遵守使用条款** - 合理使用API
2. **尊重速率限制** - 避免过快请求
3. **处理reCAPTCHA** - 可能需要人工干预
4. **临时性质** - 邮件会自动过期
5. **隐私保护** - 不要用于敏感信息

---

## 更新日志

- **2026-05-19**: 初始版本，完整逆向工程文档

---

## 技术栈总结

**后端**:
- Laravel (PHP框架)
- MySQL/PostgreSQL (推测)

**前端**:
- jQuery
- Bootstrap
- ClipboardJS
- Progress.js

**安全**:
- Google reCAPTCHA v2
- Cloudflare CDN
- CSRF Protection

**部署**:
- Cloudflare (CDN + DDoS保护)
- HTTPS/SSL

---

**创建日期**: 2026-05-19  
**版本**: 1.0  
**状态**: 完成 ✅