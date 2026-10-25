---
id: jd-lcs-cycle-list
section: coding
order: 190
level: B
title: 京东大模型算法实习：最长公共子序列和环形链表怎么写？
quick: "LCS 用 `dp[i][j]` 表示两条前缀的最长公共子序列长度，字符相同取左上角加一，不同取左边和上边的较大值。环形链表用快慢指针判环并找入口，也可以用 `HashSet` 记录访问过的节点。动手前先说清复杂度和边界。"
tags:
  - JD
  - Coding
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 京东大模型算法 实习面经 55min
    url: https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46
    type: candidate-first-hand
---

## 题目描述

完成两道独立函数题：求两字符串的最长公共子序列长度，以及判断单链表是否有环并定位入环节点。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `longest_common_subsequence(text1,text2)`、`has_cycle(head)` 和 `detect_cycle(head)`。字符串允许为空；链表节点含val/next，head可为None，节点值可重复。

### 输出与约束

LCS只需保持相对顺序，不要求连续，返回长度。`has_cycle`返回布尔值；`detect_cycle`返回原链表中首次进入环的节点对象，无环返回None。按节点身份判断，不按val判断，不能改变原next连接。

### 示例

```text
longest_common_subsequence("abcde","ace") -> 3
longest_common_subsequence("", "a") -> 0
链表3→2→0→-4，末节点next指回值为2的那个节点
has_cycle -> True，detect_cycle -> 该值为2的原节点对象。
```

## 解题思路与参考答案

两道都是经典题。LCS 用二维 DP，字符相同就从左上角加一，不同就取左边和上边的较大值；环形链表用快慢指针，相遇说明有环，再从头同步走一次就能找到入口。

这是京东大模型算法实习的一轮面试，原帖说一共 55 分钟，来自牛客候选人原帖，可信度 A，原话是**“算法题:最长公共子序列，环形链表”**。对应的是 1143 的 LCS 长度和 141/142 的环形链表。写之前问清环形链表要返回布尔还是入口节点，也别把子序列当成子串。京东零售岗另外考过非递归中序，见同公司的手撕卡。

## 思路

LCS 里 `dp[i][j]` 表示 $a[:i]$ 和 $b[:j]$ 的最长公共子序列长度。当前字符相等就取左上角的值 $+1$，否则取左边、上边的较大值，空串对应的边界是 $0$。比如 `"abcde"` 和 `"ace"`，a、c、e 依次对上，答案是 3。只求长度可以用滚动数组；要还原序列就保留二维表，从右下角回溯。

环形链表用 Floyd：慢指针每次走 $1$ 步，快指针走 $2$ 步，没环的话快指针会先走到末尾。只要布尔（141）的话，相遇就返回；要入口（142），相遇后把一个指针放回头，两个指针同步走，再相遇的地方就是入口。`HashSet` 也能判断有没有重复访问节点，但要 $O(n)$ 空间，面试先给 Floyd。

## 参考代码

```python
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def longest_common_subsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]


def has_cycle(head: Optional[ListNode]) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            p = head
            while p is not slow:
                p = p.next
                slow = slow.next
            return p
    return None


if __name__ == "__main__":
    assert longest_common_subsequence("abcde", "ace") == 3
    assert longest_common_subsequence("abc", "def") == 0

    a, b, c = ListNode(3), ListNode(2), ListNode(0)
    d = ListNode(-4)
    a.next, b.next, c.next, d.next = b, c, d, b
    assert has_cycle(a) is True
    assert detect_cycle(a) is b
    assert has_cycle(ListNode(1)) is False
    print("ok")
```

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert longest_common_subsequence("abcde", "ace") == 3` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

LCS 时间 $O(mn)$，滚动之后空间 $O(\min(m,n))$。Floyd 时间 $O(n)$、空间 $O(1)$；哈希判环时间 $O(n)$、空间 $O(n)$。

## 追问

**LCS 要测哪些边界？**
空串、没有公共字符、两串完全相等。

**改成最长公共子串呢？**
连续匹配时加一，一断开就归零。

**环形链表要测哪些情况？**
无环、环在头、环在尾、单节点自环。还要先问清返回 `bool` 还是入口。

**为什么第二次相遇的地方就是入口？**
设头到入口是 $a$、入口到相遇点是 $b$、环长 $c$，有 $a+b=k\cdot c$，所以再从头走 $a$ 步一定到入口。能讲清这一步比背公式加分。
