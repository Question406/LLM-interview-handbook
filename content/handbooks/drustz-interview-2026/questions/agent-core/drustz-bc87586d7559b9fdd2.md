---
id: drustz-bc87586d7559b9fdd2
section: agent-core
order: 95
level: A
title: agentic2 · Agentic 面试冲刺（唯一入口）
quick: 作者完整文档 · agentic2 · Agentic 面试冲刺（唯一入口）
companies: []
tags:
  - DrustZ
  - 作者完整文档
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/README.md
    type: primary
---
# agentic2 · Agentic 面试冲刺（唯一入口）

⏱ 本文件 3 分钟读完 ｜ 生成于 2026-07-14，面向 7/14–7/22 面试周

## 怎么用（只有一条规则）

**打开 [00_day_plan.md](?book=drustz-interview-2026&section=agent-core&question=drustz-61b314748bc4760ca5)，看今天那一节，照做。** 其余文件都已经被编排进日程，不需要自己另外浏览。想要更舒服的阅读体验：双击 `viewer/index.html`（离线，可折叠、渲染公式、记录进度）。

本目录吸收了 `../agentic/`（v1）的全部精华并补齐缺口——v1 从此只作为 labs 代码和完整题目 rubric 的存放处，不需要再读它的笔记。

## 文件地图

| 文件 | 一句话 | 你会在哪天用到 |
|---|---|---|
| [00_day_plan.md](?book=drustz-interview-2026&section=agent-core&question=drustz-61b314748bc4760ca5) | **主线**：7/14–7/22 每天时间块 | 每天 |
| [01_core/](?book=drustz-interview-2026&section=agent-core&question=drustz-2bb5b8f40029c7a772) | 核心概念 6 篇（loop/tools、state/memory、harness/SWE、multi-agent、reliability、eval/security） | 7/14 通读，之后定点重读 |
| [02_playbook.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d48438e1a63e68f6a5) | 60 分钟答题剧本 + AI-coding 现场脚本 | 7/14 读，每场设计/coding 面复用 |
| [03_gaps/](?book=drustz-interview-2026&section=agent-core&question=drustz-0f26f52da57b4684c5) | 七个专题：RAG、MCP、streaming、cost/latency、scaling、agentic RL、self-improvement | 7/15–7/19 分散安排 |
| [04_benchmarks.md](?book=drustz-interview-2026&section=agent-core&question=drustz-bfcfde342edce07d03) | SWE-bench/τ-bench/GAIA 等速查 + 追问备答 | 7/17–18 |
| [05_questions/](?book=drustz-interview-2026&section=agent-questions&question=drustz-1926d7a309fddb7eea) | 真题库 35+ 道（A 场景 / B 泛化 / C 实操 / D 快问），带来源和置信度 | 7/14–7/21 分散安排 |
| [06_company_briefs.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d2c49a5fc736d572d1) | 公司速记卡（按面试日期排） | 每场面试前 30 min |
| [07_labs_guide.md](?book=drustz-interview-2026&section=agent-core&question=drustz-aaa159205303abe02d) | v1 五套可跑 labs 的使用指南 | 7/14、7/16、7/19、7/20 |
| [08_cheatsheet.md](?book=drustz-interview-2026&section=agent-core&question=drustz-114f4be5164dd054f9) | 一页纸：协议/边界/高分句 Top15/万能结尾 | 每场面试前 15 min；7/21 默写 |

## 相关资产（不在本目录，日程会指过去）

- 可跑 labs（含测试）：`../agentic/labs/`，统一校验 `cd ../agentic && python3 scripts/run_all_checks.py`
- 完整题目 rubric（30 题 JSON）：`../agentic/data/questions.json`
- Mirendil take-home 专项：`../projects/takehome_mirendil/`（7/17 晚起主攻）
- RL 手写练习：`../new/drills/04_grpo_ppo.py`

## 延伸阅读 Top 10（只在错题暴露弱点时打开，读摘要+失败章节即可）

| # | 资料 | 分钟 | 对口 |
|---|---|---|---|
| 1 | [Sierra: The AI-native interview](https://sierra.ai/blog/the-ai-native-interview) | 12 | 7/15 前必读 |
| 2 | [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) | 18 | coding agent 面 |
| 3 | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 18 | loop/workflow 选型 |
| 4 | [Claude docs: How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) | 15 | 7/22 前必读 |
| 5 | [Anthropic: Writing effective tools](https://www.anthropic.com/engineering/writing-tools-for-agents) | 16 | tool design |
| 6 | [Anthropic: Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 18 | memory/context |
| 7 | [Anthropic: Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 18 | multi-agent |
| 8 | [Anthropic: Harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 16 | long-horizon |
| 9 | [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 18 | eval |
| 10 | [τ-bench 论文](https://arxiv.org/abs/2406.12045) | 20 | Sierra +  $\mathrm{pass}^k$  |

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
