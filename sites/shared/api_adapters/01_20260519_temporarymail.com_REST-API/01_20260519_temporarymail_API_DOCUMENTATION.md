# TemporaryMail.com API 逆向工程文档

## 基础信息

- **API 基础URL**: `https://temporarymail.com/api/`
- **请求方式**: GET/POST
- **响应格式**: JSON

## API 端点

### 1. 请求邮箱地址访问权限

**端点**: `/api/?action=requestEmailAccess`

**方法**: GET

**参数**:
- `key` (可选): 邮箱密钥，用于访问之前使用过的邮箱
- `value` (必需): 请求的邮箱地址，或使用 "random" 获取随机地址
- `r` (可选): 引荐来源URL (referrer)

**请求示例**:
```
GET /api/?action=requestEmailAccess&key=&value=random
GET /api/?action=requestEmailAccess&key=1glwh8WKPGmwUFqrp5GIp7VbyOcH9e85&value=test@example.com
```

**成功响应**:
```json
{
  "address": "Yaretza.Creager@EasyMailer.live",
  "secretKey": "1glwh8WKPGmwUFqrp5GIp7VbyOcH9e85"
}
```

**错误响应**:
```json
{
  "error": "错误信息",
  "code": 429,  // 或 403, 500
  "avoidRetry": 1  // 可选，表示不应重试
}
```

**错误码说明**:
- `429`: 请求过多，需要等待
- `403`: 邮箱被其他用户保留，14天后解锁
- `500`: 未授权访问此邮箱

---

### 2. 检查收件箱

**端点**: `/api/?action=checkInbox`

**方法**: GET

**参数**:
- `value` (必需): 邮箱的密钥 (secretKey)

**请求示例**:
```
GET /api/?action=checkInbox&value=1glwh8WKPGmwUFqrp5GIp7VbyOcH9e85
```

**成功响应** (有邮件):
```json
[
  {
    "id": "邮件唯一ID",
    "from": "sender@example.com",
    "name": "发件人姓名",
    "subject": "邮件主题",
    "date": 1779188633  // Unix时间戳
  }
]
```

**成功响应** (无邮件):
```json
[]
```

**错误响应**:
```json
{
  "error": "错误信息",
  "code": 500  // 或 429
}
```

**错误码说明**:
- `500`: 未授权检查此收件箱
- `429`: 检查收件箱次数过多

**轮询机制**:
- 客户端每秒检查一次是否需要更新
- 实际API调用间隔至少5秒
- 当页面不可见或正在查看邮件时暂停检查

---

### 3. 获取邮件详情

**端点**: `/api/?action=getEmail`

**方法**: POST

**参数**:
- `value` (必需): 邮件ID

**请求示例**:
```
POST /api/?action=getEmail&value=邮件ID
```

**成功响应**:
```json
{
  "邮件ID": {
    "from": "sender@example.com",
    "name": "发件人姓名",
    "subject": "邮件主题",
    "date": 1779188633,
    "sourceHash": "邮件源码哈希值",
    "attachments": [
      {
        "filename": "文件名.pdf",
        "fileId": "附件ID",
        "size": 12345
      }
    ]
  }
}
```

**错误响应**:
```json
{
  "error": "错误信息",
  "code": 429  // 或 "captcha"
}
```

**错误码说明**:
- `429`: 打开邮件次数过多
- `captcha`: 需要验证码

**邮件内容查看**:
- 邮件HTML内容通过iframe加载: `/view/?i=邮件ID&width=容器宽度`

---

### 4. 下载附件

**端点**: `/attachment/`

**方法**: GET

**参数**:
- `i` (必需): 附件ID (fileId)

**请求示例**:
```
GET /attachment/?i=附件ID
```

---

### 5. 获取可用域名列表

**端点**: `/api/?action=getDomains`

**方法**: GET

**请求示例**:
```
GET /api/?action=getDomains
```

**响应**: 返回可用的邮箱域名列表

---

### 6. 联系表单

**端点**: `/api/?action=contactForm`

**方法**: POST

**用途**: 提交联系表单

---

### 7. 创建账户

**端点**: `/api/?action=createAccount`

**方法**: POST

**用途**: 创建用户账户（用于保存邮箱地址）

---

### 8. 获取服务状态

**端点**: `/api/?action=getStatus`

**方法**: GET

**用途**: 获取服务运行状态

---

## 使用流程

### 完整使用示例

