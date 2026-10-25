---
id: sys-agent-sched
section: systems
order: 27
level: S
title: 系统：agent 多轮，工具等待时 GPU 空转怎么插 decode
quick: "请求等工具时移出 running batch，把 decode 槽位交给其他请求，历史 KV 按等待时间与 HBM 水位保留或卸到 CPU。工具回来后只对新增观察做 append prefill，再继续生成，并单独限制挂起会话的 KV 占用。"
tags:
  - SGLang
  - vLLM
  - DistServe
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast and Expressive LLM Inference with RadixAttention and SGLang
    url: https://lmsys.org/blog/2024-01-17-sglang/
    type: primary
  - title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving"
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: "Orca: A Distributed Serving System for Transformer-Based Generative Models"
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: Continuous batching from first principles
    url: https://huggingface.co/blog/continuous_batching
    type: secondary
---

工具等待时应挂起这条请求，释放 decode 计算槽，立刻补进其他请求。比如搜索 RPC 要等几秒，而 decode 一步只需毫秒，整批陪等会浪费 GPU；回来后复用历史 KV，只计算工具新增的观察。

Agent 经常先生成几十到一百多个 token 的工具调用，等待搜索 / 代码沙箱 / HTTP，再带观察续写。SGLang 讨论多轮与前缀复用，Orca / vLLM 提供 iteration 边界插拔，DistServe 则说明长 prefill 如何干扰 decode。OpenAI / Anthropic serving 题也会沿这段等待追问，调度骨架见 `sys-cont-batch`，槽位细节见 `sys-decode-batch`。

请求分为 `prefill` / `decode` / `tool_wait`，外加排队，GPU 只处理前两个状态。工具等待实际耗时经常是 $10^3$-$10^4$ 毫秒，一步 decode 是个位数到几十毫秒。若等工具时仍留在 running batch：

- 同步等：整步 batch 陪着空转，SM 利用率塌掉。
- 假装还在生成：语义错，会在 tool 结果回来之前继续往下编。
- 留着槽但不算：等价于静态 batch 的 hole，`sys-cont-batch` 就是为消灭这个洞。

正确动作在 iteration 边界：

1. 解析到 工具调用（或模型自己停在需要外部输入的点），把该序列移出 running，释放计算槽。
2. KV 页：秒级等待且 HBM 紧，卸到 CPU，见 `sys-kv-offload`；HBM 松或等待很短，可留 GPU 并加引用，回来零拷贝。不要把页当结束请求直接丢；丢掉下一轮就要整段 prefill。
3. 立刻从 waiting 里补别人的 decode（或一块 chunked prefill）。有效 $B$ 维持住，decode 瘦 GEMM 继续喂。
4. 工具结果返回：请求变成「短 append prefill」（只算观察 token）再回到 decode。历史 KV 必须还能对上 RoPE 位置。

这和「请求结束腾槽」同构，只是生命周期没完。结束是释放；暂停是挂起。计算 inflight 不包含 `tool_wait`。CUDA graph 的 $B_{\mathrm{graph}}$ 按活跃 decode 计算，挂起请求若仍 pad 进去，会保留无效计算，见 `nvidia-cuda-graph`、`sys-flashinfer`。

SGLang radix 适合复用多轮 Agent 的公共部分：系统提示、工具 字段和类型规范（schema）、上一轮对话在树上，观察回来只 miss 尾巴。扁平「整段 prompt 哈希」在每轮都加一段 tool result 时，部分命中更差。树的插入要把生成段和观察段都挂回去，见 `sys-radix-tree`。

暂停不占算力，但占 KV。一个 agent 二十轮工具，每轮历史更长，挂起会话的 KV 会长期占用 HBM，正在生成的请求却可能没有空间进入。要有：

- **挂起配额：** `tool_wait` 的 KV 水位，超出卸 CPU 或杀最久未用的会话。
- **公平：** 短 decode 的交互请求不要被「很多挂起 agent 的前缀」挤出 GPU 热层。
- **亲和：** 工具回来要打到还握着这份 KV 的 replica，否则 miss 重算，等工具省下的时间吐回去。

PD 分离：工具等待发生在 decode 池。回来的观察是短 prefill，可以走 decode 池的 chunked prefill，或送回 prefill 池再搬 KV。短观察跨池搬运往往不划算，单 decode 池 append 更常见。长「再塞一整份检索文档」则像新 prefill，该走 prefill 池，见 `sys-prefill-decode-disagg`。

Chunked prefill 仍然重要：agent 集群里同时有人开新会话（长 prefill）、有人在短 decode、有人在等工具。长 prefill 不切块，会把所有短 decode 的 TPOT 打出尖刺，agent 体感比普通聊天更糟，因为一轮里 decode 本就短，调度抖动占比更大，见 `sys-chunked-prefill`。

等工具时仍保留计算槽会造成空转；每次从 token 0 重算会丢掉 prefix cache 的计算收益；永久保留挂起 KV，又可能让活跃 decode OOM。这三项都要分别设边界。

监控：`tool_wait` 条数、挂起 KV 字节、工具返回后的 首个 token 的等待时间（TTFT）（应接近短 append）、running $B$、因挂起挤出导致的 GPU miss。Tokens/s 之外还要看这些指标。某条请求等工具时不生成 token，GPU 仍应继续处理其他请求。

## 追问

**KV 留 GPU 还是卸 CPU？**
等待远小于一秒且 HBM 松，留 GPU。秒级工具且槽位紧，卸 CPU，回来 DMA。盘只给超长冷前缀。
**观察回来要不要 PD 走一圈？**
几十到几百 token 通常在 decode 池 append。整篇文档级观察当新 prefill。
**和 continuous batching 是一层吗？**
同一套 iteration 插拔。Agent 多一个 `tool_wait` 队列，结束条件改成外部事件，不再是 eos。
**为什么多轮 Agent 适合用 radix？**
每轮只在尾巴分叉，主干（系统提示 + 工具头 + 历史）共享。见 `sys-radix-tree`。
**挂起算 inflight 吗？**
不算算力 inflight。占 KV 要单独记账，否则 `max_num_seqs` 会被僵尸会话吃光。
**工具很慢时公平怎么做？**
限制每会话挂起 TTL 和 KV 占比；超时驱逐并记 `tool_timeout`，不要让 GPU 热层被冷会话占满。
