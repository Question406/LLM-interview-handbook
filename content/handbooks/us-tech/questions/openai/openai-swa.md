---
id: openai-swa
section: openai
order: 32
level: A
title: OpenAI：sliding window attention 和全局 sink 怎么共存
quick: "滑窗后 softmax 仍要归一，sink 不会消失。共存有三种：全局层和窗层交替、少数全局 token 永远可见、分母里加学到的 sink logit。gpt-oss 用第一种加第三种。"
tags:
  - OpenAI
  - Sliding window
  - Attention sink
  - Long context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: gpt-oss-120b & gpt-oss-20b Model Card
    url: https://arxiv.org/abs/2508.10925
    type: primary
  - title: Longformer — The Long-Document Transformer
    url: https://arxiv.org/abs/2004.05150
    type: primary
  - title: Mistral 7B
    url: https://arxiv.org/abs/2310.06825
    type: primary
  - title: Efficient Streaming Language Models with Attention Sinks
    url: https://arxiv.org/abs/2309.17453
    type: primary
---

## 题怎么来的

满注意力 KV 随 $T$ 涨。滑窗（Longformer / Mistral）把每层可见历史限制在 $W$ 内。StreamingLLM 又说：满注意力训出来的模型，推理时若把句首一起扔掉，softmax 会崩，见 `openai-attention-sink`。OpenAI 公开的 gpt-oss 把两件事写进同一张模型卡：层间交替带宽 128 的窗和全密集，并且每个头在 softmax 分母里学一个 bias，使注意力可以谁都不看。推理岗要的是共存方式，不是背 128 这个数字当秘密。

## 窗把谁挡住，质量往哪倒

因果滑窗：位置 $t$ 的 query 只看见 $[t-W+1, t]$（再截到 0）。计算和 KV 都是 $O(W)$，不是 $O(T)$。Mistral 整网都是窗；gpt-oss / Gemma 2 是一层全图、一层窗交替。混合时窗层 cache 停在 $W$，全局层仍 $O(T)$，总 KV 大约减半（1:1 交替），不是减到 $O(W)$。

Softmax 仍强制 $\sum_j p_{t,j}=1$。窗口里没有「off」时，多余质量会倒向：

- 窗口里最老、几乎每个 query 都看见的那个 key（局部 sink，跟着窗滑）；
- 或你故意留在可见集合里的全局位（BOS、几个句首 文本处理单位（token））。

所以「上了 SWA 就不用管 sink」是错的。窗只是换了可见集合；归一化还在。反过来，只在推理时保留 StreamingLLM 的 $k$ 个句首 + 尾窗，那是驱逐策略，针对满注意力训出来的 checkpoint，和训练时就写死窗 mask 不是同一契约。面试第一句先问：这个权重是窗训的，还是满注意力训完再滑。

## 三种共存，别并成一个「sink」

1. 层混合。 奇数层满注意力，偶数层窗（gpt-oss：带宽 128，随 GPT-3 的 banded / dense 交替）。长距离事实走全局层；局部流畅走窗层。Cache 按层种类型分配：窗层环形缓冲，全局层线性涨。位置编码仍用绝对下标，不要把窗重编成 $0,\ldots,W-1$，见 `openai-rope-offset`。

2. Token 混合（Longformer）。 大多数位置只看窗；少数全局 token（CLS、任务 token）对所有 query 可见，它们也对全序列可见。实现是把全局 KV 拼在窗前面，mask 允许跨过中间被删的位置。Serving 上这就是「永远 pin 住这 $k$ 列」。

3. 分母 sink（gpt-oss）。 不是序列里的真 token。每头一个学到的 logit $\sigma$，

$$
p_j=\frac{e^{s_j}}{e^{\sigma}+\sum_k e^{s_k}}.
$$

$\sigma$ 大时质量可以倒向「虚无」，谁都不看。模型卡写明类似 off-by-one attention / attention sinks。StreamingLLM 的 $k=4$ 是保留位置 0 的 KV；gpt-oss 的 sink 是参数，不占序列、不进 cache。面试把两者说成同一个实现就混淆了两种机制。

StreamingLLM 仍可叠在满注意力模型的 逐 token 生成（decode） 驱逐上：cache 里留 sink KV + 最近 $W$，中间丢掉。窗训模型没有「位置 0 必须在」的契约，但窗左端仍可能变成吸收多余注意力概率的位置；这时学到的 $\sigma$ 比强行 pin 句首更干净。

RoPE：剩下的 key 带着原来的绝对位置旋。滑窗丢中间 KV 后若重编号，相对差全变，和 `openai-attention-sink` 同一类 silently wrong。

常见误区是：说 SWA 把复杂度变成 $O(1)$ 就没有 sink；把 gpt-oss 的 bias 说成「永远 attend BOS」；把训练窗和推理驱逐当成同一开关。

## 追问

- **全窗、没有全局层，长距离怎么走？** 信息要一层一层沿窗传，有效感受野大约 $L\cdot W$。$W=128$、层数不够时，针在干草堆里会丢。所以 gpt-oss 留了密集层，并给密集层上到 128k（YaRN），见 `openai-long-ctx-train`。
- **窗层还要不要 FlashAttention？** 要。局部 $S$ 也不该写回 HBM。Decode 时窗层 $T=W$ 很小，split-K 往往不划算，见 `openai-flash-decode`。
- **推理时给窗层也 pin 句首？** 窗训模型通常不必。满注意力模型的 streaming 要 pin。先看训练 mask。
- **和 GQA？** 正交。GQA 减头数，SWA 减时间维。gpt-oss 两者都用。
