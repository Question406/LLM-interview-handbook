---
id: drustz-d11bae6aa3a48f5098
section: anthropic
order: 44
level: A
title: Find Duplicate Files by Content
quick: original-structured-preparation-guide · Find Duplicate Files by Content
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
      https://www.1point3acres.com/interview/problems/ab528b5f-7c0a-5745-adfb-22d830ac4807
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 按内容去重：面向多节点文件集合

> 当前公开标题与上一题同名，无法从标题证明隐藏页一定要求分布式；本篇专门整理本地直接面经反复出现的 multi-node follow-up，避免和单机多级 hash 版本重复。

## 问题模型

文件分布在多个存储节点。返回全局重复组，路径需要包含节点或对象存储 bucket：

```python
def find_global_duplicates(manifests: Iterable[FileMeta]) -> list[list[FileId]]: ...


# FileId = (node, path, version)
```



例如 `n1:/a` 与 `n3:/x` 内容相同，即使不能共享本地路径，也必须归入一组。

## 数据流

第一阶段，各节点本地扫描并按 size 淘汰唯一项，再流式计算候选文件摘要，发出 `(size, digest) -> FileId`；不要把文件正文穿过 shuffle。协调层按 key 分区，同 key 必须路由到同一 reducer。reducer 输出长度大于一的候选组；若要求绝对正确，选择代表副本，让其他副本在数据本地逐块比较，或安排点对点分块校验。

每条记录携带不可变 `version/etag`。worker 重试使用 `(job_id, FileId)` 做幂等去重，避免同一路径重复计数；节点失联时结果应标为 incomplete，而不是静默宣布无重复。热点摘要（例如大量相同空文件）不能全部压到一台 reducer，可先局部聚合或把路径列表分片存储。

## 增量模式

全量扫描之后，文件创建/修改事件重新计算摘要并原子更新 `file_to_hash`、`hash_to_files`；删除事件通过反向索引移除旧成员。事件可能重复或乱序，因此按文件版本拒绝旧事件。只有从一条路径变成两条路径时触发“出现重复”通知，可避免重复告警。

## 复杂度与边界

全局仍至少读取所有候选内容一次，计算量 `O(N + S)`；网络正常只传 `O(N)` 条元数据，精确字节确认另计。单节点内存取决于其分片，协调索引总量 `O(N)`。需讨论跨地域带宽、加密文件、扫描中修改、权限、hash 碰撞、数据驻留，以及一致性要求是某一快照的精确答案还是最终一致的近实时视图。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ab528b5f-7c0a-5745-adfb-22d830ac4807)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
