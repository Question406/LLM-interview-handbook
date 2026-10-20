---
id: sys-moe-node-limited-routing
section: systems
order: 37
level: A
title: DeepSeek-V3 的 device-limited routing 怎么限制跨机通信？实现上先选节点还是先选专家？
quick: "每个 token 最多发到 $M$ 台设备（V3 取 $M=4$）。先按「该设备上专家亲和之和」选出 $M$ 台机器，再只在这些机器的专家里 Top-$k$。跨机 all-to-all 的目的 rank 数因此有明确上限。"
tags:
  - MoE
  - DeepSeek
  - Expert Parallel
  - Routing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

这块容易把 device-limited 说成「尽量本地路由的启发式」，或「capacity 的另一种写法」。V3 的约束是硬的：**一个 token 的 $k$ 个 routed expert 必须落在至多 $M$ 台设备上**。先全局 Top-$k$ 再发现跨了 $8$ 个节点，通信已经分散到多个目的地。正确顺序是 **先锁设备集合，再在集合内选专家**。

## 两步选择

专家铺在 EP 组里，每台设备持有 $N/\mathrm{EP}$ 个 routed expert。对 token $t$、设备 $m$，设备亲和是该设备上各专家亲和之和（V3 的亲和是 sigmoid 分数 $s_{i,t}$）：

$$
a_{m,t}=\sum_{i\in\mathrm{device}(m)}s_{i,t}.
$$

1. 取 $a_{m,t}$ 最高的 $M$ 台设备，记为 $\mathcal{M}(t)$。V3 取 $M=4$。
2. 只在 $\bigcup_{m\in\mathcal{M}(t)}\mathrm{experts}(m)$ 里做 Top-$k$（V3 的 $k=8$），选择仍可加 expert bias $b_i$，加权仍用未加 bias 的 $s_{i,t}$，见 `arch-moe-noaux`。

于是该 token 的 dispatch 目的 rank 至多 $M$ 个，而不是「理论上 $k$ 个专家在 $k$ 台不同的机器」。$k=8$、$M=4$ 意味着平均每台入选设备上约 $2$ 个专家，部分通信可以在节点内走 NVLink，跨机 RDMA 消息数也会减少。Shared expert 每卡常开，不走这套 dispatch，见 `arch-shared-expert`。

## 为什么要限制设备数

EP all-to-all 的痛是 **不规则小消息 × 多目的 rank**，见 `sys-expert-parallel`。细粒度 $N=256$ 时，朴素 Top-$8$ 很容易把一个 token 洒到 $8$ 个节点：每条消息只有一份 hidden，启动开销和尾包比带宽更致命，也难以让通信与计算重叠，见 `sys-moe-alltoall-overlap`。Device-limited 把「跨机度」写成路由约束，减少一些专家选择的自由度，让通信目的地更集中。

它不是负载均衡：$M$ 台里仍可能全挤向同一热点专家；bias / 极小 complementary aux 仍要。它也不是 capacity：容量是每专家能接多少 token，device-limited 是每 token 能碰多少设备。

## 实现注意

- **亲和要在限制之前算全局。** 先算全部 $s_{i,t}$，再聚合成 $a_{m,t}$。不要只在本机专家上算分数，否则无法比较「要不要去别的节点」。
- **Top-$k$ 的候选集是设备并集，不是每设备再 Top-$k/M$。** 某台入选设备上的专家可能全被淘汰，那该设备这一 token 就没有 payload。$M$ 是上限不是配额。
- **和节点内拓扑。** 实践上常「节点内尽量满、跨节点按 $M$」。面试对齐 V3 原文：先选 $M$ 设备，再选 $k$ 专家。
- **训推必须同一套 $M$。** 训练 $M=4$、推理改成不限制，路由集合会变，见 `sys-moe-train-infer-routing-mismatch`。

## 追问

- **$M=1$ 是什么？** 每个 token 只在一台设备上选专家，跨机 dispatch 消失，表达力变成「整机一份专家菜单」。过严。
- **$M\ge k$ 还有意义吗？** 上限变松，接近无约束 Top-$k$。$M$ 要落在「通信可以被计算遮住」和「专家可选」之间，V3 用 $4$。
- **设备亲和为什么用 sum 不是 max？** Sum 偏好「那台上有多个还行的专家」的节点，max 偏好「有一个得分特别高的专家」。V3 写的是 sum。
- **和 DualPipe / DeepEP？** 限制跨机消息数，有助于让通信与计算重叠；通信原语仍要专门 kernel。两者叠，不是二选一。
