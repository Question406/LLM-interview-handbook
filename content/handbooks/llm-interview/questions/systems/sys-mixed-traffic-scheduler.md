---
id: sys-mixed-traffic-scheduler
section: systems
order: 22
level: S
title: 长 prompt 把聊天请求 TTFT 打爆时，continuous batching 与 chunked prefill 怎么设计 / 调参？
quick: "Prefill 和 decode 抢同一份 token 预算。用 chunked prefill 把长输入切块和 decode 交错，限制每步 token 数并加抢占规则，再按流量类型分别看 TTFT 和 TPOT 尾部。"
tags:
  - Scheduling
  - Continuous Batching
  - TTFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: vLLM Scheduler Configuration
    url: https://docs.vllm.ai/en/stable/api/vllm/config/scheduler/
    type: primary
  - title: Sarathi-Serve (chunked prefill)
    url: https://arxiv.org/abs/2403.02310
    type: primary
---

别把 continuous batching 理解成「批次越大越好」。Prefill 和 逐 token 生成（decode） 抢的是同一块 GPU token 预算：长 prompt 的 prefill 是大 GEMM、算得动但占得久；短聊天的 decode 每步只吃一个 token，却对调度间隙和 KV 驻留极度敏感。任由一条长 prefill 跑完，后面所有短请求的 首个 token 的等待时间（TTFT） 一起爆炸。算力特性见 `sys-prefill-decode`。这题考的是 **队头阻塞**：平均吞吐可以很好看，交互 SLO 已经死了。调参报告如果只有 token/s，没有按长度桶切的 TTFT/TPOT，等于没做混跑验收。

## 为什么长短混跑会伤 TTFT

TTFT = 排队 + 本次 prefill。短请求本身的 prefill 很短，排队却可能卡在一条数万 token 的文档摘要后面。Decode 侧的 TPOT 同时被拖累：若调度器把整段长 prefill 当成一个不可打断的 step，正在生成的对话会停住等这块算完。用户感知是「打字突然卡一下」，根因常常是 scheduler 把预算一次性给了邻居的长 prefill，decode kernel 未必变慢。日志里要能把这一步的 prefill token 占比打出来，否则线上只能猜。

Continuous batching 解决的是「有请求结束立刻补进新序列」，避免短序列空等。它不自动解决「补进来的是一条超长 prefill」。没有切块时，新来的长请求仍会独占接下来若干毫秒到数秒的计算。这和 `sys-rl-why-vllm-rollout` 里引擎快的原因是同一套调度，只是在线服务还要面对交互 SLO。强化学习（RL） 采样轨迹（rollout） 可以容忍更高的平均延迟，在线聊天不行：同一套引擎、两套 SLO，调度参数不能直接抄训练集群。把 serving 的 chunked prefill 默认值搬进 RL 或反过来，都会在错误的尾巴上优化。

## chunked prefill 怎么交错

Chunked prefill（Sarathi-Serve 一类）把长输入切成固定 token 块，每块和正在进行的 decode step 拼进同一个 `max batched tokens` 预算。一步里可以是「若干 decode token + 一块 prefill」，而不是「先把 32k prompt 算完再理别人」。

现场要能报的旋钮：

- **每轮 `max batched tokens`。** 总预算。太大则一步过长、TTFT 尾部变差；太小则 GPU 吃不饱、吞吐掉下去。
- **Chunk 大小。** 调小可以更频繁地把 decode 插进来，改善交互延迟，但 kernel 启动和调度次数变多。
- **同时等待的 partial prefill 数量。** 太多半成品占 KV 与队列；太少则长请求迟迟开不了工。
- **优先级、抢占、等待上限。** 高优短请求能否打断低优长 prefill；被抢占的长请求要有防饥饿，否则文档流量永远排不到。

