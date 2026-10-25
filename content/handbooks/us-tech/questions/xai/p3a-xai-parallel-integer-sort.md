---
id: p3a-xai-parallel-integer-sort
section: xai
order: 617
level: A
title: "xAI：并行整数排序：分区、worker 和合并"
quick: "我会把数组分成多块交给 worker 排序，再用 k 路归并得到全局升序，保留重复元素且不改输入。小数据可能被线程启动、复制和归并开销拖慢，CPython 的 GIL 也限制真实加速；换多进程或语言后仍要实际测量。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · parallel-integer-sort"
    url: https://www.1point3acres.com/interview/problems/company/xai/parallel-integer-sort
    type: secondary
---

## 题目描述

实现多线程整数排序接口，返回保留所有重复值的升序新列表，并支持线程数大于元素个数的情况。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `parallel_sort(nums,workers=4) -> list[int]` 输入整数列表与正整数线程数，返回保留重复元素的升序新列表，不修改输入。
- nums 最多1000000项，允许空列表，workers 可以大于元素数。要求使用多个工作线程处理排序任务，各工作任务内部允许内置 sorted；不承诺在 Python 下带来 CPU 加速。

### 输入输出示例

```text
parallel_sort([3, 1, 2, 1], workers=2) -> [1, 1, 2, 3]
parallel_sort([2, 1], workers=8)       -> [1, 2]
```

## 解题思路与参考答案

我会分块并行排序，再用 k 路归并拼成全局有序结果。例如 `[3, 1, 2, 1]` 分给两个 worker，各自排好后归并成 `[1, 1, 2, 3]`，重复值保留。Python 版本用来说明并发结构，不能据此承诺 CPU 加速。

## 题目

用多线程实现整数排序，不能只调用一次单线程的 `sort`。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

把数组切成 p 块后，每个线程独立排序一块，最后用最小堆做 k 路归并。若最后的归并成了瓶颈，可以改为两两分层归并，同一层的多对归并也能并行。

面试中值得主动讨论性能：

- 线程启动、数据拷贝和最后的归并都有开销，数据量小的时候并行版可能比单线程还慢，最好实际测一下。
- 在 CPython 里，线程受 GIL 限制，纯 Python 代码的排序不会因为多线程变快。满足线程实现的要求之后，还要另测墙钟时间，确认是否真的得到 CPU 加速。真想加速可以换多进程，或者用 C++/Java 这类线程能真正并行的语言。

如果面试官允许用别的语言，可以顺便讲一下整数排序还能用基数排序，按位分桶本身也容易并行化。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `parallel_sort(nums, workers=4) -> list[int]`：把 `nums` 分块交给多个线程排序，再归并成升序的新列表，不修改输入。
- `workers` 至少为 1，否则抛 `ValueError`；$n \le 10^6$。
- 每块内部可以直接用内置 `sorted`。Python 版本只考察并发结构，不承诺 CPU 加速。

### 输入输出示例

```text
parallel_sort([3, 1, 2, 1], workers=2) -> [1, 1, 2, 3]
parallel_sort([2, 1], workers=8)       -> [1, 2]
```

### 解题思路与正确性

`split_chunks` 按 $\lceil n / p \rceil$ 切块，所以块数不超过 `workers`，元素一个不少。每个线程把自己那块排好；线程池的 `with` 块退出时会等所有任务完成，不会有没排完的块漏进归并。

`heapq.merge` 每次从各块当前的首元素里取最小的一个。因为每块都是有序的，取出的序列也就全局有序，重复元素原样保留。

### 完整参考实现（Python 3）

```python
from concurrent.futures import ThreadPoolExecutor
from heapq import merge
from math import ceil


def split_chunks(nums, parts):
    """按 ceil(len / parts) 切块，最多 parts 块，只有最后一块可能更短。"""
    size = ceil(len(nums) / parts)
    return [nums[start:start + size] for start in range(0, len(nums), size)]


def parallel_sort(nums, workers=4):
    """分块后由多个线程各自排序，再 k 路归并；返回新列表，不修改输入。"""
    if workers < 1:
        raise ValueError(f"workers must be at least 1: {workers}")
    if not nums:
        return []
    chunks = split_chunks(nums, workers)
    # with 块退出时会等所有线程结束，所以 sorted_chunks 里每块都已排好
    with ThreadPoolExecutor(max_workers=workers) as pool:
        sorted_chunks = list(pool.map(sorted, chunks))
    # heapq.merge 每次取各块当前最小的首元素
    return list(merge(*sorted_chunks))
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert parallel_sort([3, 1, 2, 1], 2) == [1, 1, 2, 3]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
import random

def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 题面示例，含重复值
assert parallel_sort([3, 1, 2, 1], 2) == [1, 1, 2, 3]

# 随机输入与内置 sorted 对照，并检查输入没被修改
rng = random.Random(4)
for n in (0, 1, 7, 1000):
    nums = [rng.randrange(-20, 20) for _ in range(n)]
    original = nums[:]
    assert parallel_sort(nums, 3) == sorted(nums)
    assert nums == original

# 线程数多于元素数
assert parallel_sort([2, 1], 8) == [1, 2]

expect_value_error(parallel_sort, [1], 0)
```

### 复杂度与追问

设元素数为 n、块数为 p。各块排序的总工作量是 $O(n \log(n/p))$，k 路归并是 $O(n \log p)$，合起来 $O(n \log n)$；额外空间 O(n)。

- 为什么 Python 多线程跑不快？CPython 的 GIL 让同一时刻只有一个线程执行 Python 字节码，墙钟时间基本不降。换成 `ProcessPoolExecutor` 可以真正用多核，但每块数据要序列化传给子进程，数据量不够大时这部分开销会吃掉收益。
- 最后的归并是单线程的，会不会成瓶颈？会。可以改成分层两两归并，每层的多对归并并行做；或者先按值域切分（类似样本排序），让每个线程负责一个值区间，各段排好后直接拼接，不需要归并。
