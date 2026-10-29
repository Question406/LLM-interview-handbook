---
id: openai-long-ctx-train
section: openai
order: 25
level: A
title: OpenAI：长上下文怎么训，RoPE 基频、续训和文档 packing
quick: >-
  我会先选定 RoPE 基频或插值方案，再用低学习率在真实长依赖数据上续训，并逐档验证中间位置。短文 packing 要隔开文档
  attention；只把窗口参数拉长或把短网页拼满，不能替代长文训练。
tags:
  - OpenAI
  - Long context
  - RoPE
  - Packing
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: 'https://arxiv.org/abs/2104.09864'
    type: primary
  - title: >-
      Extending Context Window of Large Language Models via Positional
      Interpolation
    url: 'https://arxiv.org/abs/2306.15595'
    type: primary
  - title: YaRN — Efficient Context Window Extension of Large Language Models
    url: 'https://arxiv.org/abs/2309.00071'
    type: primary
  - title: Code Llama
    url: 'https://arxiv.org/abs/2308.12950'
    type: primary
  - title: Lost in the Middle
    url: 'https://arxiv.org/abs/2307.03172'
    type: primary
---

## 可以这样回答

我会同时调整位置编码和训练数据，再验证长距离依赖是否真的学会。比如从 4k 基座扩到 32k、128k，光把短网页拼满窗口，模型仍可能只学会许多独立短篇，中间证据依然用不好。GPT-4 有 32k / 128k 产品窗口，这里的训练方法引用 RoPE、PI、YaRN、Code Llama 的公开配方，不冒充 OpenAI 内部实现。

我会先试 Code Llama 这类加大 $\theta$ 后续训的路径，把基频提高到 $10^5$–$10^6$，近处靠高频分辨，远处减少旋转圈数；Code Llama 公开用了 $10^6$。

## 技术备查

我会同时调整位置编码和训练数据，再验证长距离依赖是否真的学会。比如从 4k 基座扩到 32k、128k，光把短网页拼满窗口，模型仍可能只学会许多独立短篇，中间证据依然用不好。GPT-4 有 32k / 128k 产品窗口，这里的训练方法引用 RoPE、PI、YaRN、Code Llama 的公开配方，不冒充 OpenAI 内部实现。

## 基频、插值、续训

RoPE 第 $i$ 对维度的角频率 $\theta_i=\theta^{-2i/d}$，默认 $\theta=10^4$。位置 $m$ 的旋转是 $\theta_i m$。训练长度 $L$ 之外，高频相位是模型没见过的，直接把窗拉到 $8L$ 会糊。三条公开路：

我会先试 Code Llama 这类加大 $\theta$ 后续训的路径，把基频提高到 $10^5$–$10^6$，近处靠高频分辨，远处减少旋转圈数；Code Llama 公开用了 $10^6$。

另一条是 PI，把位置缩成 $m' = m\cdot L_{\mathrm{train}}/L_{\mathrm{target}}$，使目标窗落进原相位范围，代价是近处分辨率被稀释。NTK / YaRN 对不同频率区别处理，低频多放、高频少动，介于只改基频和统一缩位置之间，是社区公开外推方案。Llama 的具体概念可看 `meta-llama-rope`。

只改公式、不看长文档，模型仍然不会用中间那些 token。我会做 continual pretrain：从短窗 checkpoint 出发，压低 lr（常是预训练峰值的 $1/10$–$1/30$），在真实长文档上再跑一段，窗可以阶梯涨（8k → 32k → 128k）。数据必须是真的长依赖：仓库、书、长对话、论文，而不是把短网页 pack 满 128k 假装长上下文。后者模型只学到「很多短篇拼在一起」，Lost in the Middle 仍然会在中间位置掉点。

显存：激活随 $T$ 涨，checkpoint 和序列并行几乎必开，见 `openai-grad-checkpoint`。服务期滑窗是另一套，不能代替长窗训练，见 `openai-attention-sink`。

## packing：拼得满，但文档之间不要互看

短文档要 pack 满 $[B,T]$ 才不浪费。常见误区是直接 concat，让文档 A 的 token attend 到文档 B。模型会学到虚假跨文依赖，长窗评测时反而更爱抄隔壁。正确是文档级 attention mask：同一篇内因果，跨篇全挡。结束符可以当 sequence-boundary features，不能代替 mask。

```python
# 文档 id 是 [B, T]，同一篇同号
same = doc_ids[:, :, None] == doc_ids[:, None, :]
causal = torch.tril(torch.ones(T, T, dtype=torch.bool, device=x.device))
attn_mask = same & causal  # True = 可见
scores = scores.masked_fill(~attn_mask[:, None], float("-inf"))
```

损失只在有效 token 上算；pad 和跨篇位置走 ignore index。curriculum 可以先短后长，但每一档都要有该长度上的真实任务（复制针、多跳、全书问答），否则 loss 下降只说明短模式还在。

Lost in the Middle 是评测现象：证据在中间比在头尾差。训练上能做的是：长文档、位置均匀的监督、不要只把答案放在末段。它不是靠把 $\theta$ 再乘十就能消失的。

相关：`anthropic-long-context`、`msft-long-context`、`openai-rope-offset`

## 追问

**只插值不续训行不行？**
短外推有时能跑，长窗和中间位置通常要数据。产品 128k 不要赌零样本插值。
**packing 不加 mask 最坏怎样？**
模型把相邻无关文档当上下文，检索和引用会串台。throughput 看起来很高，评测是脏的。
**和 sink / 滑窗什么关系？**
滑窗是推理驱逐；长窗训练是让模型真的见过长距离。两者都要时，先保证 RoPE 下标，见 `openai-rope-offset`。
**Math 用 $6ND$ 算长窗续训吗？**
可以估 FLOPs，但 $D$ 应计新增长上下文 token，不要把短窗预训练的 token 再数一遍充数，见 `openai-scaling-laws`。

## 相关题

- [[meta-pack-seq]]：只讲本题 packing 那一节，更细地说明文档 mask、`position_ids` 重置和 SFT 的风险。
- [[coding-packed-lm]]：把文档 packing 写成代码，`cu_seqlens` 和块对角因果 mask 都要实现。
- [[meta-yarn-ntk]]：PI、NTK、YaRN 和改 `rope_theta` 的区别，本卡只把插值当一条旋钮带过。
- [[meta-llama-rope]]：Llama 3.1 的公开做法是提高 `rope_theta` 再续训长窗，可以当本卡的一个具体例子。
