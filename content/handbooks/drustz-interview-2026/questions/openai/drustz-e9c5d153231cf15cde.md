---
id: drustz-e9c5d153231cf15cde
section: openai
order: 143
level: A
title: IP Address Iterator
quick: original-structured-preparation-guide · IP Address Iterator
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
      https://www.1point3acres.com/interview/problems/fd613e94-3523-45f5-b878-ba68b79cb16f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# IP Address Iterator：基础正向版本

## 证据边界

当前标题只写 IP Address Iterator，不能据此认定一定包含 reverse 或 CIDR；本地直接面经把正向迭代列为 Part 1、后两者列为后续部分。因此本篇只给完整正向版本，并把范围端点语义明确写出。

## 题面、接口与例子

实现 Python iterator protocol：

```python
it = IPV4Iterator("255.255.255.253")
list(it)  # ["255.255.255.253", "255.255.255.254", "255.255.255.255"]
```



输入是合法 IPv4 起点，每次 next 返回当前地址并前进一步；返回最大地址后，后续调用抛 `StopIteration`。按“从起点开始”的公开例子，本指南把起点包含在结果中，所以从 `255.255.255.255` 开始会返回一次再结束；若现场测试要求空序列，应以测试为准并说明差异。

## 解法

初始化时把四段解析成一个 0 到 `2^32-1` 的整数。next 检查 `current<=MAX`，通过位移和 `&255` 还原字符串，然后 `current+=1`。整数表示自然处理 `.255 -> 下一段进位`，比手动维护四个 octet 更少边界错误。`__iter__` 返回 self；不要提前构造从起点到最大地址的巨大列表。

循环不变量是 current 始终等于下一条待返回地址的整数值；成功返回后恰好加一，超过 MAX 后永远停止。这样端点只出现一次，也不会在四段进位时跳号。若需要多个独立遍历，应创建多个 iterator，不能共享可变 current。

## 复杂度与边界

构造解析固定四段为 `O(1)`，每次 next 为 `O(1)`，额外空间 `O(1)`；真正遍历 K 个地址不可避免为 `O(K)`。测试 `0.0.0.0`、最大地址、`192.168.0.255 -> 192.168.1.0`、结束后重复 next、段数错误、负数、256、空字符串、空段和前导零。还要确认 iterator 是否一次性、是否需 reset，以及无效输入抛何种异常。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/fd613e94-3523-45f5-b878-ba68b79cb16f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
