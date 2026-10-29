---
id: drustz-102aa6c5bfaa6939a0
section: openai
order: 87
level: A
title: Implement a Simple Key-Value Store from Scratch
quick: >-
  original-structured-preparation-guide · Implement a Simple Key-Value Store
  from Scratch
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/b4834cb9-c51e-4405-9adb-f8f28a99335d
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 从零实现简单 KV Store：内存索引与 WAL 恢复

> 内容定位：当前标题只明确“from scratch”。本地真实面经另有“内存 KV 断线后用 log file 恢复”变体，因此这里把 WAL 作为重点 follow-up，而不是声称它属于会员原文。

## 接口与例子

实现 `put(key, value)`、`get(key)`、`delete(key)`；持久化练习版再提供 `recover(log)`：

```text
put("lang", "中文")
put("lang", "Python")
delete("missing")
crash()
recover()            => get("lang") == "Python"
```



内存主索引用哈希表。每次修改先向 append-only WAL 写一条完整记录，再更新哈希表；记录可定义为 `op | key_len | key_bytes | value_len | value_bytes | checksum`。长度按 UTF-8 **字节数**计算，删除用独立 op/tombstone，不用特殊字符串伪装。

## 算法

`put/delete` 在持锁状态下分配递增 sequence，编码记录并 append；如果题目承诺写成功即耐久，还要在返回前 flush/fsync。启动时顺序扫描 WAL，校验长度和 checksum，再按 sequence 重放到空字典。文件尾若只有半条记录，说明崩溃发生在 append 中途：安全做法是忽略这条尾记录并截断到最后一个合法 offset；中间损坏则应报错，不能悄悄跳过。日志过大时写全量 snapshot，再从新 sequence 开始 WAL，切换过程需用临时文件和原子 rename。

## 复杂度与边界

内存 `get/put/delete` 期望 `O(1)`；写日志还需 `O(|key|+|value|)` 编码与 I/O。恢复时间为 `O(L)`，`L` 为日志总字节数；内存为 `O(N)`。需要确认缺失 key 返回 `None` 还是异常、空 key/value 是否允许、重复 sequence、同 key 覆盖、partial write、checksum 失败、fsync 语义、并发写顺序，以及 snapshot 成功但旧 WAL 尚未删除时如何避免重复重放。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b4834cb9-c51e-4405-9adb-f8f28a99335d)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
