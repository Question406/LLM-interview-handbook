---
id: p3a-openai-design-sora-video-generation
section: openai
order: 632
level: A
title: "OpenAI：Sora 视频生成：GPU 调度与失败恢复"
quick: "用异步 job 接收视频生成，API 返回任务 id，调度器按资源与公平策略分配 GPU。worker 用租约和 checkpoint 支持续跑，先上传 attempt 产物，再以任务版本 CAS 原子发布结果。"
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

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

视频生成走异步任务：API 写入 job 后返回任务 id，调度器分配 GPU，客户端轮询或订阅进度。生成以分钟计，API 同步等待会占住请求；恢复则靠 checkpoint 和租约。

练习假设每个任务耗时 2 分钟，每秒到达 2 个任务，每块 GPU 同时跑一个任务，暂不考虑批处理。先确认 GPU 池会不会被其他业务抢占，以及是否有付费优先级。由 Little 定律，同时运行的任务数为 2 × 120 = 240，这是零排队所需的最低 GPU 任务槽数，实际还要留波动余量。

API 用 idempotency key 查重，重复点击复用已有任务，再把新 job 写入持久任务库，通过 Outbox 通知调度器。调度器按资源估计和公平策略选 worker，发出租约；worker 定期续约并写 checkpoint。调度和状态属于控制平面，大视频的读写属于数据面，两者分开。

job 保存模型版本、seed、参数、资源估计、checkpoint、attempt 和 lease token，沿 queued → running → uploading → succeeded 推进，cancelled 和 failed 是独立终态。完成生成后，worker 先把文件写到本次 attempt 的专属路径，再以任务版本做 CAS，提交最终结果指针并置 succeeded，客户端这时才看到下载链接。

worker 失联、租约到期后可以重试，旧 worker 返回时也无权再发布。用户取消后到达的结果不能覆盖 cancelled。原子发布能防止半成品或两份结果同时可见。还要说明 OOM 怎么处理、长尾怎样避免拖垮队列，并监控排队等待、成功率、GPU 利用率和每条成片的 GPU 分钟数。

## 追问

**抢占后怎么续跑？**
checkpoint 标注模型和代码版本，只在兼容 worker 上恢复；无法恢复就从头重试，额外 GPU 时间也计入预算。

**GPU 池突然缩小一半怎么办？**
排队时间会翻倍以上，准入层应按当前容量估算等待，超过上限就拒绝或提示用户。优先保留运行中的任务，必要时抢占低优先级任务，再依靠 checkpoint 续跑，避免队列无限增长。
