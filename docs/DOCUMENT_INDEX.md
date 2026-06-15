# CrazyMail 项目文档清单

## 一、方法论与流程文档

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| METHODOLOGY_FRAMEWORK.md | 邮箱网站矩阵开发闭环体系（9大环节总览） | docs/ |
| LOVABLE_PROMPT.md | 给Lovable.dev的Prompt（当前站点使用） | 项目根目录 |

## 二、Skills（可复用流程）

| Skill名称 | 内容简介 | 存储路径 |
|-----------|---------|---------|
| api-exploration | API探查标准流程：系统化学习和测试邮箱服务API | skills/email-sites/ |
| lovable-prompt-framework | 给Lovable.dev的结构化Prompt框架 | skills/email-sites/ |
| operation-manual-template | 邮箱网站操作手册模板：拟人化的用户操作流程 | skills/email-sites/ |
| email-site-testing | 邮箱网站自动化测试流程：全面测试所有功能 | skills/email-sites/ |
| knowledge-management | 知识沉淀与Skills整合：从实践中提炼可复用的方法论 | skills/email-sites/ |

## 三、项目规范文档

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| AGENTS.md | 项目开发规范（OpenCode使用） | 项目根目录 |
| DOD.md | 任务完成标准定义 | 项目根目录 |
| HERMES_OPENCODE_METHODOLOGY.md | Hermes+OpenCode协作方法论 | 项目根目录 |

## 四、架构决策记录

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| ADR-001-战略调整.md | 战略调整决策记录 | ADR/ |
| ADR-002-crewai-langgraph-hybrid.md | CrewAI+LangGraph混合架构决策 | ADR/ |
| ADR-003-yaml-agent-config.md | YAML代理配置决策 | ADR/ |
| ADR-004-soulspec-persona.md | SoulSpec人设决策 | ADR/ |

## 五、API与技术文档

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| API_DESIGN.md | API设计文档 | doc/01-整体方案初稿_claude编写/ |
| ARCHITECTURE.md | 架构设计文档 | doc/01-整体方案初稿_claude编写/ |
| DATABASE_SCHEMA.md | 数据库Schema文档 | doc/01-整体方案初稿_claude编写/ |
| DEVELOPMENT_ROADMAP.md | 开发路线图 | doc/01-整体方案初稿_claude编写/ |
| TECH_STACK.md | 技术栈文档 | doc/01-整体方案初稿_claude编写/ |
| PROJECT_STRUCTURE.md | 项目结构文档 | doc/01-整体方案初稿_claude编写/ |

## 六、头脑风暴文档

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| CrazyMail_Character_Matrix.md | 角色矩阵文档 | doc/00-头脑风暴/ |
| CrazyMail_Frontend_Implementation.md | 前端实现方案 | doc/00-头脑风暴/ |
| CrazyMail_Tech_Development_Plan.md | 技术开发计划 | doc/00-头脑风暴/ |
| OpenCode_MiMo_Config_Guide.md | OpenCode+MiMo配置指南 | doc/00-头脑风暴/ |

## 七、测试与验证文档

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| E2E_TEST_REPORT.md | 端到端测试报告（28项测试，100%通过率） | docs/ |
| OPERATION_MANUAL.md | TempMail.Pro 操作手册（含6种语言、Coming Soon标注） | docs/ |

## 八、开发计划文档

| 文件名 | 内容简介 | 存储路径 |
|--------|---------|---------|
| 20260611_180000-phase1-content-pipeline.md | Phase1内容管线计划 | .hermes/plans/ |
| 20260611_190000-phase1-mvp.md | Phase1 MVP计划 | .hermes/plans/ |
| 20260612-iteration-v1.1.md | v1.1迭代计划 | .hermes/plans/ |
| 20260612-opencode-tasks.md | OpenCode任务列表 | .hermes/plans/ |

---

## 文档使用指南

### 新项目启动时
1. 阅读 `METHODOLOGY_FRAMEWORK.md` 了解整体流程
2. 使用 `api-exploration` skill 进行API探查
3. 使用 `lovable-prompt-framework` skill 生成Prompt
4. 使用 `operation-manual-template` skill 编写操作手册

### 开发过程中
1. 参考 `AGENTS.md` 和 `DOD.md` 确保质量
2. 使用 `email-site-testing` skill 进行测试
3. 使用 `knowledge-management` skill 沉淀知识

### 项目完成后
1. 更新项目知识库
2. 提炼可复用的经验到skills
3. 更新核心文件（AGENTS.md等）
