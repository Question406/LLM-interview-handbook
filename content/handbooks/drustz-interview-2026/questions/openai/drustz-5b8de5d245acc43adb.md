---
id: drustz-5b8de5d245acc43adb
section: openai
order: 55
level: A
title: Streaming Entropy with Online and Block-wise Updates
quick: >-
  original-structured-preparation-guide · Streaming Entropy with Online and
  Block-wise Updates
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
      https://www.1point3acres.com/interview/problems/1235a5c1-d4a0-534f-93a3-46eb764de3ff
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Streaming Entropy：逐项更新与整块合并

## 证据边界与练习题面

当前标题没有说明输入是类别样本还是 logits；另一个 UUID 已明确是 logits，因此这里按本地题库记录整理成**离散符号流**练习版，不声称是会员原文。实现 `update(symbol)`、`update_block(counts)` 和 `entropy(base=e)`；任意时刻返回经验分布 `p_x=count[x]/N` 的 `H=-Σ p_x log p_x`，不能保存完整样本序列，但允许保存每类计数。

例：依次加入 `A,A,B`，计数为 2、1，熵为 `-(2/3)ln(2/3)-(1/3)ln(1/3)≈0.636514`；再合并块 `{B:1,C:2}` 后应与逐项加入三次完全一致。

## 在线公式与复杂度

维护总数 `N`、`counts` 和 `S=Σ c log c`，则 `H=log N-S/N`。单次把某类从 `c` 改成 `c+1`，只需令 `S += (c+1)log(c+1)-c log c`；块合并对块内每个非零类做 `c -> c+d` 的同类差分，并令 `N += Σd`。两个块的熵不能直接相加，因为normalization分母及跨块同类都会变化。

单项期望 `O(1)`，含 `u` 个不同符号的块为 `O(u)`，查询 `O(1)`，空间 `O(U)`。若题目真要求类别域无界且严格 `O(1)` 空间，精确答案一般不可能，需要明确改成 sketch 近似。测试空流定义、单一类别熵 0、空块、负计数拒绝、对数底、极大 N 的浮点误差、块合并顺序，以及随机分块结果与离线重算一致。

块摘要至少要携带各类别计数；仅有 `(N,H)` 无法判断两块是否含相同符号，因此不能精确合并。多个 worker 可先各自产生 Counter，再按 key 相加并更新 `S`；Counter 合并具有结合律，适合树形归约。最终因浮点加法顺序不同出现微小误差时，应使用容差比较而非逐位相等。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1235a5c1-d4a0-534f-93a3-46eb764de3ff)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
