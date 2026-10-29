---
id: drustz-7058d2ea233a66c5eb
section: anthropic
order: 82
level: A
title: File Deduplication Using Hashing
quick: original-structured-preparation-guide · File Deduplication Using Hashing
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
      https://www.1point3acres.com/interview/problems/8bcf1ece-d504-4803-901a-bfb2f6872c37
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 使用 Hash 查重：碰撞后仍要精确确认

> 标题强调 hashing；本地面经明确追问“是否存在完美 hash”。答案是否定的，所以摘要只能生成候选组。

## 接口与例子

```python
def deduplicate(paths: list[str]) -> list[list[str]]: ...
```



输入可由目录遍历阶段产生。若 `a.bin` 与 `b.dat` 字节均为 `00 01`，`c.bin` 为 `00 02`，只输出 `[a.bin,b.dat]`。即使人为构造出相同摘要但不同内容，也不能误报。

## 算法

先按 size 分桶，再为同大小文件流式计算全文 digest。对每个 `(size,digest)` 候选桶，维护若干代表文件：新文件依次与代表逐块比较，相同则加入对应组，不同则成为新代表。最后只保留大小至少为 2 的等价类。不能只把桶内所有文件与第一个比较后丢掉“不等”的文件，因为一次 hash 碰撞桶里可能同时含有多个真正的重复组。

代表文件法实际是在碰撞桶内建立“字节相等”的等价类：相等具有自反、对称和传递性，所以每个文件只需加入一个已匹配代表；与所有代表都不等时才新建一类。返回前过滤单成员类即可。

## 复杂度与边界

Hash 阶段为 `O(S)`；通常确认阶段也近似 `O(S)`，但对抗性碰撞时最多出现桶内两两比较。空间 `O(N)` 加固定块缓冲。空文件可成组；比较时应固定文件版本，避免 TOCTOU。MD5/xxHash 可作快速过滤，SHA-256 降低碰撞概率，但承诺 exact 时最终字节比较才是正确性保证。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/8bcf1ece-d504-4803-901a-bfb2f6872c37)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
