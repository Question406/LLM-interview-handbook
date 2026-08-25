---
id: nvidia-spec-medusa
section: nvidia
order: 25
level: A
title: NVIDIA：Medusa / EAGLE 多头草稿，和经典投机解码差在哪
quick: >-
  经典投机是另一份小模型自回归写 $\gamma$ 个 token，大模型一次验证，拒绝采样保证无损。Medusa 在同一套骨干上加
  $K$ 个独立头，一次前向出一棵候选树。EAGLE 在特征层自回归草稿，用移位 token 补不确定性。验证核仍是一次
  target forward；变的是草稿从哪来、KV 怎么回滚。
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

## 题怎么来的

TensorRT-LLM 文档把草稿来源写成两类：独立 draft 模型，以及 Medusa 头。EAGLE 后来也进了各家 serving 栈。NVIDIA 岗要听「无损验证没变，变的是草稿生成器和树」。算法不变量和 Google 那道同构，见 `google-spec-decode`；本题收工程差：多头、特征草稿、KV 回滚、和 IFB 怎么叠。

## 经典投机：两套权重，一条链

Leviathan / Chen：草稿模型 $q$ 自回归写出 $x_1,\ldots,x_\gamma$，目标 $p$ 一次前向得到这 $\gamma$ 个位置的 logits。位置 $i$ 抽 $u\sim U[0,1]$，若 $u \lt p(x_i)/q(x_i)$ 则接受，否则从修正分布再抽一个并截断后面。期望接受长度决定加速比，不是草稿 FLOPs。GPU 小 batch 时 decode 吃不满，一次验证摊掉 $\gamma$ 步的权重读取，这才是投机的 roofline，见 `nvidia-flash-decode`。

代价：再驻留一个模型，两套 KV，两套调度。草稿太强则自身也慢；太弱则 $\gamma$ 全拒，验证白做。拒绝后 **target 和 draft 的 KV 都要截回接受前缀**，否则注意力盯幽灵 token。Paged 上就是把多出来的页 refcount 减掉，见 `nvidia-paged-kv`。

## Medusa：同一隐状态上的独立头

Medusa（Cai et al.）不另训小 Transformer。骨干最后一层隐状态 $h_t$ 上挂 $K$ 个头：头 $k$ 直接预测 $t+k$ 的 token，头与头之间 **不互为条件**。一次骨干前向得到 $K$ 个候选位置，再靠 top-$s$ 叉出一棵树，用树状注意力一次验证多条路径。接受的是树上的一条前缀。

和经典的差：

- 草稿 FLOPs 极小（几个线性层），没有第二份 KV。
- 草稿质量通常更差，因为第 $k$ 个头看不到自己前面的草稿 token，误差不复合在自回归里，但也不享受自回归纠错。
- Medusa-1：冻骨干只训头，接近无损加速。Medusa-2：骨干和头一起训，接受率更高，有把原模型打歪的风险。
- TRT-LLM 要在配置里写 `medusa_choices`（树的叉法），IFB 路径必须显式给这棵静态树。早期文档只官宣 Vicuna 一类，别的骨架要自己接同样的头。

树验证一步的 $Q$ 长度是候选节点数，不是 1，attention 更像短 prefill，占位和 CUDA Graph 档位都要按树大小留，见 `nvidia-cuda-graph`。

## EAGLE：特征层自回归

EAGLE 观察：在倒数第二层特征上做自回归，比在 token 上更容易；但特征有不确定性，需要把 **已经采样的 token 前移一位** 拼进草稿模块，消掉「当前特征还不知道自己变成了哪个 token」。草稿模块很小：一层 decoder + 投影，embedding 和 LM head 借用目标模型。

于是草稿是短自回归，但每步是特征而不是再跑 $L$ 层。接受率通常高于独立 Medusa 头，仍走同一套拒绝采样 / 树验证。EAGLE-2 按置信度动态长树；EAGLE-3 改成更靠多层特征、token 侧预测。面试抓一句就够：**Medusa 是并行多头；EAGLE 是浅层自回归特征草稿**。两者都是自投机（self-speculative），不是第二份独立 LLM。

采样核可以交给 FlashInfer 的 chain / tree speculative sampling，见 `nvidia-flashinfer`。那只负责 $p,q$ 怎么拒绝，不负责头怎么训。

## 什么时候不要上

大 batch 已经吃满 GPU：投机的验证步更宽，吞吐可能掉，延迟收益也小。接受率低的任务（代码、随机采样高 $T$）$\gamma$ 或树太深会浪费。质量：typical acceptance 一类启发式能提速，但不再严格保持 $p$；需要无损就回到原论文的拒绝采样。IFB 里有的请求在投机、有的在普通 decode，树宽不同，token budget 更碎，见 `nvidia-inflight-batch`。

## 追问

- **无损还在吗？** 验证仍按 $p$ 做拒绝采样就在。改成「头的 greedy 直接当输出」就不在。Medusa-2 若改了骨干权重，那是另一个模型，不是原 $p$ 的无损加速。
- **草稿 KV？** 独立 draft 有自己的 cache。Medusa 头没有逐步 KV。EAGLE 的浅层草稿若逐步跑，要一小段特征侧状态，拒绝时同样截。
- **和 GQA / KV FP8？** 正交。投机减的是前向次数；量化减的是每次前向的字节。
- **$\gamma$ 越大越好？** 不是。期望接受大约随 $q$ 与 $p$ 的靠近程度掉。测的是产出 token/s 和 TBT，拒绝掉的草稿不要算进吞吐。
