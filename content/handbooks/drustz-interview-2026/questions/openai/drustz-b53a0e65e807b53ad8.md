---
id: drustz-b53a0e65e807b53ad8
section: openai
order: 181
level: A
title: Persistent Key-Value Store with Accurate Serialization/Deserialization
quick: >-
  original-structured-preparation-guide · Persistent Key-Value Store with
  Accurate Serialization/Deserialization
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
      https://www.1point3acres.com/interview/problems/25252736-d196-40ba-8c6f-51b7b416a341
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Persistent KV：准确序列化、校验与原子恢复

## 证据边界

公开标题强调 persistent 和 accurate serialization/deserialization；同题族资料还报告固定大小文件分片。下面把“任意字符串精确往返、损坏不产生半恢复状态”作为核心，把 1 KiB 分片明确标成可选 follow-up，并非声称隐藏题面一定要求。

## 题面、接口与示例

实现 `put/get/delete`、`save()` 与 `load()`。例如 key 为 `"猫\x00"`、value 为 `"🙂\n,"`，跨进程保存恢复后字节语义不变；若持久化数据被截断或篡改，load 必须报错，旧内存状态保持不动。

```text
save() -> generation/checkpoint
load() -> 完整恢复或失败，不允许部分成功
```



## 格式与提交协议

用 `magic + version + entry_count + length-prefixed entries + checksum`；按 UTF-8 字节长度解析，并拒绝重复 key、越界长度和 trailing bytes。保存时生成不可变 snapshot，写入新 generation，读回校验后再原子切换 manifest；失败不覆盖旧 generation。若每文件最多 1024 字节，把完整字节流切为 `chunk_0..n-1`，manifest 记录 generation、块数、总长和 checksum，且最后提交 manifest。

恢复总是先读取一个已提交 manifest，再按它指定的 generation 取块；因此崩溃留下的新孤儿块不会被误用。checksum 验证的是重组后的完整字节流，length-prefix 再验证内部结构，两层分别防传输损坏与解析歧义。垃圾回收只能删除不被当前 manifest 指向的旧 generation。

## 复杂度与边界

总数据 `B`、条目 `N` 时 save/load 为 `O(B+N)`；普通字典操作期望 `O(1)`。整块实现需 `O(B)` 缓冲，流式分片可降为 `O(C)`。覆盖空库、零长度字段、Unicode、旧 schema、错误 checksum、缺块/乱序块、partial write、陈旧 manifest、保存中并发修改、重复 load，以及新快照提交成功但旧块尚未清理时的恢复选择。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/25252736-d196-40ba-8c6f-51b7b416a341)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
