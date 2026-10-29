---
id: tesla-latency-slo
section: xai
order: 8
level: A
title: Tesla：车载延迟 SLO，几乎不能凑 batch，和云端 LLM serving 差在哪
quick: >-
  车载推理跟相机与规划周期同步，同车多相机要一起处理，车辆 batch 几乎为 1。超时会让控制拿到过期结果，不能靠排队凑
  throughput；预算要覆盖预处理、骨干、占用、规划和控制，并测试热降频下的尾延迟。
tags:
  - Tesla
  - Latency
  - SLO
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Tesla AI Day 2022
    url: 'https://www.youtube.com/watch?v=ODSJsviD_SU'
    type: primary
  - title: Tesla AI
    url: 'https://www.tesla.com/AI'
    type: primary
  - title: Tesla AI Day 2021
    url: 'https://www.youtube.com/watch?v=j0z4FweCy4M'
    type: primary
  - title: >-
      Orca — A Distributed Serving System for Transformer-Based Generative
      Models
    url: 'https://www.usenix.org/conference/osdi22/presentation/yu'
    type: primary
---

车载延迟要按规划周期分配，batch 基本是单车的一组同步相机输入。云端可以等更多请求提高 GPU 利用率，车上等下一批就可能漏帧，让规划拿到过期占用。

公开的 AI Day 介绍把 FSD computer 上实时运行的占用网络当作几何底层。「约 10ms 一拍」来自二次转述，只能作为硬实时、batch=1 的口头量级，不能当 Tesla 内部 SLA。云端的对照采用 Orca / 连续 batching 的公开机制。

来一帧就要在本周期内输出占用、车道和障碍，再送给控制。每辆车有自己的加速器，无法等另外 31 辆车凑成 batch=32；例如等 50ms 凑 32 车这样的策略就不适用。因此有下面这些约束：

- Batch 几乎恒为 1（多相机是同一时刻的 $N_{\mathrm{cam}}$ 路，不是 $N_{\mathrm{car}}$ 个请求）。
- 不能用排队换 throughput。队列 20ms 就是漏帧。漏帧比平均延迟更致命。
- 尾延迟就是安全。p50 好看、p99 抖，规划会在关键加塞上拿到过期占用。
- 热和功耗是一等约束。芯片降频等于延迟 SLO 被物理改写。云端可以加机器，车上不能。

Occupancy 必须进规划周期，见 `tesla-occupancy-net`。Hydra 共享骨干是一次前向摊多头，不是凑 batch，见 `tesla-hydra-nets`。公开讲过骨干特征可缓存，那是训练微调的离线技巧，车上每帧仍要跑完。

预算分别留给传感器与预处理、骨干、占用头、规划和控制，并说明哪些不能挪用。模型缩小 20% 这类示意优化也要看完整周期，不能把规划挤出去。

云端 逐 token 生成（decode） 的单位是 token，请求长度不同、到达泊松。Orca 把调度从请求级改成 iteration 级：短请求做完就走，新请求插进来。连续 batching 吃的是等待可被用户忍受（首个 token 的等待时间（TTFT） 几百毫秒常见），换 GPU 常满。KV cache 分页是为了让 batch 里每条序列长度可以长。这些假设车上都不成立：

| | 车载视觉 | 云端 LLM |
| --- | --- | --- |
| 到达 | 相机固定帧率 | 随机请求 |
| Batch | 同车多相机，$B_{\mathrm{car}}=1$ | 跨用户连续 batch |
| 超时 | 漏帧 / 控制过期 | 排队、429、降级模型 |
| 重试 | 基本不能「再推理一次」 | 可以重试或换副本 |
| 目标 | 最坏情况延迟 | throughput + p95 TTFT |

xAI 的 Grok serving 更接近表里的云端：通过并发增大 MoE 专家的 GEMM，见 `xai-grok-moe`。连续 batching 在这里适合作为对照，不能直接套到单车实时调度。

车上能做的「并行」是流水：预处理下一帧、NPU 跑本帧、CPU 规划上一帧结果。这是时间重叠，不是请求级 batch。形状固定才好编译（TensorRT / 自研编译器），动态序列长度是云端的问题。

验证时要看最坏延迟和热节流，不能用云端 p50 throughput 替代。等 8 帧再推理会改变观测时效。数据引擎的离线模型可以更重、采用较大 batch，和车载预算分别设计，见 `tesla-data-engine`。

## 追问

**多相机不是 batch 吗？**
是同一时刻的多视输入，必须对齐到同一规划拍。不是 8 个独立用户请求。
**能不能降分辨率换延迟？**
能，但是评测要按距离切片：远处的薄障碍更容易漏检。延迟档和 交并比（IoU，即两个区域的交集与并集之比） 档要一起报。
**规划能不能异步？**
控制必须用带时间戳的最新占用。异步可以，过期必须标明，不能当新观测。
**和云端 Grok 限流的关系？**
云端用 `xai-rate-limiter` 挡突发；车上没有「429 以后再说」。超预算只能减负或降级功能，不能让用户重试。
