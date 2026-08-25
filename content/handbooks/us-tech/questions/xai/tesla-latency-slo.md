---
id: tesla-latency-slo
section: xai
order: 8
level: A
title: Tesla：车载延迟 SLO，几乎不能凑 batch，和云端 LLM serving 差在哪
quick: >-
  车载是相机锁相、batch 几乎恒为 1、超时就是漏帧；云端 LLM 靠连续 batching 换吞吐。Occupancy 必须塞进规划周期，不能等 50ms
  凑 32 车。热功耗和尾延迟比平均 FLOP 更重要。
tags:
  - Tesla
  - Latency
  - SLO
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Tesla AI Day 2022
    url: https://www.youtube.com/watch?v=ODSJsviD_SU
    type: primary
  - title: Tesla AI
    url: https://www.tesla.com/AI
    type: primary
  - title: Tesla AI Day 2021
    url: https://www.youtube.com/watch?v=j0z4FweCy4M
    type: primary
  - title: Orca — A Distributed Serving System for Transformer-Based Generative Models
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
---

## 题怎么来的

FSD / 车载推理岗会拿「为什么车上不能像 ChatGPT 那样 batch」当系统设计题。公开锚点是 AI Day：占用网络在 FSD computer 上实时跑、作为几何底层；二次转述里常见「约 10ms 一拍」，我把它当 **硬实时、batch=1** 的口头量级，不当内部 SLA。云端对照用 Orca / 连续 batching 的公开机制，不装 Tesla 编译器内部数字。

## 车载 SLO：锁相机，不锁队列

车上时间轴是相机帧和规划周期，不是 GPU 利用率。来一帧就必须在本周期内给出占用、车道、障碍，送给控制。等下 31 辆车凑成 batch=32，物理上不存在——每辆车自己一块加速器。所以：

- **Batch 几乎恒为 1**（多相机是同一时刻的 $N_{\mathrm{cam}}$ 路，不是 $N_{\mathrm{car}}$ 个请求）。
- **不能用排队换吞吐。** 队列 20ms 就是漏帧。漏帧比平均延迟更致命。
- **尾延迟就是安全。** p50 好看、p99 抖，规划会在关键加塞上拿到过期占用。
- **热和功耗是一等约束。** 芯片降频等于延迟 SLO 被物理改写。云端可以加机器，车上不能。

Occupancy 必须进规划周期，见 `tesla-occupancy-net`。Hydra 共享骨干是为了 **一次前向摊多头**，不是为了凑 batch，见 `tesla-hydra-nets`。公开讲过骨干特征可缓存，那是 **训练微调** 的离线技巧，车上每帧仍要跑完。

我会把预算拆开讲，数字只作示意：传感器和预处理、骨干、占用头、规划、控制。面试官要听的是你知道 **哪一段不能挪用**。不能说「模型再小 20% 就行」却把规划算子挤出周期。

## 和云端 LLM serving 的差

云端 decode 的单位是 token，请求长度不同、到达泊松。Orca 把调度从请求级改成 iteration 级：短请求做完就走，新请求插进来。连续 batching 吃的是 **等待可被用户忍受**（TTFT 几百毫秒常见），换 GPU 常满。KV cache 分页是为了让 batch 里每条序列长度可以长。这些假设车上都不成立：

| | 车载视觉 | 云端 LLM |
| --- | --- | --- |
| 到达 | 相机固定帧率 | 随机请求 |
| Batch | 同车多相机，$B_{\mathrm{car}}=1$ | 跨用户连续 batch |
| 超时 | 漏帧 / 控制过期 | 排队、429、降级模型 |
| 重试 | 基本不能「再推理一次」 | 可以重试或换副本 |
| 目标 | 最坏情况延迟 | 吞吐 + p95 TTFT |

xAI 侧的 Grok serving 反而更像右列：靠并发把 MoE 专家 GEMM 做实，见 `xai-grok-moe`。Tesla 岗把那套搬上车是减分。不要讲 continuous batching 除非你明确说这是 **云端对照、车上禁用**。

车上能做的「并行」是流水：预处理下一帧、NPU 跑本帧、CPU 规划上一帧结果。这是 **时间重叠**，不是请求级 batch。形状固定才好编译（TensorRT / 自研编译器），动态序列长度是云端的问题。

错法：用云端 p50 吞吐量答车载；建议「等 8 帧再推理一次」；把热节流当成运维问题而不是 SLO 的一部分。数据引擎的离线大模型可以随便重、随便 batch，那正好说明 **训练和车上是两套延迟世界**，见 `tesla-data-engine`。

## 追问

- **多相机不是 batch 吗？** 是同一时刻的多视输入，必须对齐到同一规划拍。不是 8 个独立用户请求。
- **能不能降分辨率换延迟？** 能，但是评测要按距离切片：远距薄障碍先死。延迟档和 IoU 档要一起报。
- **规划能不能异步？** 控制必须用带时间戳的最新占用。异步可以，过期必须标明，不能当新观测。
- **和云端 Grok 限流的关系？** 云端用 `xai-rate-limiter` 挡突发；车上没有「429 以后再说」。超预算只能减负或降级功能，不能让用户重试。
