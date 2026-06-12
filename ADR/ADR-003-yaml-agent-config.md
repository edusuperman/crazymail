# ADR-003: Agent 配置用 YAML 而非 Python

**日期：** 2026-06-12
**状态：** 已接受

## 背景

需要定义 7 个官员 Agent（李纲、张择端、李清照等），如何存储这些定义？

## 决策

- Agent 定义放在 `backend/agents/crews/*.yaml`
- 禁止用 `.py` 文件定义 Agent

## 原因

- 符合"插座原则"：新增 Agent = 新建 YAML，不改 Python 代码
- 符合"无硬编码"原则：角色、目标、工具不硬编码在代码中
- OpenCode 可以通过修改 YAML 来调整 Agent 行为，无需触及核心逻辑
