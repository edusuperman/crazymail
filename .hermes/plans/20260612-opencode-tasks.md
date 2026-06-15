# OpenCode 任务计划：阶段一 MVP

## 执行规则
- 所有代码由 OpenCode 编写，Hermes 只做规划和验收
- 每个任务使用 `opencode run` 派发
- 任务完成后 Hermes 对照 DoD 验收

---

## TASK-001: 创建统一邮件适配器接口

**目标：** 创建邮件 API 的统一抽象层

**修改范围：**
- 创建: `sites/shared/api_adapters/__init__.py`
- 创建: `sites/shared/api_adapters/base.py`
- 创建: `sites/shared/api_adapters/registry.py`

**要求：**
1. base.py 定义 EmailAdapter 抽象基类
2. 包含 EmailAddress、EmailMessage 数据类
3. 定义异常类：EmailAdapterError、AuthenticationError、RateLimitError、NetworkError
4. registry.py 实现适配器注册中心
5. __init__.py 导出所有公共接口

**DoD：**
- [ ] 代码能正常导入
- [ ] 有完整的类型注解
- [ ] 有中文注释

---

## TASK-002: 适配 mail.tm 客户端

**目标：** 实现 mail.tm 的 EmailAdapter

**修改范围：**
- 创建: `sites/shared/api_adapters/mailtm_adapter.py`

**要求：**
1. 继承 EmailAdapter 接口
2. 使用 httpx 异步客户端
3. 实现：create_email、get_messages、get_message、delete_message、mark_as_read
4. JWT 认证管理
5. 错误处理和重试机制

**DoD：**
- [ ] 能成功创建邮箱
- [ ] 能获取邮件列表
- [ ] 语法检查通过

---

## TASK-003: 创建 FastAPI 后端

**目标：** 创建邮件 API 服务

**修改范围：**
- 创建: `backend/__init__.py`
- 创建: `backend/config.py`
- 创建: `backend/main.py`
- 创建: `backend/routers/__init__.py`
- 创建: `backend/routers/email.py`

**要求：**
1. main.py 是唯一 FastAPI 入口
2. email.py 实现：POST /create、GET /messages、GET /messages/{id}、DELETE /messages/{id}
3. CORS 配置允许 localhost:3000
4. 使用 loguru 日志

**DoD：**
- [ ] FastAPI 能启动
- [ ] /health 返回 200
- [ ] /docs 能访问

---

## TASK-004: 创建站点-01 前端

**目标：** 创建临时邮箱前端界面

**修改范围：**
- 创建: `sites/site-01/` 目录结构
- 初始化 Next.js 项目

**要求：**
1. 使用 create-next-app 初始化
2. TypeScript + Tailwind CSS + App Router
3. 创建 config.yaml 站点配置

**DoD：**
- [ ] Next.js 能启动
- [ ] 首页能访问

---

## TASK-005: 实现首页功能

**目标：** 临时邮箱核心交互

**修改范围：**
- 修改: `sites/site-01/frontend/src/app/page.tsx`
- 创建: `sites/site-01/frontend/src/lib/api-client.ts`

**要求：**
1. 一键生成邮箱按钮
2. 复制邮箱地址
3. 收件箱列表（自动刷新）
4. 移动端响应式

**DoD：**
- [ ] 能生成邮箱
- [ ] 能复制地址
- [ ] 能显示收件箱

---

## TASK-006: SEO/GEO 优化

**目标：** 搜索引擎优化

**修改范围：**
- 修改: `sites/site-01/frontend/src/app/layout.tsx`
- 创建: `sites/site-01/frontend/src/app/sitemap.ts`
- 创建: `sites/site-01/frontend/src/app/robots.ts`

**要求：**
1. JSON-LD 结构化数据
2. sitemap.xml
3. robots.txt
4. Meta tags + OG tags

**DoD：**
- [ ] sitemap 能访问
- [ ] robots.txt 能访问
- [ ] JSON-LD 验证通过
