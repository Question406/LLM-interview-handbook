---
id: kuaishou-gqa-mqa-mla
section: arch
order: 142
level: A
title: 快手：除了 MHA，GQA / MQA / MLA 原理是什么？Decoder 的 QKV 从哪来？
quick: "Decoder 自回归时，当前 token 的隐状态算出 Q 和本步的 K/V，K/V 追加进缓存，和历史 K/V 一起做注意力。MQA 让所有 Q 头共享一组 KV，GQA 分组共享，MLA 把 KV 低秩压成 latent。三者都是在质量和 KV 显存之间取舍。"
tags:
  - Kuaishou
  - GQA
  - KV Cache
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手日常实习大模型算法面经
    url: https://www.nowcoder.com/feed/main/detail/9d24592752804d2790557f81230df62d
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“问kv cache相关”**；**“decoder的 qkv输入分别来自哪”**；**“除了MHA还知道哪些(GQA MQA MLA)讲原理”**

GQA、MQA、MLA 省的都是 KV cache。MQA 和 GQA 减少 KV 的头数，MLA 沿表示维把 KV 压成低维 latent。decode 往往卡在读 KV 的带宽上，$T^2$ 的训练 FLOPs 不是这一步的瓶颈，所以别把它们说成「少算一点 attention」。回答时我会先讲 QKV 从哪来，再讲各自压的是哪条轴。

## Decoder 的 Q、K、V

自回归走一步：当前隐状态 $h_t$ 乘 $W_Q$ 得到 $q_t$；历史的 $k_{1:t-1},v_{1:t-1}$ 已经在 KV cache 里，这一步只算 $k_t,v_t$ 并追加进去。Encoder-decoder 的 cross-attn 不一样，$q$ 来自 decoder，$k/v$ 来自 encoder 的记忆，cache 的是 encoder 那一侧，不会随 decode 步数增长。RoPE 加在 $q,k$ 上，$(R_t q_t)^\top(R_s k_s)=q_t^\top R_{s-t}k_s$；cache 里存旋转前还是旋转后的值，实现必须和推理一致。

## 三种省 cache 的切法

MHA 每个头都有独立的 KV，每个 token 大约存 $2 n_h d_h$，质量最好，cache 也最大。MQA 让所有 Q 头共享一对 KV，$n_{\mathrm{kv}}=1$，cache 最小，头之间的独立性也最差。GQA 取中间，$1\lt n_{\mathrm{kv}}\lt n_h$，几个 Q 头共享一组 KV，LLaMA / Qwen 常用这个中间点。

MLA（DeepSeek）换了一条轴，主要沿表示维压，不光是砍头数。隐状态先投到低维的 $c_t^{KV}=W^{DKV}h_t$，$d_c\ll n_h d_h$，RoPE 需要的部分再拆出一段短的 $k^R$。推理时用矩阵吸收，不必还原出全长的 K/V。它和 GQA 压的轴不同，见 `arch-mla`。

FFN 那一侧用 SwiGLU 还是 MoE，和 KV 布局互不相干：专家路由不会让 decode 的 cache 变小。

## 追问

**省的是计算还是字节？**
主要是字节。Prefill 仍然接近 $O(T^2 d)$；decode 省的是每一步读 cache 的字节数。

**GQA 能和 MLA 叠在一起吗？**
能设计组合，因为两者的轴不同。但 head、latent、RoPE 的维度都要重新定义，没法当两个开关随手一起打开。

**MQA 质量为什么容易掉？**
所有头抢同一份 $k,v$，表达容量不够。GQA 用分组把这部分容量买了回来。
