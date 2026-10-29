---
id: meta-word-selection-letter-coverage
section: meta
order: 921
level: A
title: "Meta AI Coding：选择互不共用字母的 words，最大化 letter coverage"
quick: "我会先确认优化的是总字母数。因为每个选中字母只能出现一次，score 就是最终 mask 中 1 的数量，冲突检查只需要做一次 bitwise AND。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta AI Coding：选择互不共用字母的 words，最大化 letter coverage"
    url: "https://landthelab.com/companies/meta"
    type: secondary
---

## 题目描述

来源：Land the Lab 的 Meta 目录公开了 choose words / cover the most letters 题型；本题明确优化 letter 数，返回值与 tie-breaking 由手册设定。

### 输入、接口与规则

实现 `max_letter_coverage(words) -> (score, indices)`。输入最多 20 个非空 lowercase ASCII words。可以选择任意下标集合，每个下标最多一次。一个 word 内部或不同所选 words 之间，都不能重复使用同一个字母；含内部重复字母的 word 不可选。

score 为选中字母总数，indices 为升序下标列表。优化 score，而不是 word 数。若多个选择同分，返回 indices 按 Python tuple 的 lexicographic order 最小的一组；允许空集合，空输入返回 `(0,[])`。不修改输入。需给出实际选中的下标，不能只返回最大长度，并说明 26-bit mask 的冲突检测方式。

### 输入输出示例

```text
words=["ab","cd","a","b","c","d"] -> (4,[0,1])。
[2,3,4,5] 也覆盖 4 个字母，但 tie-breaking 选择 [0,1]。
words=["aa","bb"] -> (0,[])。
```

## 回答思路

> **Situation / Task：** 目标是最多不同字母，多个短 words 不一定优于一个长 word。  
> **Approach / Why：** 每个 word 编成 bitmask，用 DP 记录可达 mask 的最佳下标 tuple。  
> **Result / Check：** 检查 word 内重复、words 之间冲突、空集合与同分选择。

## 解题思路与参考答案

我会先确认优化的是总字母数。因为每个选中字母只能出现一次，score 就是最终 mask 中 1 的数量，冲突检查只需要做一次 bitwise AND。

DP 的每个状态保存一个已覆盖字母 mask 和对应下标。遍历下一个 word 时，只从上一轮状态扩展，避免重复使用当前 word。同一个 mask 只保留 lexicographically 最小的方案，最后选 bit count 最大的状态。

### 完整参考实现

```python
def max_letter_coverage(words):
    states = {0: ()}
    for i, word in enumerate(words):
        mask = 0
        for char in word:
            bit = 1 << (ord(char) - 97)
            if mask & bit:
                break
            mask |= bit
        else:
            for old, indices in list(states.items()):
                if old & mask:
                    continue
                new = old | mask
                candidate = indices + (i,)
                if new not in states or candidate < states[new]:
                    states[new] = candidate
    best = min(states, key=lambda m: (-m.bit_count(), states[m]))
    return best.bit_count(), list(states[best])
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
from itertools import combinations
from random import Random


def brute(words):
    valid = []
    for bits in range(1 << len(words)):
        ids = tuple(i for i in range(len(words)) if bits >> i & 1)
        text = ''.join(words[i] for i in ids)
        if len(set(text)) == len(text):
            valid.append((len(text), ids))
    score, ids = min(valid, key=lambda item: (-item[0], item[1]))
    return score, list(ids)


assert max_letter_coverage(['ab', 'cd', 'a', 'b', 'c', 'd']) == (4, [0, 1])
assert max_letter_coverage(['aa', 'bb']) == (0, [])
rng = Random(19)
for _ in range(100):
    words = [''.join(rng.choices('abcde', k=rng.randint(1, 3))) for _ in range(7)]
    assert max_letter_coverage(words) == brute(words)
print('letter coverage tests passed')
```

## 复杂度与追问

设可达 masks 数为 S，时间约 `O(N*S*N)`，这里包含复制与比较下标 tuples 的成本；空间约 `O(S*N)`。S 最坏呈指数增长，本题限制 N≤20。追问可用 branch-and-bound，但需证明剪枝不会丢失最优解。
