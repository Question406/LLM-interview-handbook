---
id: sys-admission-control
section: systems
order: 23
level: S
title: 容量不足时，LLM API 该拒绝、排队、降级还是缩短预算？
quick: "先判断请求能否在当前负载下满足 SLO，再决定排队、降级或拒绝。准入按租户、deadline、token 与 KV 预算计量，队列设上限，拒绝带 `Retry-After`；模型、工具和推理预算的降级要事先约定并明确返回。"
tags:
  - Admission Control
  - SLO
  - Reliability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Google SRE Book — Service Level Objectives
    url: https://sre.google/sre-book/service-level-objectives/
    type: primary
  - title: Google SRE Book — Handling Overload
    url: https://sre.google/sre-book/handling-overload/
    type: primary
---

容量不足时，我会先估计请求还能否按时完成，再决定有界排队、按约定降级或拒绝低优先级流量。比如平均 QPS 没变，但内部评测开了最大推理预算，KV 和生成槽位仍可能被占满，聊天用户的首个 token 等待时间（TTFT）就会恶化。LLM 的负载要按输入提示（prompt）长度、输出预算、工具轮次和 KV 驻留计量；SRE overload 的原则同样适用：保护已经承诺的 SLO 和错误预算，避免所有请求一起超时。

请求进 GPU 调度器之前，至少估计：输入 token、声明或历史的输出预算、工具 / 检索次数、deadline、租户等级。再叠上当前队列里已经承诺出去的 token 与 KV。若在现有 `max batched tokens` 和排队时延下无法赶上 deadline，就不要再收。这和 `sys-mixed-traffic-scheduler` 是同一条链的入口：调度管交错，admission 管 要不要接。估计输出时不要信用户随便填的 `max_tokens`：有人开到模型上限却只聊一句，有人开思考模式却把上限留默认。用该类请求的历史分位数做预算，超支就截断或改异步，并在响应里标明发生了降级。

只看并发路数会漏掉 输入预填充（prefill，即处理输入并建立缓存） 的计算峰值。一条长文档请求的 prefill 可能相当于几十条短聊天的 逐 token 生成（decode），见 `sys-prefill-decode`。把「在飞请求数」当容量单位，长尾一来就过载。工具调用把一条用户请求变成多段 generate，admission 若只在入口估一次、不把后续轮次算进预算，会在对话中途爆。Agent 流量要把「最大工具轮次 × 每轮输出上限」当作最坏 token，而不是按第一轮闲聊来准入。

选择过载动作时，要看它对 SLO 和租户公平性的影响：

- 有界排队。 队列必须有深度上限和老化。超时后返回 429 / 503，带 `Retry-After`，让客户端退避。无限等待会把 deadline 全部变成超时，error budget 一次性烧光。
- 降级是产品契约，不是偷偷换模型。 事先写清：更小模型、关闭昂贵工具、缩短 reasoning budget、只出摘要、改异步任务。客户端要能区分「完整回答」和「降级回答」，否则评测和质量投诉无法归因。
- 拒绝低优先级。 付费、交互、批处理不是同一类 SLO。先砍批量、内部重试、可延迟的 agent 循环，保住有 deadline 的对话。
- 缩短预算。 对思考模型和 agent，输出 token 上限本身就是容量旋钮。缩短的是 声明过的预算，不是生成到一半硬截断还不报错。

不要让最会重试的客户端赢。无 jitter 的同步重试会把一次过载放大成重试风暴；admission 层必须把重试当成新的负载来记账。内部评测、定时 agent、CI 里的「失败即重试」尤其危险：它们比真人更会打满。给这类调用单独的配额和并发上限，过载时先砍它们。公开 API 还要区分「用户点了重试」和「SDK 自动重试」，后者必须带退避，前者可以立即排进高优队列。

不同 tenant 用配额、并发上限和加权队列隔离，而不是共享一条 FIFO。一个超量用户把 KV 占满时，其他租户的 P99 不应也大幅恶化。可借用 SRE 的 error budget：交互 SLO 烧得太快就自动收紧 admission，而不是等值班手工限流。配额要用 token 而不是请求数计价，否则短请求用户会被长文档用户挤掉。突发允许一小段借额度，但要有归还，避免「永远 burst」。公平性出问题的典型日志是：总利用率不高，某一租户的 P99 却单独爆炸，那是隔离没做，不是集群不够。

验收时按长度和租户拆开看尾延迟，同时记录拒绝与降级的原因：

- P95 / P99 TTFT 与 TPOT，按长度桶和租户切
- 429、超时、降级率、异步改派率
- 每层队列长度、拒绝原因、KV / token 水位
- 降级后的任务成功率，防止「服务还活着、答案已经不可用」

平均 QPS 低也可能雪崩：超长 prompt、工具扇出、思考预算被默认开到最大，都会让 admission 在「看起来不忙」时失效。容量评审要覆盖最长 prompt、最大工具轮次的压力场景，过载演练也要实际打满 KV，检查 429 和隔离是否生效。

交互高峰叠一批内部评测：评测默认开最大 reasoning budget，每条请求的输出上限比聊天高一个数量级。平均 QPS 没变，KV 和 decode 槽位被评测占满，付费聊天 P99 TTFT 崩掉。正确动作是：评测走独立配额或降级预算，聊天保 deadline；评测超标就 429 而不是和用户挤同一条 FIFO。反过来，只拒绝聊天、放行无界内部流量，是把 error budget 让给了没有 SLO 的客户端。

容量单位要用 token 与 KV 页，不要用「在飞请求数」。两条 8k 文档请求可能比二十条短闲聊更贵。Admission 估错输出长度时会超收，应用历史分位数做预算，并在真实生成超过声明预算时截断或改异步，而不是默默继续占卡。

## 追问

**为什么不一律排队到有空位？**
过了 deadline 的排队只消耗 KV 和调度，不产生有效回答，还会拖死后面本可成功的短请求。LLM 的 KV 驻留让「等一等」比传统无状态 API 更贵：队列里的人不仅占坑，还占显存。
**降级和拒绝哪个更伤 SLO？**
看产品定义。若契约是「必须完整模型」，降级算失败，应拒绝并让客户端改异步。若契约允许摘要，降级能保可用性。无论哪种，都要在响应里显式标记，避免评测把降级当正常质量。
**Retry-After 怎么定？**
跟当前队列消耗时间和 error budget 走，带抖动，避免所有客户端同一秒打回来。内部客户端尤其要尊重该头；不尊重的调用方应被单独限流，而不是让遵守规则的人饿死。
**和 chunked prefill 谁先做？**
先 admission 挡住必然超时的请求，再靠调度把已接流量的长短交错做好。两者缺一都会出现「短聊天 TTFT 爆炸」。Admission 决定集合，调度决定集合内部的顺序。
