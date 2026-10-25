---
id: p3a-anthropic-sd-q3-model-distribution
section: anthropic
order: 624
level: A
title: "Anthropic：模型权重分发：带宽下界、树与分块 swarm"
quick: "我会先用源出口和单机接收量算分发时间下界，再选树形广播或分块互传。带宽是上下行独立还是共享，会直接改变估算；主机收齐并校验所有块以后才能切到新版本。"
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

我会先算带宽下界，再决定用直拉、树形广播还是分块互传。练习里 400GB 发到 200 台主机，每条链路 10Gbps，按十进制就是 1.25GB/s：单台光接收就至少 320 秒，单个 repo 串行发 200 份，出口至少要 64000 秒。

这说明应该让收到数据的主机参与转发。把 checkpoint 切成固定大小的块，manifest 记录整体版本和每块 hash，种子先从 repo 下载，再通过树或类似 BitTorrent 的 swarm 传播。控制器记录每块有哪些持有者、各主机是否 ready。

以主机 H 为例，收到新 deployment 后先读 manifest，再向控制器找块的持有者，优先从同机架、负载低的节点拉。每块到达先校验 hash，更新 `host_block_status`，这时就能转发给别人。全部到齐并校验通过，才加载模型、自检并报告 ready，路由只向 ready 且版本匹配的机器发流量。部署信息用 `deployment(id, model_hash, manifest)` 和 `ready_epoch` 记录，旧 epoch 的 ready 不能覆盖新部署，版本切换要保持原子性。

下载中断只重取缺块，坏块不能进入 swarm。个别机器很慢时可以先剔除，之后补齐，不必让整个部署等它。

上述估算还要结合机架拓扑和交换机上行带宽。上下行各自独立 10Gbps，和上下行共享 10Gbps，是两种预算；共享时一边收一边发，必须把上传量和下载量合起来算，树和 swarm 都不能突破这个限制。

### 面试追问与参考回答

**BitTorrent 式分发总是最快的吗？**
不一定。小集群或拓扑约束强时，块调度的控制开销和机架间拥塞可能让它更慢。先算割集带宽，再看实测的块调度效果，不能只背树形或 ring 的结论。

**上下行共享 10Gbps 时，下界会怎样变？**
每台主机收 400GB 的同时还要把块转发出去，接收可用的带宽小于 10Gbps，单机 320 秒的下界就达不到了。具体是多少取决于每台主机平均要上传多少数据，所以要按方案把上传量和下载量合起来除以共享带宽来估算。
