---
id: sys-rl-cont-batch-onpolicy
section: systems
order: 272
level: S
title: RL 训练开 continuous batching，会破坏 on-policy data requirements 吗？
quick: >-
  Continuous batching 可以开，但轨迹必须记录 policy 版本和 old logprob，同一题的 $G$
  条要组齐后再算优势。权重更新和异步调度可能让同一 batch 混入不同版本，因此要按版本控制新鲜度，超出允许差距的样本丢弃或交给相应的 off-policy
  校正。
tags:
  - Continuous Batching
  - On-policy
  - vLLM
  - SGLang
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: 'Orca: A Distributed Serving System for Transformer-Based Generative Models'
    url: 'https://www.usenix.org/conference/osdi22/presentation/yu'
    type: primary
  - title: vLLM PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
  - title: SGLang
    url: 'https://lmsys.org/blog/2024-01-17-sglang/'
    type: primary
---

可以开 continuous batching，但要另外守住策略版本和 group boundaries。比如同一题需要 $G$ 条回答，短回复先完成了，也得等组齐后再算优势；中途更新过权重的样本还要记录各自的版本。引擎负责交错调度请求，GRPO 数据面则负责确认轨迹是否由对应的 $\pi_{\mathrm{old}}$ 采出。引擎内部怎样提高 throughput，见 `sys-cont-batch`。

## 需要分别记录的三类信息

1. **Policy 版本。** 调度器随时插入新请求时，trainer 可能已经 `update_weights`。同一训练 batch 里会出现 $v$ 和 $v+k$ 的样本。ratio 必须用对应版本的 old logprob，否则 $\rho$ 是错的。
2. **Group。** GRPO 的均值在 prompt 组内算。连续调度让短回复先结束、长回复还占着 KV，组可能迟迟不齐。先到的 $G-1$ 条不能提前当一组 normalization，否则 baseline 变了。
3. **确定性。** 动态 batch 改变 kernel shape 和 reduction 顺序，同一 prompt 在温度 0 下也可能和离线评测对不上，见 `sys-batch-invariance`。

长尾请求占着 KV 页，会饿死后面的短题，这和普通 serving 的公平性是同一类病，但 RL 里还会拖高 stale。训练端 backpressure 让 sampling 轨迹（rollout） 队列堆积，又是第二条 stale 来源，见 `sys-staleness`。

## 合法用法

连续 batching 仍然该开：组内长度方差极大，静态 generate 几乎总在等最长 chain of thought（CoT，即分步推理过程），见 `sys-rl-why-vllm-rollout`。工程上要约束：

- 每条轨迹写 `policy_version`、token、old logprob。
- advantage estimation 等组齐；动态 sampling 也是组级滤，见 `slime-dynamic-partial`。
- 版本差过大就丢或走 TIS / CISPO，不要假装 $\rho=1$。

vLLM 强在 PagedAttention 和通用 throughput；SGLang 强在 RadixAttention、共享前缀和结构化 / 多轮 workflow。选型见 `sys-verl-vllm-vs-sglang`。无论哪个引擎，sampling logp 都要在训练图重算。

Continuous batching 在逐 token 生成（decode）的 step 之间替换已结束的请求；异步 RL 则让 trainer 与 rollout 两个池子流水执行。两者可以一起开，但各自引入的 stale 要分开统计。

## 追问

**组没齐能不能先训已经完成的题？**
可以，但那题的 $G$ 条必须都在，且版本相同。不能拿「先完成的 4 条」当 $G=8$ 的组。
**prefix cache 在 RL 里安全吗？**
同版本、同权重下复用 prompt 前缀 KV 是对的。权重一更新就必须 flush，否则 prefix 是旧 $\theta$ 算的。
**这能解释 clip fraction 乱跳吗？**
能。混版本 batch 会让 $\rho$ 分布双峰。先画 version histogram，再调 $\varepsilon$。
