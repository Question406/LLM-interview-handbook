---
id: ant-vllm-paged
section: systems
order: 161
level: A
title: 蚂蚁：vLLM 如何做推理加速？PagedAttention 解决什么？
quick: "自回归逐 token 生成（decode）每一步都要读历史 $K/V$。vLLM 用 PagedAttention 把 KV 按页管理，减少按最大长度预留造成的浪费，再用连续 batch 把不同长度的请求塞满 GPU。加速来自显存利用率和吞吐，注意力公式没改。"
tags:
  - Ant Group
  - vLLM
  - PagedAttention
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
  - title: 蚂蚁大模型面经
    url: https://www.nowcoder.com/feed/main/detail/2b27dfe1f1ab4efa87eb0aea70ffdc20
    type: candidate-first-hand
  - title: vLLM
    url: https://arxiv.org/abs/2309.06180
    type: primary-paper
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：一面 / 二面均出现 vLLM
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“vLLM框架是怎么做推理加速的？”**；**“vLLM 中使用的技术是否熟悉（如 Paged Attention、KV Cache）?”**

vLLM 的加速主要来自两件事：用 PagedAttention 按页管理 KV cache，减少显存碎片，同样显存能放下更多并发请求；再用连续 batching 让结束的请求立刻让位给新请求，把 GPU 塞满。softmax 没换成近似，提升的是吞吐，单个请求的延迟不一定下降。回答「用了 FlashAttention」或「改了注意力公式」都答偏了：FlashAttention 管单步算子的 I/O，PagedAttention 管 cache 预留的碎片，是两层东西。

先说 KV cache 为什么会先爆。decode 每步都要用历史的 $K/V$，缓存起来避免重算前缀是必要的。问题出在分配方式：给每条请求连续预留 `max_len`，比如预留 2048、平均却只生成 80 token，每条请求内部都留着一大块空洞。并发一高，显存先被这些空洞吃完，吞吐就上不去了。这是调度和分配的问题，算子的算术没毛病。

PagedAttention 的思路和操作系统的虚拟内存一样：把 cache 切成固定大小的页，逻辑上连续的序列映射到物理上不连续的块，按需增长，请求结束就回收。查页表有开销，但碎片少了通常更划算，同样的显存能塞更多并发请求。前缀共享、beam 和 parallel sampling 也能共享页。block size 是实现上的旋钮：页太小页表密、开销大，页太大又回到接近连续预留、碎片回升，讲清楚这个权衡就行。vLLM 在这上面再叠连续 batching，还可以配合量化 KV、CUDA graph。

加速的边界也要说清。收益来自更高的有效 batch 和更少浪费的显存，所以 tokens/s 上去了，单个请求的延迟不会按比例下降。输入预填充（prefill）还是大块的连续写，decode 才真正吃到分页和连续 batch 的好处，所以混合流量要把首个 token 的等待时间（TTFT）和 TPOT 分开看。另外别和训练侧混：DeepSpeed 的 ZeRO 切的是参数，主要服务训练分片；paging 切的是 KV，服务推理调度。

## 追问

**和 FlashAttention 是什么关系？**
FA 是算子内核，paging 是 KV 的布局和调度。vLLM 里两个经常一起用。

**为什么不直接预分配 max_len？**
并发下空洞太多，会先 OOM，吞吐根本上不去。平均长度远小于上限时，分页几乎总是值得做。

**页表会不会拖慢 decode？**
有开销，但通常比碎片造成的并发损失小。

**前缀缓存要小心什么？**
共享页要按输入提示指纹隔离租户和权限，见 `sys-prefix-cache-isolation`。多租户下前缀共享错了，比碎片更危险。

相关：`sys-pagedattention`、`sys-cont-batch`、`ant-flash-attention`
