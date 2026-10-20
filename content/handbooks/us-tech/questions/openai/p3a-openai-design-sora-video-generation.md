---
id: p3a-openai-design-sora-video-generation
section: openai
order: 632
level: A
title: "OpenAI：Sora 视频生成：GPU 调度与失败恢复"
quick: "视频生成走异步任务：API 先返回任务 id，调度器在有限 GPU 池里按资源和公平策略分配 worker，产物写对象存储后原子发布。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · design-sora-video-generation"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-sora-video-generation
    type: secondary
---

## 题目

在有限且容量会波动的 GPU 池上，接收用户的视频生成请求并异步完成生成。需要讨论调度、抢占、故障恢复和结果发布。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

视频生成耗时以分钟计，API 不能同步等待。正确形态是：API 立刻返回任务 id，调度器按资源需求和公平策略把任务分给 GPU worker，生成的视频放进对象存储，客户端轮询或订阅进度。

可靠性靠两样东西：检查点让被抢占的任务能续跑，任务租约让失联的 worker 被安全替换。用户重复点击时，用幂等键复用已有任务，而不是再排一个。

回答时重点讲清楚四件事：取消怎样生效、OOM 怎样处理、长尾任务怎样避免拖垮队列，以及输出发布为什么必须是原子的。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

视频生成请求异步执行。假设单个任务耗时 2 分钟，到达速率每秒 2 个，每块 GPU 同一时刻只跑一个任务，先不考虑批处理。

开始回答时复述这些假设，问面试官 GPU 池是否会被其他业务抢占、是否有付费优先级。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. API 接收请求，写入持久任务库，并通过 Outbox 通知调度器。
2. 调度器把任务分配给空闲 GPU worker。
3. worker 生成视频，把产物写进对象存储。

控制平面（调度、状态）和视频数据面（大文件读写）分开。客户端按 job id 查询或订阅进度。

**2. 数据模型和状态变化。** job 记录模型版本、seed、参数、资源估计、checkpoint、attempt 和 lease token。状态按 queued → running → uploading → succeeded 推进，cancelled 和 failed 是独立的终态。

**3. 走一遍正常任务。** 用户提交一段 prompt，API 用幂等键查重后建 job，返回 job id。调度器选中一台空闲 GPU，给 worker 发租约；worker 定期续约并写 checkpoint。生成完成后，worker 把视频写到本次 attempt 的专属路径，状态改为 uploading；随后用任务版本做 CAS，把"最终结果指针"指向这个 attempt 的文件并置为 succeeded。客户端此时才看到可下载链接。

**4. 失败、重复与恢复。**

- worker 失联，租约到期后任务可以重试，但旧 worker 即使回来也不能再发布结果。
- 产物先写 attempt 路径，再由任务版本 CAS 提交最终指针，避免半成品或两份结果同时可见。
- 用户取消之后仍到达的结果不能覆盖 cancelled 状态。

**5. 容量和验证指标。** 由 Little 定律，系统中同时在跑的任务数 = 到达率 × 耗时 = 2 × 120 = 240，这是零排队时需要的最低 GPU 任务槽数，实际还要留余量应对波动。衡量指标包括排队等待时间、成功率、GPU 利用率，以及每条成片消耗的 GPU 分钟数。

### 面试追问与参考回答

**任务被抢占后怎样续跑？** 检查点要标注模型版本和代码版本，只能在兼容的 worker 上恢复。不能恢复时从头重试，额外消耗的 GPU 时间计入预算和监控。

**GPU 池突然缩小一半怎么办？** 新请求的排队时间会翻倍以上，所以准入层要根据当前容量估算等待时间，超过上限就拒绝或提示用户，而不是让队列无限增长。已在运行的任务优先保留，低优先级任务可以被抢占并依赖检查点续跑。
