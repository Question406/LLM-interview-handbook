---
id: lc-30-substring-with-concatenation-of-all-words
section: sliding-window
order: 3
level: A
title: LC 30 · 串联所有单词的子串
quick: >-
  单词等长。按偏移 $0\ldots w-1$ 做词级滑窗：窗口凑齐 `words` 的多重集就记起点，某词超量则左缩。时间
  $O(|s|\cdot w)$。
tags:
  - Sliding Window
  - Hash
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 30. 串联所有单词的子串
    url: https://leetcode.cn/problems/substring-with-concatenation-of-all-words/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`words` 中单词等长。找出 `s` 里所有起点，使得从该处起、连续拼接 `words` 的某个排列（每个词用且仅用一次）。

## 思路

设词长 $w$。合法子串长度固定为 $n\cdot w$，且按 $w$ 切词。对每个偏移 `offset` 在 $0\ldots w-1$，以 $w$ 为步长滑窗：维护窗口内词频。遇到不在 `need` 里的词就整窗清空；某词超过需求则从左边弹出。窗口词数等于 $n$ 时，左端就是一个答案。

不要枚举排列。面试先讲「等长才能按词滑」。

## 参考代码

```python
from collections import Counter
from typing import List


def findSubstring(s: str, words: List[str]) -> List[int]:
    if not s or not words:
        return []
    w = len(words[0])
    n = len(words)
    need = Counter(words)
    ans: List[int] = []
    for offset in range(w):
        left = offset
        window: Counter[str] = Counter()
        count = 0
        for right in range(offset, len(s) - w + 1, w):
            word = s[right : right + w]
            if word not in need:
                window.clear()
                count = 0
                left = right + w
                continue
            window[word] += 1
            count += 1
            while window[word] > need[word]:
                left_word = s[left : left + w]
                window[left_word] -= 1
                count -= 1
                left += w
            if count == n:
                ans.append(left)
    return ans


if __name__ == "__main__":
    assert findSubstring("barfoothefoobarman", ["foo", "bar"]) == [0, 9]
    assert findSubstring("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]) == []
    assert findSubstring("barfoofoobarthefoobarman", ["bar", "foo", "the"]) == [6, 9, 12]
    print("ok")
```

## 复杂度

每个起点至多当一次词首，切词 $O(w)$，时间 $O(|s|\cdot w)$。空间 $O(|words|)$。

## 边界

- `s` 短于 $n\cdot w$ 直接空答案。
- `words` 含重复：`need` 必须用多重集，不能去重。
- 中间插入不在词典里的词：当前窗口作废，`left` 跳到该词之后。

## 追问

- **词长不等怎么办？** 不能按固定步长 $w$ 切。从每个起点做 DFS：枚举还没用完的词，若 `s` 从当前位置 `startswith` 该词就扣一次计数往下搜，全部用完即命中。`need` 要回溯加回去。时间最坏 $O(|s|\cdot n\cdot n!)$，只在 $n$ 很小或词很稀疏时能过。也可用 Trie 把 `words` 插进去，按字符走，遇到词尾就进入下一层；本质仍是搜索。面试先讲清「等长才能词级滑窗」，不等长不要硬套本题代码。

```python
from collections import Counter

def findSubstringUnequal(s, words):
    need0 = Counter(words)
    n, ans = len(words), []

    def dfs(i, left, need):
        if left == 0:
            return True
        for w in list(need):
            if need[w] and s.startswith(w, i):
                need[w] -= 1
                if dfs(i + len(w), left - 1, need):
                    need[w] += 1
                    return True
                need[w] += 1
        return False

    for i in range(len(s)):
        if dfs(i, n, need0.copy()):
            ans.append(i)
    return ans
```

- **只要判断是否存在一个起点？** 算法不变，`count == n` 时立刻 `return True`，不必收集全部下标。最坏仍可能扫完整串，复杂度还是 $O(|s|\cdot w)$，只是最好情况提前退出。空 `words` 或 `s` 不够长先剪枝。不要为了「存在性」改成枚举排列去 `s.find`，排列数是 $n!$，比滑窗差一个量级。
