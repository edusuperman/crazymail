# Guerrilla Mail 真实邮件测试报告

## 测试信息
- **测试日期**: 2026-05-21
- **测试服务**: Guerrilla Mail (guerrillamail.com)
- **发送方**: Mailfence (4qvwxanaqn@mailfence.com)
- **测试方法**: 自动化测试 + 手动验证

## 测试结果总览

### ✅ 测试状态: 完全成功

所有测试均已通过，包括手动测试和完整的端到端自动化测试。

---

## 详细测试记录

### ✅ 手动测试 - 成功
**测试时间**: 2026-05-21 (用户手动操作)

**测试流程**:
1. 手动登录 Mailfence
2. 手动创建 Guerrilla Mail 临时邮箱
3. 手动发送测试邮件
4. 确认邮件成功到达

**结果**: ✅ **成功** - Guerrilla Mail 成功接收到来自 Mailfence 的邮件

**关键发现**:
- Mailfence → Guerrilla Mail 的邮件传递路径是畅通的
- Guerrilla Mail 不会屏蔽来自 Mailfence 的邮件
- 邮件到达时间正常（几秒到几分钟）

---

### ✅ 自动化测试 - 完全成功
**测试时间**: 2026-05-21 16:00+ (最终成功版本)
**测试脚本**: `tests/07_20260520_guerrillamail_automated_test.py`

**测试流程**:
1. ✅ 自动创建 Guerrilla Mail 临时邮箱
2. ✅ 自动登录 Mailfence
3. ✅ 自动打开撰写窗口
4. ✅ 收件人字段正确填写
5. ✅ 主题和正文填写成功
6. ✅ **Send 按钮成功点击**
7. ✅ 邮件成功发送并到达
8. ✅ API 成功检索到测试邮件

**测试输出示例**:
```
✓ Send 按钮已出现 (id=mailSend)
✓ 已点击 Send 按钮
✓ 撰写窗口已关闭，邮件已发送

✓ 测试成功！
找到测试邮件:
  发件人: 4qvwxanaqn@mailfence.com
  主题: Guerrilla Mail Automated Test - 1779350757
  邮件ID: 256269297
```

---

## 关键技术突破

### 1. Send 按钮选择器修复 ✅

**问题历史**:
- 初始尝试: `button:has-text("Send")` - 失败
- 第二次尝试: `[title="Send"]` - 失败
- Ctrl+Enter 快捷键 - 失败

**最终解决方案**:
```python
# 使用 ID 选择器（最可靠）
'send_button': '#mailSend'
```

**关键发现**:
- 用户通过 DOM 检查发现 Send 按钮有 `id="mailSend"` 属性
- ID 选择器是最可靠的选择器类型
- 这个修复使得所有后续自动化测试都能成功

**实现代码**:
```python
# 等待 Send 按钮出现
await self.page.wait_for_selector(
    self.SELECTORS['send_button'],  # '#mailSend'
    state='visible',
    timeout=10000
)

# 点击 Send 按钮
await self.page.click(self.SELECTORS['send_button'])
```

### 2. 收件人字段填写流程 ✅

**Mailfence 特殊要求**:
```python
# 1. 等待撰写窗口完全加载
await self.page.wait_for_timeout(3000)

# 2. 填写收件人
to_input = await self.page.query_selector('input.GCSDBRWBPL')
await to_input.fill(to, force=True)

# 3. 按两次 Tab 键确认
await to_input.press('Tab')  # 第一次：确认邮箱（变灰色）
await self.page.keyboard.press('Tab')  # 第二次：跳转到 Subject
```

**关键点**:
- 必须等待3秒让撰写窗口完全加载
- 输入后必须按 Tab 键确认（邮箱会变成灰色标签）
- 再按一次 Tab 跳转到下一个字段

### 3. 登录稳定性改进 ✅

**问题**: 密码输入框有时显示红色边框，登录失败

**解决方案**:
```python
# 用户名输入后等待
await username_input.fill(self.config['username'])
await self.page.wait_for_timeout(500)

# 密码输入后等待
await password_input.fill(self.config['password'])
await self.page.wait_for_timeout(1000)
```

---

## 技术细节

### Mailfence 表单导航规则

**To/Cc/Bcc 字段**:
- 选择器: `input.GCSDBRWBPL`
- 输入流程: 输入 → Tab（确认）→ Tab（跳转）
- 确认标志: 邮箱地址变为灰色标签

**Send 按钮**:
- 选择器: `#mailSend` (ID 选择器)
- 类型: 分体式按钮（带下拉菜单）
- 状态检查: 撰写窗口关闭 = 发送成功

### Guerrilla Mail API 响应格式

**邮件列表格式**:
```python
response = {
    'list': [
        {
            'mail_id': '256269297',
            'mail_from': '4qvwxanaqn@mailfence.com',
            'mail_subject': 'Test Subject',
            'mail_timestamp': '1779350757',
            'mail_read': '0'
        }
    ]
}
```

**访问方式**:
```python
email_list = guerrilla_client.get_email_list()
emails = email_list['list']  # 注意：返回的是字典，不是列表
```

---

## 测试脚本

### 完整自动化测试脚本
**位置**: `tests/07_20260520_guerrillamail_automated_test.py`

**功能**:
1. 创建 Guerrilla Mail 临时邮箱
2. 使用 Mailfence 自动发送测试邮件
3. 等待邮件到达
4. 通过 API 验证邮件接收
5. 输出详细测试结果

**运行方式**:
```bash
python tests/07_20260520_guerrillamail_automated_test.py
```

---

## 经验总结

### 成功因素

1. **DOM 检查的重要性**: 用户提供的 HTML 结构信息（`id="mailSend"`）是解决问题的关键
2. **ID 选择器优先**: ID 选择器比属性选择器更可靠
3. **等待时间充足**: 给予足够的时间让页面元素完全加载
4. **Tab 键导航**: 理解并正确实现 Mailfence 的表单导航逻辑
5. **端到端验证**: 不仅检查发送操作，还验证邮件实际到达

### 最佳实践

1. **选择器优先级**:
   - 第一优先: ID 选择器 (`#elementId`)
   - 第二优先: 属性选择器 (`[attribute="value"]`)
   - 第三优先: 文本选择器 (`button:has-text("Text")`)

2. **等待策略**:
   - 使用 `wait_for_selector()` 等待元素出现
   - 使用 `wait_for_timeout()` 给予加载时间
   - 检查元素状态 (`visible`, `editable`)

3. **验证方法**:
   - 检查撰写窗口是否关闭
   - 通过 API 验证邮件实际到达
   - 记录详细的日志信息

---

## 结论

✅ **Guerrilla Mail 服务完全可用**

- REST API 功能完整且稳定
- 与 Mailfence 的邮件传递路径畅通
- 完整的自动化测试流程已建立
- 可作为其他服务测试的参考模板

**下一步**: 将此自动化测试模式应用到其他临时邮箱服务（temporarymail.com, tempimail.org, tempail.com）