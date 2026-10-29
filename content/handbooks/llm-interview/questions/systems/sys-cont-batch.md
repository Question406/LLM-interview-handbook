---
id: sys-cont-batch
section: systems
order: 9
level: A
title: Continuous Batching 为什么提升 throughput？
quick: >-
  Continuous batching 每生成一轮 token 就更新请求集合，短请求结束后马上补入新请求，GPU 少等长请求，所以 throughput
  更高。静态 batch 即使调大，短请求的槽位也要等最长那条结束。实际还要用分页 KV 管内存，并约束 TPOT，避免 throughput
  提高后单个请求反而变慢。
tags:
  - Serving
  - Scheduling
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: 'Orca: A Distributed Serving System for Transformer-Based Generative Models'
    url: 'https://www.usenix.org/conference/osdi22/presentation/yu'
    type: primary
  - title: vLLM PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
---

## 可以这样回答

Continuous batching 每轮生成一个 token 后就更新请求集合，短请求结束便能补入新请求，因此减少 GPU 空等。比如聊天已经 EOS，另一条长 chain of thought 还在生成，静态 batch 的聊天槽位仍被占住；Orca 的 iteration-level scheduling 则会让这个槽位马上接下一条。单纯调大 `max_num_seqs` 只是提供更多候选，收益要靠逐轮补位才能实现。

静态生成时，$B$ 条请求的长度 $T_1,\ldots,T_B$ 可能差一个数量级。实现通常 pad 到 $\max T_i$，先结束的行还占着 KV 和计算槽。虽然矩阵乘法的形状仍是 $[B,d]\times[d,d]$，部分行却只是在做被 mask 的无效计算，有效 token/s 被最长尾部拖住。聊天可能几十字，CoT可能几千字，这种差异比分类负载明显；RL 同一 prompt 的 $n$ 条 rollout 也一样。

## 技术备查

Continuous batching 每轮生成一个 token 后就更新请求集合，短请求结束便能补入新请求，因此减少 GPU 空等。比如聊天已经 EOS，另一条长 chain of thought 还在生成，静态 batch 的聊天槽位仍被占住；Orca 的 iteration-level scheduling 则会让这个槽位马上接下一条。单纯调大 `max_num_seqs` 只是提供更多候选，收益要靠逐轮补位才能实现。

静态生成时，$B$ 条请求的长度 $T_1,\ldots,T_B$ 可能差一个数量级。实现通常 pad 到 $\max T_i$，先结束的行还占着 KV 和计算槽。虽然矩阵乘法的形状仍是 $[B,d]\times[d,d]$，部分行却只是在做被 mask 的无效计算，有效 token/s 被最长尾部拖住。聊天可能几十字，chain of thought（CoT）可能几千字，这种差异比分类负载明显；RL 同一 prompt 的 $n$ 条 rollout 也一样。

## 每轮怎样补位

调度器先移走本轮 EOS 的序列，释放 KV 页；容量和槽位允许时，从 waiting 队列补入请求，先做输入 prefill，再给仍在生成的序列做一步 decode。这样有效 $B$ 能维持在较高水平，小矩阵乘法里有更多真正工作的行，已结束请求也不再占用 HBM。短回复释放的页可以交给下一题，这是静态训练图 `generate` 难以做到的。

PagedAttention 让 KV 页释放后可以立即复用。若按最大长度连续预留，请求虽然在调度上能补进来，显存却可能很快 OOM；分页把逻辑序列与物理块分开，也减少了碎片。块大小仍会影响利用率，释放页与后来请求的需求不匹配时，仍可能有空间却不能及时利用。实际要一起选择 block 大小、抢占和公平性策略。

新请求的 prefill 是 compute-bound，可能打断 decode 的带宽流水。比如一条 8k prompt 一次算完，会让其他对话的 TPOT 升高。Chunked prefill 把 prompt 分块，在块间插入 decode；PD 分离则让 prefill 和 decode 去不同池，用跨池空间隔离减少干扰。连续 batching 管单池的时间复用，两者可以组合。

## throughput 还受什么约束

有效 batch 变大能提高 decode 算术强度，但 KV 容量和延迟 SLO 都有上限。`max_num_seqs` 开到显存边缘，P99 TPOT 可能先恶化，瞬时 tokens/s 上升，goodput 却下降。调度器应关注在 SLO 内完成的有效 throughput，指标见 `sys-serving-metrics`。

公平性也需要额外规则。一直补短请求会让长请求饥饿，可以用 aging、max waiting，或把长请求的 KV 暂时放到 CPU。抢占会增加调度复杂度并牺牲部分 throughput，换来更可控的尾延迟；页分配、碎片和 KV 容量要一起看。

## 追问

**和动态 padding 有什么区别？**
动态 padding 仍等整批结束才换请求；连续 batching 在每个 decode token boundaries 移走 EOS、补入 waiting，请求级等待变成逐轮调度。

**PagedAttention 和连续 batching 必须一起用吗？**
它们解决不同问题。分页负责按页分配、共享和回收 KV，连续调度负责每轮换请求；只有分页，短请求仍可能空等，只有连续调度而依旧按最大长度预留，并发又容易受显存限制。

**RL rollout 为什么收益明显？**
同一 prompt 的 $n$ 条回复长短差异很大，静态 batch 常等最长 CoT。短而齐的 SFT 式生成则看不出那么大差距，相关见 `sys-rl-why-vllm-rollout`。

**这算异步 RL 吗？**
不算。这里是引擎内部交错请求，没有引入 policy version 差；异步 RL 是 trainer 与 rollout 引擎之间的流水线，会产生 policy staleness，见 `slime-async-train`。

**PD 分离能替代 chunked prefill 吗？**
它们都是在减轻 prefill 对 decode 的打断，但资源组织不同：chunked prefill 在同池切块，PD 用两个池。是否拆池还要结合负载与资源配置决定。
