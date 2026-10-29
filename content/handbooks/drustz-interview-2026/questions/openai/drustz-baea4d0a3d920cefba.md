---
id: drustz-baea4d0a3d920cefba
section: openai
order: 82
level: A
title: IP address to CIDR blocks (iterative/range-based)
quick: >-
  original-structured-preparation-guide · IP address to CIDR blocks
  (iterative/range-based)
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
      https://www.1point3acres.com/interview/problems/1beea68a-2947-4257-ade0-7714ac9f43d3
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# IP 地址区间转最少 CIDR Blocks

## 题目

给定起始 IPv4 地址和连续地址数量 `n`，用尽可能少的 CIDR 块精确覆盖该区间，不能遗漏或超出。前置部分可能要求 IPv4 与 32 位整数互转及区间迭代。

## 贪心

每轮选择从当前整数地址 `x` 开始、同时满足“地址对齐”和“不超过剩余数量”的最大 2 的幂区块。`x & -x` 给出对齐允许的最大块；再不断减半直到不超过 `n`。

```python
def ip_to_int(ip):
    value = 0
    for part in map(int, ip.split(".")):
        value = (value << 8) | part
    return value


def int_to_ip(value):
    return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))


def ip_to_cidr(ip, n):
    x, answer = ip_to_int(ip), []
    while n:
        block = (x & -x) if x else (1 << 32)
        while block > n:
            block >>= 1
        prefix = 32 - (block.bit_length() - 1)
        answer.append(f"{int_to_ip(x)}/{prefix}")
        x += block
        n -= block
    return answer
```



## 复杂度与边界

输出 `k` 个块时，时间 `O(k)`、额外空间 `O(1)`。`x=0` 的 lowbit 需特判；`n=1` 为 `/32`；起点未对齐时先输出较小块；不得越过 `2^32-1`。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1beea68a-2947-4257-ade0-7714ac9f43d3)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
