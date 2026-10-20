---
id: p3a-xai-parallel-integer-sort
section: xai
order: 617
level: A
title: "xAI：并行整数排序：分区、worker 和合并"
quick: "把数组切成多块交给多个线程分别排序，再用 k 路归并合成结果；要说明小数据时并行开销和 Python GIL 会让多线程拿不到真实加速。"
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

## 题目

用多线程实现整数排序，不能只调用一次单线程的 `sort`。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

标准做法是分治：把数组切成 p 块，每个线程排一块，再把 p 个有序块归并成一个结果。归并可以用最小堆做 k 路归并；块数多时也可以两两分层归并，每一层的多对归并本身又能并行。

面试中值得主动讨论性能：

- 线程启动、数据拷贝和最后的归并都有开销，数据量小的时候并行版可能比单线程还慢，最好实际测一下。
- 在 CPython 里，线程受 GIL 限制，纯 Python 代码的排序不会因为多线程变快。要分清「题目要求用线程实现」和「真的拿到 CPU 加速」是两回事。真想加速可以换多进程，或者用 C++/Java 这类线程能真正并行的语言。

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
