---
id: sys-rl-cont-batch-onpolicy
section: systems
order: 272
level: S
title: RL 训练开 continuous batching，会破坏 on-policy 边界吗？
quick: >-
  Serving 里 continuous batching 只为减少空等。RL 还要每条样本带着 policy 版本、old logprob、以及所属
  prompt group。动态插入会把不同 $\theta$ 的轨迹混进同一训练 batch，组内 $G$ 条完成时间也被打散。引擎可以开连续调度，但数据面必须记录版本、组齐了再算优势。
tags:
  - Continuous Batching
  - On-policy
  - vLLM
  - SGLang
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: 'Orca: A Distributed Serving System for Transformer-Based Generative Models'
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: vLLM PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: SGLang
    url: https://lmsys.org/blog/2024-01-17-sglang/
    type: primary
---

Continuous batching 为什么涨吞吐，见 `sys-cont-batch`。那张卡讲的是引擎内部交错请求。本题问的是 **把它接到 GRPO 数据面之后会怎样**。Serving 只关心 tokens/s；RL 还关心这条轨迹是不是当前 $\pi_{\mathrm{old}}$ 采的、同一 prompt 的 $G$ 条是否还在一组。

## 会打散的三本书

1. **Policy 版本。** 调度器随时插入新请求时，trainer 可能已经 `update_weights`。同一训练 batch 里会出现 $v$ 和 $v+k$ 的样本。ratio 必须用对应版本的 old logprob，否则 $\rho$ 是错的。
2. **Group。** GRPO 的均值在 prompt 组内算。连续调度让短回复先结束、长回复还占着 KV，组可能迟迟不齐。先到的 $G-1$ 条不能提前当一组归一化，否则 baseline 变了。
3. **确定性。** 动态 batch 改变 kernel shape 和 reduction 顺序，同一 prompt 在温度 0 下也可能和离线评测对不上，见 `sys-batch-invariance`。

长尾请求占着 KV 页，会饿死后面的短题，这和普通 serving 的公平性是同一类病，但 RL 里还会拖高 stale。训练端 backpressure 让 rollout 队列堆积，又是第二条 stale 来源，见 `sys-staleness`。

## 合法用法

连续 batching 仍然该开：组内长度方差极大，静态 generate 几乎总在等最长 CoT，见 `sys-rl-why-vllm-rollout`。工程上要约束：

- 每条轨迹写 `policy_version`、token、old logprob。
- 优势估计等组齐；动态采样也是组级滤，见 `slime-dynamic-partial`。
- 版本差过大就丢或走 TIS / CISPO，不要假装 $\rho=1$。

vLLM 强在 PagedAttention 和通用吞吐；SGLang 强在 RadixAttention、共享前缀和结构化 / 多轮 workflow。选型见 `sys-verl-vllm-vs-sglang`。无论哪个引擎，采样 logp 都要在训练图重算。

Continuous batching 和异步 RL 不是一层：前者是 decode step 内换人；后者是 trainer 与 rollout 两池流水线。可以同时开，stale 来源变成两条，账要分开记。

## 追问

- **组没齐能不能先训已经完成的题？** 可以，但那题的 $G$ 条必须都在，且版本相同。不能拿「先完成的 4 条」当 $G=8$ 的组。
- **prefix cache 在 RL 里安全吗？** 同版本、同权重下复用 prompt 前缀 KV 是对的。权重一更新就必须 flush，否则 prefix 是旧 $\theta$ 算的。
- **这能解释 clip fraction 乱跳吗？** 能。混版本 batch 会让 $\rho$ 分布双峰。先画 version histogram，再调 $\varepsilon$。
