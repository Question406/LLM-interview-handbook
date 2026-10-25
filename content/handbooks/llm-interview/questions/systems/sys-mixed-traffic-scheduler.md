---
id: sys-mixed-traffic-scheduler
section: systems
order: 22
level: S
title: 长 prompt 把聊天请求 TTFT 打爆时，continuous batching 与 chunked prefill 怎么设计 / 调参？
quick: "我会把长 prompt 切成 prefill chunk，与 decode 交错执行，并限制每一步的 token 预算和并行长 prefill 数。长输入一次占满 GPU，会让短聊天排队、正在生成的对话停顿；切块后还要加优先级和防饥饿规则。调参分别看短聊和长文档的 TTFT、TPOT 尾部，吞吐提高后仍要守住交互 SLO。"
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

我会用 continuous batching 及时补请求，再用 chunked prefill 把长输入拆开，给 decode 持续留预算。比如一条数万 token 的文档摘要进来，如果先把它整段算完，短聊天会排队，已经开始输出的对话也会停顿。两类任务在争同一块 GPU：prefill 是占用较久的大 GEMM，decode 每轮每请求只需要一个 token，却对调度间隙和 KV 驻留敏感，算力特性见 `sys-prefill-decode`。

TTFT = 排队 + 本次 prefill。短请求自己的 prefill 很短，也可能被前面的长文档挡住；正在 decode 的 TPOT 同时会有尖刺。此时 decode kernel 未必更慢，可能只是调度器把本轮预算都给了 prefill。日志要记录每步 prefill token 占比，验证时按输入长度桶看 TTFT / TPOT，平均 token/s 无法显示这些问题。

Continuous batching 决定请求结束后谁补位，无法自动限制补进来的长 prefill。没有切块，一条请求仍可能独占几毫秒到数秒。这与 `sys-rl-why-vllm-rollout` 的调度收益相通，但 RL rollout 可容忍更高平均延迟，在线聊天要守交互 SLO，两边的默认参数不能直接互抄。

## 在一步里分配 token 预算

Chunked prefill 把长输入分块，与 decode 交错，Sarathi-Serve 就采用这类思路。一步可以执行若干 decode token 加一块 prefill，不必先算完 32k prompt。预算若长期全给 decode，长请求的 TTFT 又会饿死，所以要一起控制每轮 `max batched tokens`、chunk 大小、同时进行的 partial prefill 数，以及优先级、抢占和最大等待时间。

总预算太大，一步太长，TTFT 尾部会变差；太小则吞吐下降。Chunk 缩小能更频繁插入 decode，却增加 kernel 启动和调度次数。Partial prefill 太多会占 KV 和队列，太少又会让长请求难以开工。高优短请求允许打断低优长请求时，还要有 aging 等防饥饿措施和最大抢占次数；被抢占者通常回队列，超过 deadline 才失败。

这些参数互相影响。比如 chunk 缩小却把 `max batched tokens` 开得很大，一步仍能塞进大量 prefill。调参应固定回放流量、一次动一个变量，区分收益来自 chunk 还是优先级。交互为主时缩小 chunk、保留 decode 预算并限制 in-flight 长 prefill；吞吐型离线流量可以增大 chunk，减少切块开销。聊天和文档入口可以按路由或租户设不同参数，避免一次文档流量高峰改变聊天延迟。

## 用两类流量分别验收

回放采用线上长度直方图与流量比例，至少按小时覆盖高峰，再按输入长度、输出长度、租户和优先级分别看 TTFT P50 / P95 / P99、TPOT、排队时延、preemption 次数、partial prefill 队列与 goodput，也就是 SLO 内完成的请求比例。常见失败是总 token/s 提高，短聊 P99 TTFT 却变差；另一个是 chunk 太小，让 decode 因调度开销而一字一顿。

报警同样按流量类拆，给短请求 P95 TTFT 和长请求排队时间各设 SLO。调度负责让已经进入的长短请求共存，注定超时的过载要由 admission 拒绝或降级，见 `sys-admission-control`。持续排队和仅看全局 token/s 都会掩盖交互失败。

更重的做法是 PD disaggregation：prefill 和 decode 各用专用池，以 KV 传输换隔离。它与同池 chunking 可以分别评估；slime 的池内拆分见 `slime-pd-disagg`，和 RL 的 HybridEngine 也处在不同层。

## 追问

**Chunk 越小越好吗？**
不是。太小会降低计算效率，并增加启动和调度开销。在目标模型、硬件和流量上找短请求 P95 TTFT 可接受、GPU 利用率又未明显下降的点。

**KV 不够时抢谁？**
通常考虑还在 prefill、低优先级或已生成很长的请求，但要限制反复抢占。回到队列后还应能靠等待时间得到机会。

**加卡能替代调度吗？**
能缓解平均排队，仍解决不了一条长 prefill 阻挡短请求的方式。先做好交错和 admission，再按实际吞吐扩容量。
