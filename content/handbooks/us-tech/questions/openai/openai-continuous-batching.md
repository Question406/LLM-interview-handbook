---
id: openai-continuous-batching
section: openai
order: 12
level: A
title: OpenAI：continuous batching / iteration-level 调度解决什么
quick: "连续批处理按一次 decoder iteration 调度：完成的请求释放 KV，等待请求补进来，活跃请求各生成一个 token。这样短请求结束后槽位能继续工作；KV 分页和 chunked prefill 则分别解决内存预留、长输入拖慢单步的问题。"
tags:
  - OpenAI
  - Continuous Batching
  - Serving
  - KV Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Orca — A Distributed Serving System for Transformer-Based Generative Models
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

continuous batching 把调度单位缩小到一次 decoder iteration，让完成的请求退出、新请求补进来。比如三条请求还要 8、40、200 步，静态批次会让空出的槽一直等最长请求；连续批处理在第 8 步和第 40 步就能补入下一条，让 GPU 继续处理活跃 token。

请求级 batch 先凑满 $B$ 条、pad 到最大长度，再一起 decode 到最慢请求 EOS。长度 20 和 200 放一起会浪费 padding，短请求还会等待收批或长请求结束。KV 若按 `max_new_tokens` 预留连续空间，实际可能只用 10%，余量却占住显存。裸 tokens/s 看着还行，满足时延 SLO 的完成数 goodput 可能很差；训练的固定 $T$ 不存在同样的在线到达问题。

Orca 用 iteration-level 调度，每步先释放已结束请求的 KV，再在空位 prefill 新请求，活跃序列各生成 1 个 token。batch 成员每步可变，GPU 不再为结束槽继续做 GEMM。每个请求独立保存 `position`、采样 RNG、停止条件和 KV page 表，batch 维的第 $i$ 个位置代表当前 slot，没有统一的全局 `T`。

只改调度还不够。连续 `cat` 的 KV 仍迫使系统按上限预留，vLLM 的 PagedAttention 把 KV 切成固定 page，逻辑连续、物理可分散；新增 token 时申请页，请求结束归还，投机解码拒绝也可通过还页 rollback。attention kernel 要支持 ragged 长度或 page 间接寻址，写死 `[B, H, T_max, D]` 再 pad 会损失调度收益。

新请求的完整 prefill 若塞进一个 iteration，又会拖慢这一轮 decode。可以用 chunked prefill，每轮只处理部分 prompt，把剩余预算留给 decode；分离 prefill、decode 池则需要另做架构权衡。解释时画静态 batch 的空槽和连续批的活 token 时间线，就能把这两种瓶颈区分清楚。

这张卡依据 Orca、vLLM 等公开系统讨论推理调度，不指向一份已确认的 OpenAI onsite 原题。

## 追问

**和 dynamic batching 有什么差别？**
很多 dynamic batching 只在开始前凑请求，continuous batching 在运行过程中仍更换成员。

**长请求会不会一直占资源？**
会占着 KV，需要 max tokens、优先级或抢占；抢占后 KV 要 offload 或丢弃。

**batch 越大越好吗？**
decode 在带宽饱和前常受益，再大可能恶化 TTFT 和排队。按 SLO 调，不能只追 MFU。

**训练也要这样调吗？**
通常没必要，训练可把样本切齐，也没有在线到达过程。

相关：`openai-prefill-decode`、`openai-speculative-decoding`、[[meta-vllm]]（连续批与 PagedAttention）、[[google-tpu-decode]]（静态 shape 与重编译）、[[sys-paged-attn]]（块表）、[[nvidia-kv-offload]]（抢占与量化的取舍）
