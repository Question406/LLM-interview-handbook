---
id: drustz-1926d7a309fddb7eea
section: agent-questions
order: 11
level: A
title: 05_questions · Agentic 真题库
quick: 作者完整文档 · 05_questions · Agentic 真题库
companies: []
tags:
  - DrustZ
  - 作者完整文档
  - Agent · Interview Questions & Solutions
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/README.md
    type: primary
---
# 05_questions · Agentic 真题库

⏱ 约 5 分钟读完 ｜ 面试前只看目标公司的 ⭐⭐⭐ 行，点链接跳到对应题

汇编来源：9 个挖掘 agent 的产出（1p3a 缓存题库、hack2hire、官方博客、Exponent/PracHub/面经站）+ v1 题库（`../../agentic/data/questions.json`）吸收。共 **A/B/C 44 题 + D 类 20 条**。Applied Compute / Hark / Humans& / Extend 无公开面经（挖掘确证为空），用 🧪 推导题 + 对口 generic 题覆盖。

## 分类法

| 类 | 定义 | 文件 | 数量 |
|---|---|---|---|
| A | 具体应用场景设计题（绑定产品场景的 SD） | [`A_scenario_design`.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-08c4d176e4d4e07c5b) | 16 |
| B | 泛化 agent 设计题（loop/memory/multi-agent/eval 平台） | [`B_general_design`.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-fcd783e0e7ae0ef3e2) | 9 |
| C | live coding / AI-assisted coding 实操 | [`C_live_ai_coding`.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-47aa581fa1cecd1fb3) | 19 |
| D | 概念快问（一行问 + 两句答） | [`D_rapid_fire`.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-9d5b52c44f5252c7ab) | 20 |

## 置信度规则

- ✅ **多源确认**：≥2 个独立来源家族（1p3a / reddit / glassdoor / blind / 官方博客互为独立；hack2hire 单独不算数）。例外：公司官方博客描述**自家**面试流程，视同 ✅（Sierra、PromptLayer）。
- ⚠️ **单源**：仅一个来源家族，题面可信但可能不完整或已轮换。
- 🤖 **hack2hire 未交叉验证**（该站约 86% 内容疑似 AI 生成）。本库所有 hack2hire 条目均已与独立来源合并升级为 ✅，当前无纯 🤖 条目。
- 🧪 **推导练习非真题**：按公司公开产品/JD 方向自拟，v1 带完整 rubric。
- 挖掘结果与 v1 吸收题重复的已合并为一条并升置信度；v1 吸收题在 details 末尾附 rubric 链接。

## ⭐ 优先级

⭐⭐⭐ = 本周面试公司（Sierra 7/15、Anthropic 7/22、Hark、Humans&、Extend、Applied Compute）的真题，及对口这些公司的 🧪/迁移题（表中标注）；⭐⭐ = generic/其他公司真题；⭐ = 低相关备查。

## 全库总表

