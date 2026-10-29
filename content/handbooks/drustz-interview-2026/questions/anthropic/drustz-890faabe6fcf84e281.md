---
id: drustz-890faabe6fcf84e281
section: anthropic
order: 90
level: A
title: Find Duplicate Files in a System
quick: original-structured-preparation-guide · Find Duplicate Files in a System
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
      https://www.1point3acres.com/interview/problems/ed023e78-cfc9-4f97-b29d-de300fb741b8
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 系统中的重复文件：初始扫描与增量维护

> “持续监控”来自本地同题族的直接追问，公开标题本身没有证明当前隐藏题面一定要求这一部分。

## 目标与接口

先对根目录做一次重复检测，随后处理新增、修改、删除事件，使查询始终能返回当前重复组。

```text
initial_scan(root)
apply(event: ADD | MODIFY | DELETE, path)
duplicate_groups() -> List[List[path]]
```



例如 `a` 与 `b` 内容相同；删除 `a` 后该组消失；新增同内容的 `c` 后，`b,c` 再形成重复组。

## 数据结构与流程

维护 `fingerprint -> paths` 和 `path -> fingerprint` 两个索引。ADD 先读取稳定版本并计算 `(size,digest)`；DELETE 通过反向索引移除；MODIFY 等价于旧版本 DELETE 再 ADD。文件监听事件可能重复、乱序或丢失，因此操作必须幂等，并定期全量 reconciliation。多节点时各 worker 输出 `(size,digest,file_id,version)`，按 key shuffle 汇总，正文尽量留在数据节点，候选再做字节确认。

索引更新应在同一事务中完成：先移除路径的旧 fingerprint，再写入新 fingerprint 和反向映射，避免查询看到一条路径同时属于两个组。大文件计算期间先标记 pending，版本稳定并确认成功后再发布结果；失败则保留旧状态或明确标为未知。

## 复杂度与边界

单次新增读取文件大小 `s`，时间 `O(s)`，索引更新平均 `O(1)`；删除平均 `O(1)`；全量扫描 `O(N+S)`。要处理 rename、原子替换、事件合并、无权限、节点失联、热点 hash（大量空文件）、重试幂等，以及扫描期间版本改变；结果不完整时应显式标记，不能静默漏报。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ed023e78-cfc9-4f97-b29d-de300fb741b8)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
