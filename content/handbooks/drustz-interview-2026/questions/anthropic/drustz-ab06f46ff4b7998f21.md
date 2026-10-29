---
id: drustz-ab06f46ff4b7998f21
section: anthropic
order: 66
level: A
title: Design a Data Batcher (Code & Design)
quick: original-structured-preparation-guide · Design a Data Batcher (Code & Design)
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/d0bfa6e3-f932-41aa-9448-bb8d17c493eb
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Design a Data Batcher：从单机实现到可恢复数据管线

> 内容定位：这一 UUID 的公开标题偏“设计”，本地直接面经确认了 weighted registry、offset checkpoint 与不整除追问。下面在核心算法上增加 API、不变量和故障设计；它仍是原创准备答案，而非官方或会员标准答案。

## API 与语义

```text
DataBatcher(registrySnapshot, weights, batchSize)
nextBatch() -> Batch
checkpoint() -> Checkpoint
restore(checkpoint, registrySnapshot) -> DataBatcher
```



先定义三个不变量：已返回的 item 不会因普通恢复而再次返回；同一 snapshot + 同一 checkpoint 的后续序列确定；长期来源比例接近 weights。还要问清 source 到末尾时是循环新 epoch、停止，还是从其余源renormalization。

## 分层设计

把实现拆为三层：`RegistryReader` 负责 `read(source, offset)`；`WeightedScheduler` 只决定下一个 source；`BatchAssembler` 聚合 item 并定义交付边界。确定性比例模式可用 smooth weighted round-robin，checkpoint 保存 per-source offset 和 scheduler credit；随机模式则保存 counter-based RNG 的 seed/draw index。二者都不能依赖 map 的非稳定遍历顺序。

## 一致性与恢复

最容易忽略的是 checkpoint 与下游交付之间的原子性。若先返回 batch 再落 checkpoint，崩溃后可能重复；先落 offset 再返回则可能丢批。单机练习可明确提供 at-least-once，并让下游用 `batchId` 去重；更强语义需要把“提交 checkpoint”和“确认 batch”放进同一个事务/两阶段协议。

checkpoint 示例：

```json
{
  "version": 1,
  "registryVersion": "sha256:...",
  "nextBatchId": 42,
  "offsets": { "code": 18, "math": 9 },
  "scheduler": { "credits": { "code": -1, "math": 1 } },
  "buffer": []
}
```



权重和不能整除 batch size 时，不应每批都把余数固定给同一源；跨 batch 保留 fractional credit，长期消除偏差。

## 扩展到多 worker

为每个 worker 分配互不重叠的 `(source, offset range)`，或由 coordinator 发带 lease 的 batch plan。lease 超时后可重派，因此 batch ID 必须幂等。动态 registry 不可悄悄改当前序列，应生成新 version，只在 checkpoint 边界显式迁移并记录权重变化。

## 复杂度与边界

朴素 scheduler 每 item `O(s)`，状态 `O(s+b)`；`s` 是数据源数、`b` 是缓冲项数。读取成本还取决于 registry。测试 batch size 为 1、与权重和互质、空/耗尽 source、权重 0、恢复多次、旧 schema、registry version 不匹配、checkpoint 写到一半、batch 已交付但未确认、worker crash 和动态改权重。面试时先完成单机确定性版本，再讨论这些一致性选择。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/d0bfa6e3-f932-41aa-9448-bb8d17c493eb)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
