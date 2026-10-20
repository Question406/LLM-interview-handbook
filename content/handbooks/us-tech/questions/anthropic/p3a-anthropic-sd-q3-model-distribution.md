---
id: p3a-anthropic-sd-q3-model-distribution
section: anthropic
order: 624
level: A
title: "Anthropic：模型权重分发：带宽下界、树与分块 swarm"
quick: "分发大模型 checkpoint 前先用源节点出口和每台主机的接收量估出时间下界，再比较全员直拉、树形广播和分块互传。"
companies:
  - anthropic
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · sd-q3-model-distribution"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/sd-q3-model-distribution
    type: secondary
---

## 题目

把数百 GB 的模型 checkpoint 分发到数百台主机，每条链路都有带宽上限。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

先算下界：源节点的出口带宽要送出多少数据，每台主机至少要收多少数据，各需要多少时间。有了下界，再比较三种方案：所有主机直接从源拉、树形广播、分块互传（类似 BitTorrent）。

如果每台主机的上传和下载共享同一份带宽预算，就必须把两者放在一起算，不能分开估。能否安全上线还取决于分片校验、版本原子切换、ready 检查和失败重取。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

把 400GB 模型从单个 repo 发给 200 台主机，每条链路 10Gbps。先分别讨论两种预算：上下行各有独立的 10Gbps，以及上下行共享 10Gbps。

开始回答时复述这些范围，问面试官机架拓扑和交换机的上行带宽。

### 一套可展开的参考答案

**1. 架构与关键路径。** checkpoint 切成固定大小的块，附上每块的 hash 和整体 manifest。种子节点先从 repo 拉取，然后在主机之间做树形广播或 swarm 分发。控制器跟踪每个块在哪些主机上可用，以及每台主机是否 ready。

**2. 数据模型和状态变化。** `deployment(id, model_hash, manifest)`、`host_block_status` 和 `ready_epoch`。主机要等所有块都校验完成才标为 ready；路由只把流量发给 ready 且版本匹配的主机。

**3. 走一遍一台主机的下载。** 控制器发布新 deployment，主机 H 拿到 manifest，看到需要哪些块。它向控制器查询每个块当前的持有者，优先从同机架、负载较低的节点拉；每收到一块就校验 hash，写入 `host_block_status`，并开始把这一块上传给别的主机。所有块到齐并校验通过后，H 加载模型、自检，报告 ready，路由随即开始给它派发该版本的流量。

**4. 失败、重复与恢复。**

- 下载中断按块重试，校验失败的坏块不进入 swarm。
- 旧 epoch 的 ready 不能覆盖新部署。
- 个别主机很慢时，先把它剔除、事后补齐，不让全局等最慢的节点才开始接流量。

**5. 容量和验证指标。** 10Gbps 理想情况下是 1.25GB/s（十进制单位）。单台主机接收 400GB 的下界是 320 秒；如果单个 repo 串行发 200 份，出口下界是 64000 秒。树形广播和分块互传能减轻源出口压力，但在共享上下行预算时，每台主机一边收一边发，必须把两者合起来核算。

### 面试追问与参考回答

**BitTorrent 式分发总是最快的吗？** 不一定。小集群或拓扑约束强时，块调度的控制开销和机架间拥塞可能让它更慢。先算割集带宽，再看实测的块调度效果，不能只背树形或 ring 的结论。

**上下行共享 10Gbps 时，下界会怎样变？** 每台主机收 400GB 的同时还要把块转发出去，接收可用的带宽小于 10Gbps，单机 320 秒的下界就达不到了。具体是多少取决于每台主机平均要上传多少数据，所以要按方案把上传量和下载量合起来除以共享带宽来估算。