| 题号 | 标题 | 公司 | 置信度 | ⭐ | 链接 |
|---|---|---|---|---|---|
| A1 | take-home：虚构公司客服 agent（5 选 2）+ onsite 演示 | Sierra | ✅ | ⭐⭐⭐ | [A1](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a1) |
| A2 | 订阅取消 agentic 系统设计 | Sierra | ⚠️ | ⭐⭐⭐ | [A2](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a2) |
| A3 | 文档自动化管线（银行材料/医生账单） | generic·Extend 对口 | ✅ | ⭐⭐⭐ | [A3](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a3) |
| A4 | 保险理赔文档 agent | Extend | 🧪 | ⭐⭐⭐ | [A4](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a4) |
| A5 | LLM Inference Batch API（含 100K RPS 变体） | Anthropic | ✅ | ⭐⭐⭐ | [A5](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a5) |
| A6 | Prompt Playground 全栈设计 | Anthropic | ✅ | ⭐⭐⭐ | [A6](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a6) |
| A7 | Design ChatGPT（SSE streaming 后端） | Anthropic/OpenAI | ✅ | ⭐⭐⭐ | [A7](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a7) |
| A8 | 500GB 模型分发到 100–1000 worker | Anthropic | ✅ | ⭐⭐⭐ | [A8](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a8) |
| A9 | Design Sora / GPU job scheduler | OpenAI | ✅ | ⭐⭐ | [A9](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a9) |
| A10 | 企业级 RAG 聊天机器人（类 Glean） | OpenAI | ✅ | ⭐⭐ | [A10](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a10) |
| A11 | 企业知识库 agent（官方 rubric；多租户/10M 变体） | generic | ✅ | ⭐⭐ | [A11](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a11) |
| A12 | Design the OpenAI Playground（全栈） | OpenAI | ✅ | ⭐⭐ | [A12](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a12) |
| A13 | Design Copilot / Perplexity | generic | ✅ | ⭐⭐ | [A13](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a13) |
| A14 | PromptLayer 官方题单（白板+coding+take-home） | PromptLayer | ✅ | ⭐⭐ | [A14](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a14) |
| A15 | 客服 agent 10K 工单/天 <2s | generic | ⚠️ | ⭐⭐ | [A15](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a15) |
| A16 | 受限域三题族（银行/法律/医院） | generic | ⚠️ | ⭐⭐ | [A16](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md#a16) |
| B1 | 能适应新任务的 agentic AI system | Anthropic | ⚠️ | ⭐⭐⭐ | [B1](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b1) |
| B2 | ChatGPT 跨会话 memory | generic·Humans& 对口 | ✅ | ⭐⭐⭐ | [B2](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b2) |
| B3 | 多人 + 多 Agent Shared Workspace | Humans& | 🧪 | ⭐⭐⭐ | [B3](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b3) |
| B4 | Computer-use Agent Sandbox 与 Tool Harness | Hark | 🧪 | ⭐⭐⭐ | [B4](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b4) |
| B5 | Enterprise Agent Eval Harness 与 Reward Hacking | Applied Compute | 🧪 | ⭐⭐⭐ | [B5](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b5) |
| B6 | Eval 平台题族（50 workflows / GDM harness / 反馈闭环） | generic·AC 对口 | ⚠️ | ⭐⭐⭐ | [B6](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b6) |
| B7 | 多 agent 委派系统 + 失败模式 | generic | ✅ | ⭐⭐ | [B7](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b7) |
| B8 | Agent Tool-use System Design | TikTok | ⚠️ | ⭐⭐ | [B8](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b8) |
| B9 | GDM Applied AI ML SD 官方考纲 | GDM | ⚠️ | ⭐ | [B9](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/B_general_design.md#b9) |
| C1 | 手搭 Claude agent loop（股票价格 tool use） | Anthropic | ✅ | ⭐⭐⭐ | [C1](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c1) |
| C2 | Durable Function Call Cache（key + WAL） | Anthropic | ✅ | ⭐⭐⭐ | [C2](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c2) |
| C3 | onsite AI-assisted coding 轮（Claude Code CLI） | Anthropic | ✅ | ⭐⭐⭐ | [C3](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c3) |
| C4 | FDE 55min CodeSignal "build an agent" | Anthropic | ✅ | ⭐⭐⭐ | [C4](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c4) |
| C5 | 线程安全 rate limiter（多级 follow-up） | Anthropic | ✅ | ⭐⭐⭐ | [C5](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c5) |
| C6 | debug GRPO training loop（3 bug + ratio≠1） | Anthropic | ✅ | ⭐⭐⭐ | [C6](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c6) |
| C7 | Applied AI 轨题族（retrieval scorer / token allocator / take-home） | Anthropic | ⚠️ | ⭐⭐⭐ | [C7](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c7) |
| C8 | Weighted DataBatcher 确定性 checkpoint | Anthropic | ⚠️ | ⭐⭐⭐ | [C8](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c8) |
| C9 | TS/React debugging round（禁 AI） | Sierra | ✅ | ⭐⭐⭐ | [C9](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c9) |
| C10 | Markdown 按 header 层级分块 | Sierra | ✅ | ⭐⭐⭐ | [C10](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c10) |
| C11 | Debug 日志区间合并 + overlap/gap | Sierra | ✅ | ⭐⭐⭐ | [C11](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c11) |
| C12 | 官方 Plan→Build→Review（2h AI build） | Sierra | ✅ | ⭐⭐⭐ | [C12](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c12) |
| C13 | 官方试点：draft PR + coding agents 改进 | Sierra | ✅ | ⭐⭐⭐ | [C13](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c13) |
| C14 | 电面风格样本（循环引用 / keyboard undo-redo） | Sierra | ✅/⚠️ | ⭐⭐⭐ | [C14](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c14) |
| C15 | 通用 AI-allowed live coding（1–2K 行 codebase） | generic·本周通用格式 | ✅ | ⭐⭐⭐ | [C15](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c15) |
| C16 | agentic coding beta（现有 codebase + AI） | OpenAI | ⚠️ | ⭐⭐ | [C16](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c16) |
| C17 | AI-enabled coding round（三面板） | Meta | ✅ | ⭐⭐ | [C17](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c17) |
| C18 | Chatbot OOD 家族（ChatApp / refactor） | OpenAI | ✅ | ⭐⭐ | [C18](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c18) |
| C19 | 看视频复刻流式聊天 UI | OpenAI | ✅ | ⭐⭐ | [C19](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c19) |
| D1–D19 | agent 基础/eval/安全/memory 快问 | generic | ✅ | – | [D](?book=drustz-interview-2026&section=agent-questions&question=drustz-9d5b52c44f5252c7ab) |
| D20 | agentic training 工具返回 mask | 快手（跨公司考点） | ⚠️ | – | [D20](?book=drustz-interview-2026&section=agent-questions&question=drustz-9d5b52c44f5252c7ab) |

## 完整解答

26 道题已有完整解答（A11 与 A10 共用一份，共 25 个文件）——先自己限时作答，再对照解答查缺。

- **Sierra**：[A1 客服 agent take-home](?book=drustz-interview-2026&section=agent-questions&question=drustz-e339aece19ea4dc750) ｜ [A2 订阅取消](?book=drustz-interview-2026&section=agent-questions&question=drustz-75a1d5d16c4e2aca2d) ｜ [C9 TS/React debugging](?book=drustz-interview-2026&section=agent-questions&question=drustz-84edd1277eae5e2399) ｜ [C10 Markdown 分块](?book=drustz-interview-2026&section=agent-questions&question=drustz-ae067731a574d11a60) ｜ [C11 日志区间合并](?book=drustz-interview-2026&section=agent-questions&question=drustz-ea71b8b4d979233d94) ｜ [C12 Plan→Build→Review](?book=drustz-interview-2026&section=agent-questions&question=drustz-b79f6b2a35b4cc0c0f) ｜ [C13 draft PR round](?book=drustz-interview-2026&section=agent-questions&question=drustz-4a07cf1ba370057d96)
- **Anthropic**：[A5 Batch API](?book=drustz-interview-2026&section=agent-questions&question=drustz-511499f433f1ec6716) ｜ [A6 Prompt Playground](?book=drustz-interview-2026&section=agent-questions&question=drustz-a3f95a672539bfe129) ｜ [A7 Design ChatGPT](?book=drustz-interview-2026&section=agent-questions&question=drustz-b6f2567ca90d9516d4) ｜ [A8 权重分发](?book=drustz-interview-2026&section=agent-questions&question=drustz-a128f631d8dab91fc6) ｜ [B1 自适应 agent](?book=drustz-interview-2026&section=agent-questions&question=drustz-25ff030951a05f473a) ｜ [C1 股票 agent loop](?book=drustz-interview-2026&section=agent-questions&question=drustz-316f3c2c38b3a50173) ｜ [C2 Durable Cache](?book=drustz-interview-2026&section=agent-questions&question=drustz-f1e2141227ee03a6bc) ｜ [C4 build an agent](?book=drustz-interview-2026&section=agent-questions&question=drustz-cebf765a31b8312976) ｜ [C5 rate limiter](?book=drustz-interview-2026&section=agent-questions&question=drustz-67e47e8dac3ab7adb8) ｜ [C6 GRPO debug](?book=drustz-interview-2026&section=agent-questions&question=drustz-a23b472ed3ba1b5d1e) ｜ [C8 Weighted DataBatcher](?book=drustz-interview-2026&section=agent-questions&question=drustz-6997781bde8be3ca8d)
- **Extend**：[A3 文档自动化管线](?book=drustz-interview-2026&section=agent-questions&question=drustz-a468477bfe21732bee) ｜ [A4 保险理赔文档 agent](?book=drustz-interview-2026&section=agent-questions&question=drustz-95a7a7b86086109e08)
- **Humans&**：[B2 ChatGPT memory](?book=drustz-interview-2026&section=agent-questions&question=drustz-8d300a7aef5c1cea82) ｜ [B3 Shared Workspace](?book=drustz-interview-2026&section=agent-questions&question=drustz-b8616a5c0778e35b1e)
- **Hark**：[B4 Computer-use Sandbox](?book=drustz-interview-2026&section=agent-questions&question=drustz-0ffee857b00cec8408)
- **Applied Compute**：[B5 Eval Harness](?book=drustz-interview-2026&section=agent-questions&question=drustz-46d8037ed5b42022ff)
- **OpenAI / generic**：[A10 企业级 RAG](?book=drustz-interview-2026&section=agent-questions&question=drustz-5459a213c9a546aa52)（A11 共用）

## 使用建议

- **7/15 Sierra 前**：C9→C10→C11→C12→C13→C14 + A1→A2，再扫 D 全部
- **7/22 Anthropic 前**：C1→C2→C4→C5→C6→C7 + A5→A6→A7→A8 + B1
- **Applied Compute / Hark / Humans& / Extend**：对应 🧪 题（B3/B4/B5/A4）+ 对口题（B2/B6/A3），配合 [../06_company_briefs.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d2c49a5fc736d572d1)
- 每题按 [../02_playbook.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d48438e1a63e68f6a5) 的 60 分钟节奏干练：澄清 5–7 min → 设计 10 min → 实现/展开 30 min → 测试复盘 10 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/05_questions/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
