# ADR-002: CrewAI + LangGraph 双框架混用

**日期：** 2026-06-12
**状态：** 已接受

## 背景

需要构建 7 阶段 AI 内容流水线，涉及多个 Agent 角色和复杂的状态流转。

## 决策

- **CrewAI**：负责角色定义（谁做什么）
- **LangGraph**：负责状态编排（怎么流转、断点续跑、人工节点）

## 原因

- CrewAI 擅长 Agent 角色定义和任务分配
- LangGraph 擅长状态管理和 Human-in-the-Loop
- 两者互补，不冲突