```javascript
// 1. 请求一个随机邮箱地址
const response1 = await fetch('/api/?action=requestEmailAccess&key=&value=random');
const data1 = await response1.json();
console.log('邮箱地址:', data1.address);
console.log('密钥:', data1.secretKey);

// 2. 定期检查收件箱（每5秒）
setInterval(async () => {
  const response2 = await fetch(`/api/?action=checkInbox&value=${data1.secretKey}`);
  const emails = await response2.json();
  
  if (emails.length > 0) {
    console.log('收到新邮件:', emails);
    
    // 3. 获取邮件详情
    for (const email of emails) {
      const response3 = await fetch(`/api/?action=getEmail&value=${email.id}`, {
        method: 'POST'
      });
      const emailDetail = await response3.json();
      console.log('邮件详情:', emailDetail);
    }
  }
}, 5000);
```

---

## 重要说明

### 1. 速率限制
- API有严格的速率限制
- 收到429错误时需要等待5秒后重试
- 建议不要在多个标签页同时使用同一邮箱

### 2. 邮箱保留机制
- 邮箱地址会被当前会话锁定
- 其他用户无法访问被锁定的邮箱
- 14天未使用后会自动解锁

### 3. 数据存储
- 邮箱地址历史存储在 `localStorage.addressHistory`
- 格式: `{ "邮箱地址": ["密钥", 时间戳] }`
- 已读邮件ID存储在 `localStorage.readEmails`

### 4. 安全特性
- 邮件内容通过iframe隔离显示
- 外部请求被阻止
- 使用密钥而非邮箱地址进行API调用

### 5. 通知机制
- 收到新邮件时播放声音提示
- 页面标题显示未读邮件数量
- 支持浏览器扩展集成（通过CustomEvent）

---

## Python 使用示例

```python
import requests
import time
import json

class TemporaryMail:
    def __init__(self):
        self.base_url = "https://temporarymail.com/api/"
        self.email = None
        self.secret_key = None
    
    def get_random_email(self):
        """获取随机邮箱地址"""
        url = f"{self.base_url}?action=requestEmailAccess&key=&value=random"
        response = requests.get(url)
        data = response.json()
        
        if 'error' not in data:
            self.email = data['address']
            self.secret_key = data['secretKey']
            return self.email
        else:
            raise Exception(f"获取邮箱失败: {data['error']}")
    
    def check_inbox(self):
        """检查收件箱"""
        if not self.secret_key:
            raise Exception("请先获取邮箱地址")
        
        url = f"{self.base_url}?action=checkInbox&value={self.secret_key}"
        response = requests.get(url)
        
        if response.text.strip() == '[]':
            return []
        
        data = response.json()
        
        if isinstance(data, list):
            return data
        elif 'error' in data:
            raise Exception(f"检查收件箱失败: {data['error']}")
        
        return []
    
    def get_email(self, email_id):
        """获取邮件详情"""
        url = f"{self.base_url}?action=getEmail&value={email_id}"
        response = requests.post(url)
        data = response.json()
        
        if 'error' in data:
            raise Exception(f"获取邮件失败: {data['error']}")
        
        return data
    
    def wait_for_email(self, timeout=300, check_interval=5):
        """等待接收邮件"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            emails = self.check_inbox()
            if emails:
                return emails
            time.sleep(check_interval)
        
        return None

# 使用示例
if __name__ == "__main__":
    mail = TemporaryMail()
    
    # 获取临时邮箱
    email_address = mail.get_random_email()
    print(f"临时邮箱地址: {email_address}")
    
    # 等待接收邮件
    print("等待接收邮件...")
    emails = mail.wait_for_email(timeout=60)
    
    if emails:
        print(f"收到 {len(emails)} 封邮件")
        for email in emails:
            print(f"\n发件人: {email['from']}")
            print(f"主题: {email.get('subject', '无主题')}")
            
            # 获取邮件详情
            detail = mail.get_email(email['id'])
            print(f"详情: {json.dumps(detail, indent=2, ensure_ascii=False)}")
    else:
        print("未收到邮件")
```

---

## 注意事项

1. **请遵守网站使用条款**
2. **不要滥用API**，避免对服务器造成过大压力
3. **临时邮箱仅用于临时用途**，不要用于重要账户
4. **邮件会自动过期删除**
5. **API可能随时变更**，建议定期检查更新

---

## 更新日志

- **2026-05-19**: 初始版本，完整逆向工程文档