这些旋钮互相耦合：缩小 chunk 却同时把 `max batched tokens` 开很大，一步里仍可能塞进超长 prefill，TTFT 尾巴减不下来。调参要一次只动一个，并用同一套合成流量回放，否则说不清是 chunk 还是优先级在起作用。默认值来自通用 serving，不一定适合「短聊为主、偶发长文档」的产品形态。

调参方向：交互流量占比高时，缩小 chunk、给 decode 留预算、限制同时 inflight 的长 prefill。吞吐型离线流量可以加大 chunk，减少切块开销。这些是调度层；挡不住的过载应在 `sys-admission-control` 拒绝或降级，而不是靠无限排队。两个流量类的默认参数不要共用一份：聊天入口和文档入口应有不同的 chunk 与优先级，否则一次活动把文档流量打进来，聊天默认就被改写。配置要按路由或租户分，而不是全局一个 `max batched tokens`。

## 按流量切片验收

不能只追平均 throughput。至少按输入长度桶、输出长度、租户、优先级分别报：

- TTFT 的 P50 / P95 / P99
- TPOT（decode 间隔）
- 排队时延、preemption 次数、partial prefill 队列
- goodput：在 SLO 内完成的请求比例，而不是 token/s

一个典型失败是：总 token/s 上升，但短聊天 P99 TTFT 崩了，长 prefill 吃满了预算。另一个失败是 chunk 过小、调度过碎，decode TPOT 变差，对话「一个字一个字顿」。调参必须同时看这两条尾巴。报警也要按流量类拆：只有全局 token/s 告警时，聊天已经被打挂也不会响。把短请求 P95 TTFT 和长请求排队时延做成独立 SLO。合成流量要用线上比例：真实世界往往是大量短请求被少量长请求卡住，实验比例设错会调出一套上线即失效的参数。回放用生产 trace 的长度直方图，至少按小时切分高峰。

Prefill/decode 分离（PD disaggregation）是更重的解：长 prefill 到专用池，decode 到另一池，用 KV 传输换隔离。chunked prefill 是同池交错，PD 是分池，不要混成一个开关。slime 的 PD 路径见 `slime-pd-disagg`，那是推理集群内部的拆分，和训练 RL 的 HybridEngine 不是一层。

## 一步里预算怎么切

把每个 scheduler step 想成一块固定 token 配额。Decode 每条只要 1 个新 token，但对延迟敏感；prefill chunk 一次能吃掉配额的一大部分。若一步把配额全给某条长 prefill，正在生成的对话会停一拍，TPOT 出现尖刺。若配额全给 decode、长期不切 prefill，长请求的 TTFT 饿死。调参是在这一步的切分比例、chunk 宽和抢占规则上找点，而不是调一个「全局 batch size」。

Admission（`sys-admission-control`）负责把注定超时的长请求挡在门外，调度负责让已经进来的长短共存。验收时把流量合成「短聊 + 长文档」再看双尾巴。

## 追问

- **Chunk 是不是越小越好？** 不是。过小会让算力强度掉下去，decode 也要为更频繁的调度付税。选在「短请求 P95 TTFT 可接受」且 GPU 利用率不明显掉的拐点。拐点随硬件和模型宽度变，要在目标流量上扫，不要抄别家的默认值。
- **和 continuous batching 的关系？** Chunking 决定一步里 prefill 占多少预算；continuous batching 决定一步结束谁补位。两者一起才能混跑。只有后者时，新来的长 prefill 仍可能独占接下来好几步。
- **KV 不够时抢谁？** 通常抢还在 prefill、或优先级低、或已生成很长的请求。要有最大抢占次数，避免一条请求被反复踢出。被抢占的请求应回到队列而不是直接失败，除非已经过了 deadline。
- **只加卡能代替调调度吗？** 能缓解均值，改不了「一条长 prefill 挡住一排短请求」的队头阻塞。规模上来之前先把交错和 admission 做对。加卡之后队头阻塞还在，只是发生得更晚、更贵。
