---
id: ant-vllm-paged
section: systems
order: 161
level: A
title: 蚂蚁：vLLM 如何做推理加速？PagedAttention 解决什么？
quick: "自回归逐 token 生成（decode）每步都需要历史 $K/V$。vLLM 用 PagedAttention 把 KV 按页管，减少预留空间造成的浪费，再做连续 batch 把不同长度请求塞满 GPU。加速来自显存利用和吞吐，不是改注意力公式。"
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

常见误区是：「用了 FlashAttention」或「改了注意力公式」。加速来自 KV 显存怎么管、请求怎么连续 batch，softmax 没换成近似。FlashAttention 解决单步算子 I/O，PagedAttention 解决 cache 预留碎片，两层别混。相关卡：`sys-pagedattention`、`sys-cont-batch`、`ant-flash-attention`。被问「加速」时先说吞吐（同显存更高并发），再补一句单请求延迟不一定下降。

## KV cache 为什么会先爆

自回归逐 token 生成（decode）每步都要历史 $K/V$。连续预留 `max_len` 会在每条请求内部留下大块空洞，并发一高，显存先被碎片吃完，吞吐上不去。KV cache 避免重算前缀是必要的，但「按最大长度连续占住」把并发度卡死。这是调度 / 分配问题，不是算子算术问题。面试可以用「预留 2048 但平均只生成 80 token」说明碎片从哪来。

## PagedAttention：逻辑连续、物理分页

把 cache 切成固定页，逻辑序列映射到非连续物理块，分配按需增长，结束就回收，类似 OS 虚拟内存。页表查找有开销，但碎片下降通常更值：同样显存能塞更多并发请求。前缀共享、beam / parallel sampling 也能共享页。vLLM 再叠加连续 batching：某个请求结束立刻插入新请求，减少 decode 空泡。还可配合量化 KV、CUDA graph。DeepSpeed 主训练分片，不要和 vLLM 推理调度混职责。block size 是实现旋钮：过小页表密，过大又接近连续预留，说清权衡即可。

## 加速从哪来、边界在哪

收益来自更高有效 batch 和更少浪费显存，从而 tokens/s 上升；单请求延迟不一定成比例下降。页过小则页表开销大，过大则碎片回升。和训练 ZeRO 不是一回事：ZeRO 切参数，paging 切 KV。输入预填充（prefill）仍可能是大块连续写，decode 才真正吃到分页与连续 batch 的好处；混合流量要分开看 首个 token 的等待时间（TTFT） 和 TPOT。记住：KV 按页，少碎片，连续 batch 喂满 GPU。

## 追问

- **和 FlashAttention 什么关系？** FA 是算子内核；paging 是 KV 布局与调度。vLLM 里两者常一起用。
- **为什么不预分配 max_len？** 并发下空洞太多，先 OOM 再谈吞吐。平均长度远小于上限时，分页几乎总是值得做。
- **页表会不会拖慢 decode？** 有开销，但通常小于碎片导致的并发损失。
- **前缀缓存注意什么？** 共享页要按输入提示指纹隔离租户与权限，见 `sys-prefix-cache-isolation`。多租户下错共享前缀比碎片更危险。
