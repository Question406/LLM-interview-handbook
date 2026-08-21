---
id: jd-lcs-cycle-list
section: coding
order: 190
level: B
title: 京东大模型算法实习：最长公共子序列和环形链表怎么写？
quick: >-
  LCS 用 $dp[i][j]$：相等则对角 $+1$，否则取左/上最大。环形链表用快慢指针相遇再找入口，或
  `HashSet` 判访。两题都要先讲复杂度再写边界。
tags:
  - JD
  - Coding
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 京东大模型算法 实习面经 55min
    url: https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46
    type: candidate-first-hand
---

## 真题 / 考点说明

- 公司：京东
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：原帖 55 分钟一轮
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“算法题:最长公共子序列，环形链表”**

两道经典题连问：1143 LCS 长度，141/142 环形链表。写代码前问清环形链表返回布尔还是入口节点。注意是子序列不是子串。零售岗另有非递归中序，见同公司手撕卡。

## 思路

LCS：`dp[i][j]` 为 $a[:i]$ 与 $b[:j]$ 的 LCS。相等走对角 $+1$，否则取左/上最大。空串边界为 $0$。只要长度可滚一维；还原序列从右下沿相等格子回溯。

环形链表（Floyd）：慢走 $1$、快走 $2$。无环则快指针先空。相遇后再把一个指针放回头，两指针同步走，再相遇处即入口（142）。只要布尔（141）相遇即可返回。`HashSet` 也能判访，但要 $O(n)$ 空间，面试先给 Floyd。

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

## 复杂度

- LCS：时间 $O(mn)$，滚动后空间 $O(\min(m,n))$。
- Floyd：时间 $O(n)$，空间 $O(1)$。哈希判环时间 $O(n)$、空间 $O(n)$。

## 边界与追问

1. LCS：空串、无公共、整串相等。追问子串：连续匹配加一，断开归零。
2. 环：无环、环在头、环在尾、单节点自环。问清返回 `bool` 还是入口。
3. 追问「为何第二次相遇是入口」：设头到入口 $a$、入口到相遇 $b$、环长 $c$，有 $a+b=k\cdot c$，再从头走 $a$ 步必到入口。讲清比背公式加分。
