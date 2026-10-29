---
id: drustz-ec06e69d2140efd1c8
section: openai
order: 134
level: A
title: Implement a KV Store with Shutdown/Restore
quick: >-
  original-structured-preparation-guide · Implement a KV Store with
  Shutdown/Restore
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
      https://www.1point3acres.com/interview/problems/b3abad37-3795-4610-a47a-c68ea9df6bbb
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# KV Store with Shutdown/Restore：生命周期与原子恢复

> 内容定位：当前标题和本地面经都明确包含 shutdown/restore。下面把重点放在线性化的生命周期；文件大小限制可作为独立 follow-up。

## 状态与接口

对象有 `ACTIVE`、`SHUTTING_DOWN`、`SHUTDOWN` 三态。ACTIVE 支持 `put/get/delete`；`shutdown()` 保存一致快照。恢复推荐通过 `KVStore.restore(medium)` 创建新的 ACTIVE 实例，而不是在旧实例上混合两份状态。

```text
kv.put("x", "1")
kv.shutdown()          # 保存成功，状态变为 SHUTDOWN
kv.put("x", "2")      # 明确抛 StoreClosedError
kv2 = restore(medium)  # kv2.get("x") == "1"
```



`get` 在 shutdown 后是否仍允许是产品约定；练习版允许只读，但必须在接口文档和测试中固定下来。

## 算法与并发

`shutdown` 获取互斥锁，若不在 ACTIVE 则按约定返回或报错；切到 SHUTTING_DOWN 后阻止新写，复制字典形成 snapshot，然后释放锁完成 length-prefix 编码和保存。只有 Medium 确认成功后才切到 SHUTDOWN；保存失败则恢复 ACTIVE，不能声称已安全关机。restore 先把所有分片/单 blob 读到临时缓冲，完整校验后解析到临时 map，最后构造对象。

如果单文件最多 1KB，则把完整字节流切成编号 chunk，并另写 manifest（schema、chunk 数、总长度、checksum、generation）。先写新 generation 的 chunks，最后原子提交 manifest；旧 generation 在提交后再清理，避免崩溃留下“新 manifest + 缺 chunk”。

## 复杂度与边界

总数据 `B` 字节时，shutdown/restore 为 `O(B)`；chunk 上限 `C` 时文件数为 `ceil(B/C)`，辅助内存可为 `O(B)`，流式实现可降到 `O(C)`。需覆盖空库、重复 shutdown、保存中并发 put、保存异常、缺失/乱序/重复 chunk、陈旧 generation、checksum 错误、只写了一半 manifest，以及 restore 后 sequence/generation 是否继续单调递增。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b3abad37-3795-4610-a47a-c68ea9df6bbb)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
