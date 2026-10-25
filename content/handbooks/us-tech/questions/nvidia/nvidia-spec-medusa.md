---
id: nvidia-spec-medusa
section: nvidia
order: 25
level: A
title: NVIDIA：Medusa / EAGLE 多头草稿，和经典投机解码差在哪
quick: "差别主要在草稿生成：经典投机解码运行另一个小模型，Medusa 在骨干上挂 $K$ 个并行头，EAGLE 用浅层模块自回归预测特征。候选仍由目标模型验证；要保持原模型的输出分布，就要使用相应的严格接受和修正规则，不能直接输出草稿。"
tags:
  - NVIDIA
  - Speculative Decoding
  - Medusa
  - EAGLE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
  - title: Medusa — Simple LLM Inference Acceleration Framework with Multiple Decoding Heads
    url: https://arxiv.org/abs/2401.10774
    type: primary
  - title: EAGLE — Speculative Sampling Requires Rethinking Feature Uncertainty
    url: https://arxiv.org/abs/2401.15077
    type: primary
  - title: Speculative Sampling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html
    type: primary
---

经典投机、Medusa 和 EAGLE 都想用便宜的草稿减少目标模型逐 token 前向的次数，主要区别是草稿从哪里来。经典方法另跑一个小模型，Medusa 让同一个隐状态上的多个头并行猜后续位置，EAGLE 用浅层模块在特征上自回归预测。候选的生成和验证要分开看：草稿便宜并不保证接受率高。

TensorRT-LLM 文档列出了独立 draft 模型和 Medusa 头，EAGLE 也进入了 serving 栈。严格验证的基础见 `google-spec-decode`；这里继续看多头、特征草稿、KV 回滚，以及它们和 in-flight batching（IFB）的配合。

经典的 Leviathan / Chen 方法先让草稿模型 $q$ 自回归写出 $x_1,\ldots,x_\gamma$，目标 $p$ 一次前向得到这 $\gamma$ 个位置的 logits。位置 $i$ 抽 $u\sim U[0,1]$，若 $u \lt p(x_i)/q(x_i)$ 则接受，否则从修正分布再抽一个并截断后面。期望接受长度决定加速比，不是草稿 FLOPs。GPU 小 batch 时 逐 token 生成（decode） 吃不满，一次验证摊掉 $\gamma$ 步的权重读取，这才是投机的 roofline，见 `nvidia-flash-decode`。

代价是同时驻留第二个模型，维护两套 KV 和调度。草稿过强会拖慢自己，过弱则可能把 $\gamma$ 个候选全部拒绝，白做一次验证。拒绝后 target 和 draft 的 KV 都要截回接受前缀，否则注意力会继续读到已被丢弃的 token。Paged 上就是把多出来的页 refcount 减掉，见 `nvidia-paged-kv`。

## Medusa：同一隐状态上的独立头

Medusa（Cai et al.）不另训小 Transformer。骨干最后一层隐状态 $h_t$ 上挂 $K$ 个头：头 $k$ 直接预测 $t+k$ 的 token，头与头之间不互为条件。一次骨干前向得到 $K$ 个候选位置，再靠 top-$s$ 叉出一棵树，用树状注意力一次验证多条路径。接受的是树上的一条前缀。

这些头只有几个线性层，草稿 FLOPs 很小，也没有第二份 KV。但第 $k$ 个头看不到前面的草稿 token，虽然避免了自回归误差累积，也少了根据前文修正预测的机会，草稿质量通常较弱。

Medusa-1 冻结骨干、只训练头，接近无损加速；Medusa-2 连骨干一起训练，接受率可能更高，但原模型行为也可能改变。TRT-LLM 用 `medusa_choices` 配置树的分叉，IFB 路径要显式提供静态树。早期文档只官宣 Vicuna 一类，其他骨架需要接入相同的头。

树验证一步的 $Q$ 长度是候选节点数，不是 1，attention 更像一段短 prefill，占位和 CUDA Graph 档位都要按树大小留，见 `nvidia-cuda-graph`。

## EAGLE：特征层自回归

EAGLE 的出发点是在倒数第二层特征上自回归预测更容易，但特征还未确定对应哪个 token。它把已经采样的 token 前移一位，与特征一起送进草稿模块，补上这部分不确定性。草稿模块很小：一层 decoder + 投影，embedding 和 LM head 借用目标模型。

于是草稿是短自回归，但每步是特征而不是再跑 $L$ 层。接受率通常高于独立 Medusa 头，仍走同一套拒绝采样 / 树验证。EAGLE-2 按置信度动态长树；EAGLE-3 改成更靠多层特征、token 侧预测。因此 Medusa 用并行多头，EAGLE 用浅层自回归特征草稿；两者都复用目标骨干，属于自投机（self-speculative）。

采样核可以交给 FlashInfer 的 chain / tree speculative sampling，见 `nvidia-flashinfer`。那只负责 $p,q$ 怎么拒绝，不负责头怎么训。

大 batch 已经吃满 GPU：投机的验证步更宽，吞吐可能掉，延迟收益也小。接受率低的任务（代码、随机采样高 $T$）$\gamma$ 或树太深会浪费。质量上还要区分接受规则。typical acceptance 等启发式可能更快，但不再严格保持 $p$；要求无损就用原论文的拒绝采样。IFB 里有的请求在投机、有的在普通 decode，树宽不同，token budget 更碎，见 `nvidia-inflight-batch`。

## 追问

**无损还在吗？**
按 $p$ 做严格拒绝采样才能保留无损保证。直接把头的 greedy 候选当输出，就没有这项保证。Medusa-2 若改了骨干权重，那是另一个模型，不是原 $p$ 的无损加速。
**草稿 KV？**
独立 draft 有自己的 cache。Medusa 头没有逐步 KV。EAGLE 的浅层草稿若逐步跑，要一小段特征侧状态，拒绝时同样截。
**和 GQA / KV FP8？**
可以一起用。投机减少目标前向次数，GQA、KV FP8 减少每次前向读取的字节。
**$\gamma$ 越大越好？**
不会。期望接受长度受 $q$ 与 $p$ 的相似程度影响，草稿更长也可能只是多做被拒绝的工作。测的是产出 token/s 和 TBT，拒绝掉的草稿不要算进吞吐。

## 相关题

- [[google-spec-decode]]：从无损性讲起，Medusa / EAGLE 只占一节，适合先打基础。
- [[meta-multi-token]]：同样是在主干上挂多个未来头，但 Meta 是预训练时就用多步 CE 训练。
- [[sys-spec-sys]]：草稿长度 $\gamma$ 和吞吐测量的系统视角，和本卡末尾的追问一致。
- [[coding-spec-accept]]：验证这一步的接受规则代码，经典投机和 Medusa 共用。
