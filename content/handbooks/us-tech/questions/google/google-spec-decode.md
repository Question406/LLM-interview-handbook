---
id: google-spec-decode
section: google
order: 18
level: S
title: Google：投机解码怎么保证无损，和 Medusa / EAGLE 差在哪
quick: >-
  草稿模型一次提 $\gamma$ 个 token，目标模型一次前向并行验证。按 $p/q$ 做拒绝采样，接受前缀再从修正分布抽一个，分布等于原模型。加速看接受率，不看草稿有多快。Medusa
  / EAGLE 是自投机：草稿来自同一套权重上的头或隐状态，概念同构，实现不是同一个小模型。
tags:
  - Google
  - Speculative Decoding
  - Inference
  - Sampling
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
  - title: Accelerating Large Language Model Decoding with Speculative Sampling
    url: https://arxiv.org/abs/2302.01318
    type: primary
  - title: "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads"
    url: https://arxiv.org/abs/2401.10774
    type: secondary
  - title: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty"
    url: https://arxiv.org/abs/2401.15077
    type: secondary
---

Google 的 Leviathan et al. 和 DeepMind 的 Chen et al. 几乎同时把「草稿 + 一次验证」写成无损加速。Gemini serving / 推理岗问这题，要听你把算法不变量和草稿从哪来拆开。KV 带宽见 `google-gqa-mqa`；这题不解决长上下文的 $T^2$，它只砍 decode 的逐步前向次数。

## 无损：验证是并行的，接受是串行前缀

记目标分布 $p$（大模型），草稿分布 $q$（小模型或草稿头）。草稿先自回归写出 $x_1,\ldots,x_\gamma$。目标模型用这 $\gamma$ 个 token 做一次前向（带上已有前缀的 KV），得到每个位置的 $p(\cdot\mid \mathrm{prefix})$。

逐个位置做拒绝采样：抽 $u\sim U[0,1]$，若

$$
u \le \min\bigl(1,\, p(x_i)/q(x_i)\bigr)
$$

则接受 $x_i$，继续看下一个；否则丢掉 $i$ 及之后的草稿，从修正分布 $\mathrm{normalize}(\max(0, p-q))$ 再抽一个 token。这一步保证输出分布等于 $p$，不是「小模型像了就当大模型」。DeepMind 那篇叫 speculative sampling，校正同一件事。

墙钟：原来每步一次大模型前向；现在每 $\gamma$ 个草稿位一次大模型前向，外加草稿自己的代价 $c$（相对大模型）。期望加速大致是 $(1+\mathrm{E}[\text{接受长度}]) / (c + \gamma\text{ 的摊销})$。真正的数是平均接受长度。$q$ 很接近 $p$，接受长，加速明显；代码、模板、低温度更香。开放域、高温度、事实性长尾，草稿动不动被拒，加速趋近 1，还可能更慢。

实现不变量：拒绝之后 KV cache 必须滚回接受前缀。只改输出文本、不改 cache，后续全错。这和连续批处理绑在一起，白板要提一句。

## 草稿从哪来：小模型 vs 自投机

经典配置：另训 / 另蒸馏一个同词表小模型当 $q$。词表必须对齐，否则 token 对不上。延迟上小模型也要能 batch，不然 $c$ 把红利吃光。蒸馏出草稿模型见 `google-distill-llm`。

自投机族不另跑一座小模型：

- Medusa：在已有 LM 的最后隐状态上加若干额外头，并行猜 $t+2,t+3,\ldots$。常配树状注意力，一次验证多条草稿前缀。训练多是后加头，不是从头改预训练目标。
- EAGLE：草稿发生在特征空间：用上一层隐状态加 token 嵌入，跑一个便宜的自回归头，再映射回词表。直觉是「下一 token 的不确定性在特征里比在 token 里更好预测」。
- Meta 的 multi-token 头是预训练就加多步 CE，推理再拿去投机，概念同类，训练阶段更早。

面试对照只抓三列：草稿计算图是否共享主干、验证是否仍用原 $p$、是否还做拒绝采样（无损）还是直接 argmax 拼上去（有损）。产品若能接受轻微分布漂移，有损会更快；Google 论文主叙事是无损。别把三个名字背成一种 kernel。

和「并行采样」别混：那是同时抽 $N$ 条完整样本做投票，见 `google-cot-reason`，付的是 $N$ 倍 decode。投机是同一条生成轨迹上少跑大模型步数。

## 我会主动报的错法

说投机改变了 $p$，那叫蒸馏或投机训练，不是这篇算法。说 $\gamma$ 越大越快：后面的草稿条件更远离 $p$，接受率掉，$\gamma$ 有最优不是单调。说 TPU 上不好做：验证步是标准前向，TPU 友好；难的是 decode 步 $B$ 小、草稿模型也要占 MXU，见 `google-tpu-llm`。

## 追问

- **温度怎么进公式？** $p$ 和 $q$ 都是加温之后的分布。两边温度不一致，校正不再对应你真正的采样策略。
- **草稿必须同词表吗？** 经典算法要同词表。跨词表要先对齐 token 边界，工程上几乎当新问题。
- **和 beam 的差别？** Beam 是搜索多条假设；投机是用便宜假设加速采样，默认仍是一条链。
- **失败模式？** 接受率随域漂。代码高、闲聊低。上线要按任务监控平均接受长度，不要只报离线 HumanEval 加速比。
