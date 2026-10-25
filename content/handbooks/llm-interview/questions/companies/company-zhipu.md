---
id: company-zhipu
section: companies
order: 5
level: A
title: 智谱 Agent：为什么这份公开面经特别值得完整刷？
quick: "这份智谱面经在同一轮里串起了后训练、Agent 数据、模型规模估算和代码题，包括 DPO/GRPO、正负样本长度、tool-response 的损失计算范围、MCP 数据、参数量与 KV Cache，以及流式 parser，很适合整轮模拟。"
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

这份智谱 Agent 面经值得整轮模拟，因为它在同一场面试里同时考了训练目标、数据边界和推理服务细节：既要理解 DPO/GRPO，也要说明 Agent 轨迹怎么对应 parser、工具协议和 KV 缓存。

光看答案收获不大，每题都要补上为什么、失败模式和怎么验证。我的做法是按原帖逐题过，每题至少再往下追三层，光收集标题没什么用。

## 准备主线

1. 偏好和长度这块，DPO/GRPO 的公式要能写出来，还要知道正负样本长度差会污染隐式奖励。GUI / pair 长度见 `zhipu-dpo-gui-pair-length`，推导见 `code-dpo`、`pt-dpo-derive`，组内优势见 `code-grpo`、`pt-grpo`。
2. Agent 数据边界上，要明确 tool-response 参不参与损失计算，否则模型可能学会复述工具观测（`pt-tool-mask`）；MCP 数据和目录信任见 `agent-mcp`、`mcp-tool-catalog-trust`。
3. Sizing 和 serving 要会估参数量和 KV Cache（`code-sizing`、`code-kv-cache-step`、`arch-kv-cache`）。流式工具调用要用状态机 parser（`code-stream-parser`）处理还没接收完整的数据，光靠正则切分处理不了。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `zhipu-dpo-gui-pair-length`：正负样本长度如何影响 直接偏好优化（DPO） / GUI pair
- `code-dpo` / `pt-dpo-derive`：DPO 手撕与推导
- `code-grpo` / `pt-grpo`：GRPO 目标
- `pt-tool-mask`：tool-response 损失计算范围
- `agent-mcp` / `mcp-tool-catalog-trust`：MCP 数据与目录
- `code-sizing` / `code-kv-cache-step` / `arch-kv-cache`：参数量与 KV
- `code-stream-parser`：streaming parser

## 追问

**为什么同一轮会问 parser？**
Agent 岗要把协议落到半包、重试和工具边界上。只会解释训练损失，还做不出推理服务。

**长度差为什么这么要命？**
chosen 更长时，DPO 会学着写长，见 `zhipu-dpo-gui-pair-length`。要控制偏好对的长度差，或者做长度归一化。

**这场面试怎么模拟？**
按原帖逐题过，每题都逼自己回答失败模式和怎么验证。需要的 id 上面已经列全了。
