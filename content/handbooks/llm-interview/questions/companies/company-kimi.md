---
id: company-kimi
section: companies
order: 6
level: A
title: Moonshot / Kimi：Agent 方向值得重点读哪些东西？
quick: >-
  Kimi 方向我会重点看 agentic data、long-context、tool use、orchestration、Agent Swarm /
  PARL 和 multi-agent credit assignment，模型 benchmark 只是起点。
tags:
  - Moonshot
  - Kimi
  - Agent
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ Kimi K2
    url: 'https://arxiv.org/abs/2507.20534'
    type: legacy-reference
  - title: ↗ Kimi K2.5
    url: 'https://arxiv.org/abs/2602.02276'
    type: legacy-reference
---

Kimi / Moonshot 方向，背榜单分数用处不大。K2 / K2.5 给面试的素材在别处：什么时候并行 sub-agent 真有收益，orchestrator 和 workers 怎么分 credit，冻结 workers 只训 orchestrator 会带来什么非平稳和能力上限。

长上下文也会被问成工程题：全塞进 context，还是走 retrieval / memory / skill，窗口越大并不就越好。桌面 Agent 的面经另外会问权限、多窗状态和结果护栏，比如让 Agent 整理一个本地文件夹，它能碰哪些目录、两个窗口同时操作时状态怎么保持一致，拿 chatbot 的故事套不过去。

## 准备主线

1. Agentic data 的轨迹要包含工具失败、澄清和长 horizon，光堆成功 demo 不够。对照 `minimax-data-quality-gpt`、`byte-agent-posttrain-data-stage` 的阶段划分，讲清 SFT 怎么教会调用格式，RL 怎么学可验证的探索。
2. Long-context 和检索的取舍在于全塞又贵又脏，要说清检索、memory、skill 各解决什么。相关工程见 `pdd-long-context-cheap`、`agent-mcp`。
3. 编排和 credit 要讲并行 sub-agent 什么时候能缩短实际耗时、什么时候会因汇总损失而失败，以及冻结 worker 训 orchestrator 时环境是非平稳的。
4. 桌面 / 本地 Agent 要准备本地文件权限、多窗状态、任务中心、多模态上下文和结果护栏，见下面的 moonshot 卡。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `moonshot-desktop-local-file-permission`：本地文件权限怎么收
- `moonshot-desktop-multiwindow-state`：多窗状态如何一致
- `moonshot-desktop-task-center`：任务中心如何编排
- `moonshot-desktop-multimodal-context`：多模态上下文怎么截
- `moonshot-desktop-result-guardrails`：结果护栏
- `agent-mcp`：MCP / tool protocol scope
- `pdd-long-context-cheap`：长上下文如何做便宜

## 追问

**并行 sub-agent 什么时候有收益？**
子任务能独立做、汇总结果能验证时有收益；要是共享可变状态，或者信用很难分，串行更稳。

**冻结 worker 训 orchestrator 有什么风险？**
worker 的能力就是上限，orchestrator 学到的是一个过时的环境。上线换了 worker，调度器面对的环境可能和训练时不同，就会出现 OOD 问题。

**为什么光看 benchmark 不够？**
榜单暴露不出权限、状态和护栏上的失败。按上面的 id 准备对照实验。
