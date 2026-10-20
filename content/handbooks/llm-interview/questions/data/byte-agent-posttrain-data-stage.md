---
id: byte-agent-posttrain-data-stage
section: data
order: 100
level: S
title: 字节 AI 数据技术：Agent 后训练的 SFT / RL 数据怎么设计，何时切 RL？
quick: "监督微调（SFT）先训练合法的工具调用格式、工具和参数选择、状态跟踪、失败恢复与安全边界。强化学习（RL）再探索模型已经具备、但表现不稳定的可验证能力。是否切换，要看留出任务的轨迹成功率、格式合规率、奖励能否区分好坏，以及探索覆盖情况，不能只看 epoch 或 loss。"
tags:
  - ByteDance
  - Agent Post-training
  - SFT Data
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 4.28 字节 AI数据技术一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/8e812a2e2b824779bea596a90d7603e0?sourceSSR=enterprise
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 团队 / 岗位：AI 数据技术
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-28
- 来源类型与可信度：牛客候选人原帖，B（岗位、轮次与题单明确；届别、面试日期未披露）
- 原始措辞：**“如果让你做Agent方向的后训练，SFT数据怎么设计？RL数据怎么设计？SFT做到什么程度可以开始做RL？”**

常见误区是：按固定 epoch 或「loss 够低了」切 强化学习（RL），以及 监督微调（SFT） 只放最终正确答案。Agent SFT 要覆盖可执行格式，RL 要覆盖已会但不稳的可验证探索。切分看 held-out 轨迹成功、格式合规、奖励分数（reward） 能否区分好坏组，不要看步数。

## SFT：分层覆盖，别只堆成功调用

SFT 集需要：任务意图、可调用工具集合、合法 JSON / 参数、观测结果（observation） grounding、多步 state、拒绝与澄清、timeout / tool error recovery、安全终止。按任务、工具、失败类型、轨迹长度、风险等级分层，防止最多的简单 工具调用 主导 损失（loss）。环境返回的 token 排除在损失计算之外（见 `pt-tool-mask`）。实验：去掉「失败恢复」桶再训，held-out 超时任务应掉。这样才能判断这类数据是否带来了额外收益。

## RL：用当前策略新采样的轨迹，先看组是否可分

RL 数据来自当前策略在可复现环境中新采样的轨迹，保留成功、近成功、有诊断价值的失败。开始 RL 的门禁我一般要求同时满足：

- 格式合法率高于阈值（否则 reward 全打在 parse 失败上）；
- held-out 基础任务显著高于随机探索；
- 同一输入提示 的组内对错混合，优势 $\hat A_i$ 非常数；若绝大多数组全对或全错，先改难度 / SFT 覆盖 / reward，不要加大 RL 步数。

对照：只加 SFT 步数 vs 达门禁后开 RL，报告格式率、任务成功、钻奖励规则的空子 率。

## 追问

- **loss 降了能开 RL 吗？** 不能。Loss 可被简单调用刷低。看 holdout 成功与组内区分度。
- **RL 为什么要 用当前策略新采样的轨迹？** 离线轨迹对当前策略 off-policy，优势偏差大；环境版本一变还不可回放。
- **全对组怎么办？** 优势为 0，这一 step 无效。提高难度或动态采样，见 GRPO 零优势卡。
