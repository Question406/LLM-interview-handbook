---
id: sys-serving-metrics
section: systems
order: 14
level: A
title: TTFT、TPOT、Throughput、Goodput 分别是什么？
quick: >-
  TTFT 是请求到第一个 token 的时间；TPOT 是后续 token 间平均时间；Throughput 是单位时间总
  tokens/requests；Goodput 是满足 latency SLO 的有效吞吐。产品比较看 goodput 和 P99，不要只报
  tokens/s。
tags:
  - Serving
  - Metrics
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DistServe
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: vLLM production metrics
    url: https://docs.vllm.ai/en/stable/usage/metrics/
    type: primary
---

这块容易只报 tokens/s。产品比较的是 **给定 TTFT / TPOT SLO 下还有多少有效吞吐**。把 batch 开到最大，throughput 很好看，尾延迟已经打穿 SLA，这个数叫空转的繁忙。四个词要能画到同一条请求的时间轴上，而不是背定义。到达 → 排队 → prefill（首 token）→ decode 循环（后续 token）。TTFT 覆盖前三段，TPOT 覆盖最后一段的平均，throughput 数所有段加起来的 token，goodput 只数 SLO 内的请求。内部优化用 tokens/s 看引擎有没有喂饱，对外 SLA 用 goodput。回答「系统好不好」时我先报 goodput 和 P99，再报峰值吞吐。没有 SLO 就没有 goodput，只剩一个没有约束的繁忙程度。

## TTFT 和 TPOT

**TTFT**（time to first token）：请求到达服务，到第一个输出 token 离开。它叠了排队 + 取权重 / 调度 + **prefill**。长 prompt、chunked prefill 切得不好、队列里塞满 decode，TTFT 都会涨。vLLM 里常见直方图 `vllm:time_to_first_token_seconds`，口径要从 `arrival_time` 算起，含前端 tokenize，不只是 kernel 时间。

**TPOT**（time per output token）：第一个 token 之后，后续 token 的平均间隔，有时和 ITL（inter-token latency）混用。它主要受 decode：有效 batch、KV / 权重带宽、是否被一条大 prefill 打断。vLLM 用 `vllm:inter_token_latency_seconds`。输出只有 1 个 token 时 TPOT 无定义，benchmark 里常记 0，算 goodput 时要约定。

同一 GPU 上混跑时，一条长 prefill 会饿死正在进行的 decode，TPOT 出现尖刺。不是 decode 突然变慢，是调度把带宽流水拆碎了，见 `sys-prefill-decode`。排队还会让 TTFT 的方差远大于 kernel 方差：P50 很好看、P99 已经被队列打穿。报 TTFT 必须带百分位，并声明是否含 tokenize / 是否从 `arrival_time` 起算。ITL 是相邻 token 的间隔序列，TPOT 常是对间隔取平均；尾部一个慢 token 会拉高平均，但直方图才能看见尖刺。流式对用户的体感更接近 ITL，而不是「整段生成时间 / 长度」。

## Throughput 不是 Goodput

**Throughput**：单位时间总 tokens 或总 requests。可以靠 continuous batching、更大并发堆上去，见 `sys-cont-batch`。它不看单请求是否超时。

**Goodput**：满足 latency SLO 的有效吞吐。例如「TTFT $\lt$ 200ms 且 TPOT $\lt$ 50ms 的请求」每秒完成多少。SLO 外的 token 对用户是失败，不应进这个分子。DistServe 把 goodput 当作 PD 分离的优化目标，正是因为混部时 TTFT 和 TPOT 互相伤害：堆 prefill 救了吞吐、打穿了 TPOT，或反过来。

我会画 **latency-throughput frontier**：横轴吞吐，纵轴 P50/P99 TTFT 或 TPOT。只报一个工作点没有意义。加 replica 提高的是 frontier 的位置；加 batch 常常是在同一条曲线上用延迟换吞吐。

## 怎么报数才像做过

声明：tokens 是 prompt 还是 generation、是否含失败重试、百分位而不是均值、SLO 阈值。均值 TTFT 会被短请求拉好看。计费若按 token，还要和 goodput 分开：用户没等到的 token 不应算收入。Prefix cache 会让 TTFT 对「命中用户」很好看，对冷启动用户仍差，要分场景报，见 `sys-prefix-cache-isolation`。admission control 把队列堵住，TTFT 的 P99 会下来、throughput 也会下来，这是在 frontier 上选工作点，不是性能回退，见 `sys-admission-control`。能画出「提高并发 → throughput 升、P99 升、goodput 先升后降」的拐点，这题就答完了。不要用单一 tokens/s 和别的模型比，上下文长度、输出长度、缓存命中率不同，分母就不是同一个。

聊天产品先卡 TTFT，代码补全先卡 TPOT，批量摘要可以放宽两者、追求吞吐。Prefix cache 命中会让 TTFT 双峰，要分冷热报。goodput 是这条曲线与 SLO 矩形的交集，不是曲线上最高的那个点。vLLM 的 TTFT 直方图从 `arrival_time` 起算，含排队和 tokenize，对 kernel 优化的同学要主动声明口径。

## 追问

- **Throughput 涨了为什么产品更卡？** 有效 batch 变大，TPOT 涨、排队变长，TTFT 也涨。看 goodput 和 P99，不看平均值。这是在同一条 latency-throughput 曲线上用延迟换吞吐，不是引擎变强了。
- **TTFT 和 prefill 是一回事吗？** Prefill 是 TTFT 的计算部分；TTFT 还含 queue 和 tokenize。vLLM 从 `arrival_time` 起算。只优化 kernel 救不了排队，要配 admission control。
- **Goodput 的 SLO 怎么选？** 按产品：聊天看 TTFT，代码补全看 TPOT，批量摘要可以放宽。没有 SLO 就没有 goodput，只剩一个没有约束的 tokens/s。
- **为什么 PD 分离能提 goodput？** Prefill 和 decode 的最优 batch / 硬件不同，混部时互相伤害。拆池后两条 SLO 可以独立扩，见 DistServe。
- **Prefix cache 会不会让指标骗人？** 会。命中用户 TTFT 很好看，冷启动仍差，要分场景报。命中造成的时序差还可能是侧信道。
- **ITL 和 TPOT 差在哪？** ITL 是相邻 token 间隔序列，TPOT 常对间隔取平均。尾部一个慢 token 拉高平均，直方图才能看见被 prefill 打断的尖刺。流式体感更接近 ITL。
- **只报均值 TTFT 为什么会被打？** 短请求把均值拉好看，P99 已经被排队打穿。必须带百分位，并声明是否含 tokenize、是否从到达时刻起算。
- **goodput 分子包不包含超时后仍生成的 token？** 不应包含。用户没等到的 token 对产品是失败，对计费也不该算收入。否则优化会走向「拼命产出超时 token」。
- **四个指标怎么一句话串起来？** TTFT 是排队加 prefill，TPOT 是 decode 间隔，throughput 是总产出，goodput 是 SLO 内的有效产出。产品比较看 goodput 和 P99，内部看 tokens/s 判断引擎是否喂饱。没有 SLO 就没有 goodput，加并发是在 frontier 上用延迟换吞吐。
