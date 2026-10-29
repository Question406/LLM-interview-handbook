---
id: meta-llama-moe
section: meta
order: 21
level: S
title: Meta：Llama 4 / MoE 服务侧（公开信息）——专家并行和 batch
quick: >-
  Llama 4 每个 token 经过 shared expert 和一个 Top-1 routed expert，采用 dropless
  路由。稀疏计算减少每 token 的 FLOPs，但服务仍要容纳全部专家权重；decode batch 太小时，每专家 token 太少，EP 的
  all-to-all 反而可能比 GEMM 更慢。
tags:
  - Meta
  - Llama
  - MoE
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: The Llama 4 herd — natively multimodal AI
    url: 'https://ai.meta.com/blog/llama-4-multimodal-intelligence/'
    type: primary
  - title: MetaShuffling — Accelerating Llama 4 MoE Inference
    url: 'https://pytorch.org/blog/metashuffling-accelerating-llama-4-moe-inference/'
    type: primary
  - title: Switch Transformers
    url: 'https://arxiv.org/abs/2101.03961'
    type: secondary
  - title: Mixtral of Experts
    url: 'https://arxiv.org/abs/2401.04088'
    type: secondary
---

Llama 4 服务要同时算专家权重占用和每专家拿到的 token 数。稀疏路由省了每 token 的计算，但小 batch 下可能省不回 all-to-all 的延迟。Llama 4 是 Meta 第一条公开 MoE 产品线，下面的架构信息来自博客和 PyTorch MetaShuffling 文，材料没有给出内部 EP 度数、all-to-all GB/s 或 MFU。

## 公开架构对服务意味着什么

博客和 MetaShuffling 公开了以下架构信息：

- **Scout：** $17\mathrm{B}$ 激活，$16$ 个 routed expert，总量约 $109\mathrm{B}$。
- **Maverick：** $17\mathrm{B}$ 激活，$128$ 个 routed expert，总量 $400\mathrm{B}$。单机 H100 DGX 能放下（博客介绍），也可以分布式。
- **层：** 交替 dense 和 MoE，推理效率用的。
- **路由：** token-choice、Top-1、**dropless**。每个 token 进 **shared expert + 一个 routed expert**。
- **FFN：** 两边都是 SwiGLU，三路线性。

Behemoth 博客写了 $288\mathrm{B}$ 激活、$16$ expert、近 $2\mathrm{T}$ 总量，当时作教师、未发权。因此这里只把它作为 distillation 教师来源，不推断服务拓扑。

与 dense Llama 3 相比，显存按总参数量计算，每 token 的 FLOPs 则按激活参数量计算。 $400\mathrm{B}$ 权都要在内存里（或 NVLink 域里），只是每 token 只乘一小撮。专家卸载可以再省显存，但要另算加载延迟。

## 路由、通信和 batch 怎么配合

单卡：所有专家在一张 GPU 上，router 选出 expert id，按 id **把 token 排在一起**再 GroupedGEMM。MetaShuffling 避免 pad 到每专家最大长度，也避免按专家拆成多次动态 shape 的 GEMM，后者会影响 CUDA Graph。shuffle 之后激活仍是静态稠密张量，metadata 留在 device 上，避免 D2H 同步。

多卡 EP：每张卡只驻留一部分 routed expert。一步 MoE 是：

1. 各卡本地算 router；
2. all-to-all：token 送到拥有该 expert 的卡；
3. 本地 GroupedGEMM（再加 shared expert，shared 常复制）；
4. all-to-all 把输出送回。

通信量跟「被路由走的 token $\times$ hidden」走，不是跟总参数走。Decode 时 $S_q=1$，每请求每层只有一个 token；**全局 batch 太小，每个专家分到的 token 数接近 $0/1$**，GroupedGEMM 退化成一堆瘦矩阵，EP 的 all-to-all 延迟会大于 GEMM。这时更常见的是：逐 token 生成（decode） 少切 EP、多复制专家，或先把很多请求拼成大 batch 再 EP。Prefill 有长序列，token 多，EP 才容易打满。

负载：Top-1 dropless 仍会热点。某个 expert 过热，那张卡 GEMM 变长，all-to-all 等它。服务时要看路由直方图和容量，必要时考虑复制热点 expert。训练中的 aux loss 不应直接当成推理配置，公开材料没有写 Llama 4 推理必须开启它。

Attention 仍是 dense + GQA，KV cache 按请求驻留，通常 DP；只把 MoE FFN 做 EP。这是现在大 MoE 服务的默认拼法，和 DeepSeek / Mixtral 叙事同类，不必编 Meta 内部 mesh。

配置时可以先检查几个具体问题。若按 dense 70B 的 TP 方式切 Maverick，每个 expert 都切一份，每张卡都存 $128$ 个切片。显存省不下来，token 还要在 TP 组里 all-reduce。MoE 该切的是专家维。

例如 decode batch=$1$ 却开 EP=$128$，几乎每步都在 all-to-all 搬单个向量。先估每专家 token 数 $\approx B_{\mathrm{global}}/E$，小于几十就该减 EP。

若 pad 到 `[E, T_max, D]` 再做 BMM，$E=128$ 时 padding 能把有效算力打到个位数。Shuffling + GroupedGEMM 就是为了这个。

相关：`sys-expert-parallel`。

## 追问

**Shared expert 算不算激活？**
算。每 token 的 FFN 算力是 shared + 一个 routed，不是「只有 1/128」。激活 $17\mathrm{B}$ 已经含这一份。
**Dropless 服务会 OOM 吗？**
某个 expert 突然接到很多 token，那张卡激活会鼓。要有每专家上限或动态缓冲，不能假设均匀。公开文没给上限数字，现场说「要监控，不要假设均匀」即可。
**和 Llama 3 dense 比延迟？**
同激活量 GEMM 更小，但多了 router 和两次 all-to-all。小 batch decode 不一定更快。要用 prefill/decode 分开的曲线，不要用训练 MFU 代替服务 P99。
**量化放哪？**
权大量在专家矩阵上，专家权量化对显存最划算；KV 仍跟 GQA 走。别把两笔账混成「MoE 所以 KV 也小」。

## 相关题

- [[google-gemini-moe]]：Google 版的 MoE 服务题，按容量丢 token，和 Llama 4 的 dropless 是两种取舍。
- [[sys-expert-parallel]]：本题服务一节里 EP 和 all-to-all 的通用系统讲法，不绑定某个模型。
- [[xai-grok-moe]]：同样是「公开架构 + decode 时 EP 变延迟墙」的问法，模型换成 Grok-1 的 8 专家 top-2。
- [[xai-moe-decode]]：只看 decode 一步，专家拿到的小 GEMM 长度不齐、连续 batch 让碎片更严重。
