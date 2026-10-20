---
id: company-kimi
section: companies
order: 6
level: A
title: Moonshot / Kimi：Agent 方向值得重点读哪些东西？
quick: >-
  我会重点看 agentic data、long-context、tool use、orchestration、Agent Swarm / PARL 和
  multi-agent credit assignment，不会只停在模型 benchmark。
tags:
  - Moonshot
  - Kimi
  - Agent
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ Kimi K2
    url: 'https://arxiv.org/abs/2507.20534'
    type: legacy-reference
  - title: ↗ Kimi K2.5
    url: 'https://arxiv.org/abs/2602.02276'
    type: legacy-reference
---

Kimi / Moonshot 方向，常见误区是：背榜单分数。K2 / K2.5 给面试的素材是：什么时候并行 sub-agent 真有收益、orchestrator 和 workers 怎么分 credit、冻结 workers 只训 orchestrator 会带来什么非平稳和能力上限。长上下文还会把「全塞 context vs retrieval / memory / skill」问成工程题，不是窗口越大越好。桌面 Agent 面经另有权限、多窗状态、结果护栏，不要用 chatbot 故事套过去。

## 准备主线

1. **Agentic data**：轨迹要含工具失败、澄清和长 horizon，不是只堆成功 demo。对照 `minimax-data-quality-gpt`、`byte-agent-posttrain-data-stage` 的阶段划分，讲清监督微调（SFT）如何教会调用格式，以及强化学习（RL）如何学习可验证的探索。
2. **Long-context vs 检索**：全塞会贵且脏；检索、memory、skill 各解决什么。相关工程见 `pdd-long-context-cheap`、`agent-mcp`。
3. **编排与 credit**：并行 sub-agent 何时缩短实际耗时、何时因汇总损失失败；冻结 worker 训 orchestrator 时环境非平稳。
4. **桌面 / 本地 Agent**：本地文件权限、多窗状态、任务中心、多模态上下文、结果护栏。见下列 moonshot 卡。

## 本手册真题卡

点击下面每条即可跳到对应题。

- `moonshot-desktop-local-file-permission`：本地文件权限怎么收
- `moonshot-desktop-multiwindow-state`：多窗状态如何一致
- `moonshot-desktop-task-center`：任务中心如何编排
- `moonshot-desktop-multimodal-context`：多模态上下文怎么截
- `moonshot-desktop-result-guardrails`：结果护栏
- `agent-mcp`：MCP / 工具协议边界
- `pdd-long-context-cheap`：长上下文如何做便宜

## 追问

- **并行 sub-agent 何时有收益？** 子任务可独立、汇总可验证时有；共享可变状态或信用难分时，串行更稳。
- **冻结 worker 训 orchestrator 的风险？** worker 能力成上限，orchestrator 学到的是过时环境，上线换了 worker 后，调度器面对的环境可能与训练不同，产生 OOD 问题。
- **为什么不能只看 benchmark？** 榜单不暴露权限、状态和护栏失败。按 id 准备对照实验。
