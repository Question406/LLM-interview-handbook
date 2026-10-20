---
id: dt-llama4-rl-recipe
section: posttrain-data
order: 31
level: S
title: Llama 4 博客里的 RL 数据配方是什么？
quick: "Llama 4 公开采用轻量 SFT、在线 RL、轻量 DPO。先去掉过易样本，再根据当前策略 pass@$k$ 动态筛题，丢弃零优势组，混合能力与提示模板。数据过滤随策略更新，不能只在训练前做一次。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "The Llama 4 herd (Meta)"
    url: https://ai.meta.com/blog/llama-4-multimodal-intelligence/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

公开流程是轻量 SFT、在线 RL，最后轻量 DPO 改善回复细节。SFT 过多可能限制后续在线探索，尤其在推理、代码和数学上。公开配方是 2025-04 Llama 4 技术博客的后训练节（Maverick）。

常见误区是：SFT 越多越好，或开训前滤一次就冻住题表。简单题占步数，零优势组没有梯度。

## 数据侧三刀

先减少简单 SFT 样本。用 Llama 判断 easy 后，小模型丢弃约 50%，Behemoth（约 2T 总参）丢弃到 95%。剩下难题做轻量 SFT。和 `dt-math-passk-band`、`dt-filter-too-hard` 同一方向。

在线 RL 跟着策略滤。用当前策略做 pass@$k$，只留中等到难的 输入提示（prompt）。训一轮，再用新策略滤一轮，循环。零优势的 prompt 动态丢掉。Behemoth 那节还写了按难度做 curriculum。这就是 `dt-agent-passk-zero` 的实验室配方。

同一 batch 混合数学、推理和代码，避免策略只向一个域偏移。系统提示要多样，不然指令跟随在推理 / 代码上会掉。Agent 版就是：不要让一个 batch 全部来自同一仓库、同一工具 schema。

连续在线 RL 还要求异步基础设施。那是系统卡。数据岗要会说：过滤是训练循环的一部分，不是开训前跑一次的静态表。

## Agent 怎么用

博客没写 SWE 容器细节，SWE-RL 是另一条（oracle patch 相似），见 `dt-agent-reward-spec`。现场把 Llama 4 当「题怎么进 RL 队列」：easy 砍、零优势砍、混能力、提示多样。环境仍要自己的 grader。

苹果：参考模型当 easy 法官可以，用户日志不能当 prompt 池。许可题库和合成环境按当前 AFM 学生模型重算 pass@$k$。

## 追问

- **DPO 还要吗？** 我会放最后、很轻，处理回复质量边角。主智力在 RL。
- **easy 法官会不会误杀？** 会。我会按能力分组统计，代码桶不要用聊天 easy 头。
- **和 R1 冷启动？** R1 也是少量 SFT 再 RL。Llama 4 多写了「SFT 过多有害」和在线滤题。我会按后半句做题表。
