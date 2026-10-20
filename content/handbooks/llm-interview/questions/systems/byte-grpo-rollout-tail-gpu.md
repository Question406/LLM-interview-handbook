---
id: byte-grpo-rollout-tail-gpu
section: systems
order: 100
level: S
title: 字节 27 暑期：GRPO rollout 长尾拖低 GPU 利用率，工程上怎么解？
quick: "我会把问题拆成生成、调度和训练三段：连续 / 动态 batching、长度感知分组统计、每组完成即送训、截断与预算控制、异步 actor-learner 解耦。但要盯 policy freshness，不能只靠堆并发把 off-policy 盖住。"
tags:
  - ByteDance
  - 2027 Summer Intern
  - GRPO
  - RL Infrastructure
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节27暑期 大模型算法一面凉经分享（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/28b254940eb940189188d795f4606c52?urlSource=home-api
    type: candidate-first-hand
  - title: vLLM
    url: https://arxiv.org/abs/2309.06180
    type: primary-paper
---
## 真题记录

- 公司：字节跳动
- 团队 / 岗位：大模型算法
- 届别 / 流程：27 届暑期实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GRPO中roll out过程的长尾问题，导致GPU使用率低，有什么工程上的解决方案”**

常见误区是：「加大并发」或「把 max_len 砍短」。GRPO 一个 group 要等最慢那条样本，generation worker 空转、padding 变厚、learner 出现 bubble。要先分清是 逐 token 生成（decode） 长尾还是工具 I/O 长尾，再动调度；异步化会引入 off-policy，必须管 freshness。相关卡：`infra-rl-rollout-optimize`、`slime-dynamic-partial`、`sys-cont-batch`。

## 先测量尾部是谁

收集生成长度分布、工具等待时间、拒答 / retry 比例和 per-GPU idle。模型 decode 长尾：少数超长 思维链（CoT，即分步推理过程） 拖住整组。环境长尾：搜索 / 沙箱超时。两者的处理方法不同。前者分组统计、预算、连续 batch；后者并发可交换 action、超时与缓存。不要在没直方图时直接改 `max_new_tokens`。

## 调度：分组统计、连续 batch、组完成即送训

长度感知 packing / 分组统计，减少为一条长样本 pad 整组。推理引擎侧用连续 batching，结束的请求立刻让位。token 或时间预算加可审计截断，避免无限想。已完成的 group 尽早后处理、算优势、进 learner，不必等全局 step 里最慢的 bucket。工具型任务对幂等查询缓存，对可交换工具并行。这些都能抬 GPU 有效 token，但截断会改奖励分布，要在日志里打标。

## 异步的代价是旧策略

actor 与 learner 解耦、backlog 设上限，能掩盖 bubble，但 采样轨迹（rollout） 用的是旧权重。必须记录 policy version、age 分布、有效样本比例和 holdout；超过 freshness 阈值的样本丢弃或做受控修正（IS / TIS）。用过 slime 时落到开关：`--partial-rollout` + abort 回收半成品，长尾 Agent 换 `train_async.py` / `generate_rollout_fully_async`，旧 prefix 用 `--mask-offpolicy-in-partial-rollout` 或 `--use-tis`。见 `sys-staleness`、`slime-async-train`。

## 追问

- **只砍 max_len 行不行？** 能降尾部，但可能砍掉可解轨迹，奖励分数（reward） 失真；要可审计并看 holdout。
- **连续 batch 为什么有用？** decode 步里短请求结束立刻填新请求，减少为长尾 pad 的空算力。
- **partial rollout 的正确性？** 半成品要掩码或修正，否则用过期 prefix 训当前策略。
- **如何证明 GPU 利用率真的好了？** 看 tokens/s、idle 时间、group 完成时间 P99，而不是只看瞬时 SM%。
