---
id: company-zhipu
section: companies
order: 5
level: A
title: 智谱 Agent：为什么这份公开面经特别值得完整刷？
quick: >-
  因为它把 post-training、Agent data、模型 sizing 和 coding
  串在同一轮：DPO/GRPO、正负样本长度、tool-response loss mask、MCP 数据、参数量/KV Cache、streaming
  parser。
tags:
  - Zhipu
  - Agent
  - 真题导航
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 智谱 Agent 真实面经
    url: 'https://www.nowcoder.com/feed/main/detail/24952c828c59435abd3c302c97fa358d'
    type: legacy-reference
---

这份智谱 Agent 面经值得整轮模拟。这块容易直接答成只看答案，不补为什么、失败模式、怎么验证。它把 objective、数据边界和 serving 细节串在同一场：既要会 DPO/GRPO，也要把 trajectory 落到 parser、tool protocol、KV。按原帖逐题过，每题至少追加三层追问，而不是收集标题。

## 准备主线

1. **偏好与长度**：DPO/GRPO 公式能写；正负样本长度差会污染隐式奖励。GUI / pair 长度见 `zhipu-dpo-gui-pair-length`，推导见 `code-dpo`、`pt-dpo-derive`，组内优势见 `code-grpo`、`pt-grpo`。
2. **Agent 数据边界**：tool-response 必须 loss mask，否则学复读观察（`pt-tool-mask`）；MCP 数据与目录信任（`agent-mcp`、`mcp-tool-catalog-trust`）。
3. **Sizing 与 serving**：参数量 / KV Cache 估算（`code-sizing`、`code-kv-cache-step`、`arch-kv-cache`）；流式工具调用要状态机 parser（`code-stream-parser`），不能正则切半包。

## 本手册真题卡

点击下面每条即可跳到对应题。

- `zhipu-dpo-gui-pair-length`：正负样本长度如何影响 DPO / GUI pair
- `code-dpo` / `pt-dpo-derive`：DPO 手撕与推导
- `code-grpo` / `pt-grpo`：GRPO 目标
- `pt-tool-mask`：tool-response loss mask
- `agent-mcp` / `mcp-tool-catalog-trust`：MCP 数据与目录
- `code-sizing` / `code-kv-cache-step` / `arch-kv-cache`：参数量与 KV
- `code-stream-parser`：streaming parser

## 追问

- **为什么同一轮会问 parser？** Agent 岗要把协议落到半包、重试和工具边界。只训 loss 过不了 serving。
- **长度差为什么要命？** chosen 更长时 DPO 会学写长，见长度卡。要控制 pair 长度或归一。
- **如何模拟这场面？** 按原帖逐题，每题强制问失败模式和验证。id 已列全，不要只背 30 秒回答。
