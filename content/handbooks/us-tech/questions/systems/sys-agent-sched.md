---
id: sys-agent-sched
section: systems
order: 27
level: S
title: 系统：agent 多轮，工具等待时 GPU 空转怎么插 decode
quick: "工具 RPC 是秒级，逐 token 生成（decode） 步是毫秒级。等工具时把这条请求从 running batch 摘掉，槽位和算力让给别人的 decode；KV 可留 HBM 或卸 CPU。工具返回后只对新观察做 prefill，不要重算整段历史。"
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

## 题怎么来的

Agent 流量不是「一条长 completion」。模型吐几十到一百多个 token 的工具调用，停住，等搜索 / 代码沙箱 / HTTP，再带着观察续写。SGLang 的公开卖点就是多轮和前缀复用；Orca / vLLM 的 continuous batching 给了 iteration 边界插拔；DistServe 说明别用长 输入预填充（prefill，即处理输入并建立缓存） 堵住 逐 token 生成（decode）。OpenAI / Anthropic serving 岗会问：等工具那几秒 GPU 在干什么。调度骨架见 `sys-cont-batch`，槽位细节见 `sys-decode-batch`。本题只谈 `tool_wait` 这个状态。

## 三个状态，不要占着 decode 槽

我会先把请求拆成 `prefill` / `decode` / `tool_wait`（外加排队）。GPU 只该跑前两个。工具等待实际耗时经常是 $10^3$-$10^4$ 毫秒，一步 decode 是个位数到几十毫秒。若等工具时仍留在 running batch：

- 同步等：整步 batch 陪着空转，SM 利用率塌掉。
- 假装还在生成：语义错，会在 tool 结果回来之前继续往下编。
- 留着槽但不算：等价于静态 batch 的 hole，`sys-cont-batch` 就是为消灭这个洞。

正确动作在 iteration 边界：

1. 解析到 工具调用（或模型自己停在需要外部输入的点），把该序列移出 running，释放计算槽。
2. KV 页：秒级等待且 HBM 紧，卸到 CPU，见 `sys-kv-offload`；HBM 松或等待很短，可留 GPU 并加引用，回来零拷贝。不要把页当结束请求直接丢；丢掉下一轮就要整段 prefill。
3. 立刻从 waiting 里补别人的 decode（或一块 chunked prefill）。有效 $B$ 维持住，decode 瘦 GEMM 继续喂。
4. 工具结果返回：请求变成「短 append prefill」（只算观察 token）再回到 decode。历史 KV 必须还能对上 RoPE 位置。

这和「请求结束腾槽」同构，只是生命周期没完。结束是释放；暂停是挂起。Inflight 计数不应包含 `tool_wait`。CUDA graph 捕获的 $B_{\mathrm{graph}}$ 按在飞 decode 来，等工具的人 pad 进去是在买空气，见 `nvidia-cuda-graph`、`sys-flashinfer`。

SGLang 的 radix 对 agent 特别值：系统提示、工具 字段和类型规范（schema）、上一轮对话在树上，观察回来只 miss 尾巴。扁平「整段 prompt 哈希」在每轮都加一段 tool result 时，部分命中更差。树的插入要把生成段和观察段都挂回去，见 `sys-radix-tree`。

## 水位、公平、和 PD

暂停不占算力，但占 KV。一个 agent 二十轮工具，每轮历史更长，挂起会话的 KV 会长期占用 HBM，真正在生成的请求 反而进不来。要有：

- **挂起配额：** `tool_wait` 的 KV 水位，超出卸 CPU 或杀最久未用的会话。
- **公平：** 短 decode 的交互请求不要被「很多挂起 agent 的前缀」挤出 GPU 热层。
- **亲和：** 工具回来要打到还握着这份 KV 的 replica，否则 miss 重算，等工具省下的时间吐回去。

PD 分离：工具等待发生在 decode 池。回来的观察是短 prefill，可以走 decode 池的 chunked prefill，或送回 prefill 池再搬 KV。短观察跨池搬运往往不划算，单 decode 池 append 更常见。长「再塞一整份检索文档」则像新 prefill，该走 prefill 池，见 `sys-prefill-decode-disagg`。

Chunked prefill 仍然重要：agent 集群里同时有人开新会话（长 prefill）、有人在短 decode、有人在等工具。长 prefill 不切块，会把所有短 decode 的 TPOT 打出尖刺，agent 体感比普通聊天更糟，因为一轮里 decode 本就短，调度抖动占比更大，见 `sys-chunked-prefill`。

错误说法：等工具时把请求留在 batch 里「占着图」；每次工具返回都当新请求从 token 0 prefill；为了命中率永不淘汰挂起 KV。前一个空转 GPU，中间一个把 radix / prefix cache 的意义归零，后一个把在飞 decode OOM。

监控：`tool_wait` 条数、挂起 KV 字节、工具返回后的 首个 token 的等待时间（TTFT）（应接近短 append）、running $B$、因挂起挤出导致的 GPU miss。不要只报 tokens/s。等工具期间 token 是 0，但 GPU 不该是 0。

## 追问

- **KV 留 GPU 还是卸 CPU？** 等待远小于一秒且 HBM 松，留 GPU。秒级工具且槽位紧，卸 CPU，回来 DMA。盘只给超长冷前缀。
- **观察回来要不要 PD 走一圈？** 几十到几百 token 通常在 decode 池 append。整篇文档级观察当新 prefill。
- **和 continuous batching 是一层吗？** 同一套 iteration 插拔。Agent 多一个 `tool_wait` 队列，结束条件改成外部事件，不再是 eos。
- **为什么 radix 对 agent 更香？** 每轮只在尾巴分叉，主干（系统提示 + 工具头 + 历史）共享。见 `sys-radix-tree`。
- **挂起算 inflight 吗？** 不算算力 inflight。占 KV 要单独记账，否则 `max_num_seqs` 会被僵尸会话吃光。
- **工具很慢时公平怎么做？** 限制每会话挂起 TTL 和 KV 占比；超时驱逐并记 `tool_timeout`，不要让 GPU 热层被冷会话占满。
