---
id: drustz-fb0c623ac0bcc85a52
section: openai
order: 151
level: A
title: Map Serialization and De-serialization
quick: original-structured-preparation-guide · Map Serialization and De-serialization
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
      https://www.1point3acres.com/interview/problems/f47116fa-8557-4c2e-b784-18ae4e55df2c
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Map Serialization and De-serialization：可逆二进制格式

## 证据边界

当前公开标题只确认 Map 的序列化与反序列化；本地保存的同题族公开页明确禁止 JSON/pickle，并允许 key/value 含分隔符、换行、NUL 和 Unicode。下面据此给出完整练习题面，但不是当前会员页的逐字内容，也不把文件分片 follow-up 混进本题。

## 题面、接口与示例

实现字符串字典的无损往返：

```python
def serialize(data: dict[str, str]) -> bytes: ...
def deserialize(blob: bytes) -> dict[str, str]: ...
```



`{"a:b":"换行\n🙂", "":"x=y"}` 编码后再decoding必须逐项相同；不能依赖某个不会出现在内容里的分隔符。

## 解法与关键结构

先写 magic、schema version 和条目数；每条写 `u32 key_byte_len + key_utf8 + u32 value_byte_len + value_utf8`。长度必须是 UTF-8 **字节数**，不是字符数。反序列化用游标依次读定长整数和对应字节；每次读取前检查剩余长度，全部成功后才发布临时 map，并要求游标恰好到文件尾。若要确定性输出，可按 key 的编码字节排序。

正确性依赖“长度字段唯一确定下一段边界”：内容即使包含冒号或换行，也不会改变游标位置；按相同规则依次读取全部条目，就能恢复原 key/value。条目数和最终游标检查还能发现少读、截断或多余数据，而不是静默接受模糊格式。

## 复杂度与边界测试

设编码总字节 `B`、条目数 `N`，两方向均为 `O(B+N)` 时间、`O(B+N)` 输出/结果空间。测试空 map、空 key/value、emoji、换行与 NUL、截断 header、超大声明长度、非法 UTF-8、重复 key、未知版本和额外尾字节；循环拼接 immutable bytes 会退化为 `O(B²)`，应收集片段后一次 join。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/f47116fa-8557-4c2e-b784-18ae4e55df2c)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
