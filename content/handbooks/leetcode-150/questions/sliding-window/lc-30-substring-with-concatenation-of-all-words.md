---
id: lc-30-substring-with-concatenation-of-all-words
section: sliding-window
order: 3
level: A
title: LC 30 · 串联所有单词的子串
quick: >-
  单词等长，所以能按词滑窗：对偏移 $0\ldots w-1$ 各滑一遍、步长 $w$，窗口词频凑齐 `words`
  的多重集就记下起点，某个词超量就左缩。不用枚举排列，时间 $O(|s|\cdot w)$。
tags:
  - Sliding Window
  - Hash
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 30. 串联所有单词的子串
    url: 'https://leetcode.cn/problems/substring-with-concatenation-of-all-words/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定字符串 s 和由等长非空单词组成的列表 words，找出 s 中所有符合要求的连续片段的起点：片段必须由 words 中的所有单词以某种顺序直接拼接而成，每个列表位置上的单词恰好使用一次，不能插入其他字符或空隙。words 可以包含重复单词，重复次数也必须匹配。

### 输入与输出

实现 `findSubstring(s: str, words: List[str]) -> List[int]`。返回所有合法片段的 0 基起始下标，顺序不限。每个候选片段长度固定为单词长度乘单词数量。

### 约束

- `1 <= len(s) <= 10^4`，`1 <= len(words) <= 5000`。
- 每个单词长度相同，长度为 1 到 30；s 和所有单词只含小写英文字母。

### 示例

```text
输入：s = "barfoothefoobarman", words = ["foo","bar"]
输出：[0,9]
```

起点 0 对应 `barfoo`，起点 9 对应 `foobar`；两者都恰好使用 foo 与 bar 一次。

## 解题思路与参考答案

## 题意

`words` 中单词等长。找出 `s` 里所有起点，使得从该处起、连续拼接 `words` 的某个排列（每个词用且仅用一次）。

## 思路

因为所有单词等长，我会做以词为单位的滑动窗口，不去枚举排列。设词长 $w$、词数 $n$，合法子串长度固定是 $n\cdot w$，而且一定能按 $w$ 切成词。等长是能按词滑的前提，这点我会先讲。

起点按对 $w$ 取余只有 $w$ 种，所以对每个偏移 `offset`（$0\ldots w-1$）各做一遍步长为 $w$ 的滑窗，维护窗口内的词频。切出来的词不在 `need` 里，就整窗清空，左端跳到这个词后面；某个词超过需求，就从左边一个词一个词地弹出。窗口词数等于 $n$ 时，左端就是一个答案。

拿 `s="barfoothefoobarman"`、`words=["foo","bar"]` 看，$w=3$。偏移 $0$ 这一轮切出 `bar foo the foo bar man`。`bar foo` 凑齐，记下起点 $0$；遇到 `the` 不在 vocabulary 里，窗口清空；接着 `foo bar` 又凑齐，起点是 $9$。偏移 $1$、$2$ 切不出有效的词，答案是 `[0, 9]`。

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
    assert (
        findSubstring("wordgoodgoodgoodbestword", ["word", "good", "best", "word"])
        == []
    )
    assert findSubstring("barfoofoobarthefoobarman", ["bar", "foo", "the"]) == [
        6,
        9,
        12,
    ]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert findSubstring("barfoothefoobarman", ["foo", "bar"]) == [0, 9]
assert findSubstring("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]) == []
assert findSubstring("barfoofoobarthefoobarman", ["bar", "foo", "the"]) == [6, 9, 12]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每个起点至多当一次词首，切一个词是 $O(w)$，所以时间 $O(|s|\cdot w)$。空间 $O(|words|)$。

## Edge Cases

`s` 比 $n\cdot w$ 短，直接返回空答案。

`words` 里有重复词时，`need` 必须按多重集计数，去重就错了。

中间插进一个词典里没有的词，当前窗口作废，`left` 跳到这个词之后。

## 追问

**词长不等怎么办？**
那就没法按固定步长 $w$ 切了，这题的代码别硬套。可以从每个起点做 DFS：枚举还没用完的词，如果 `s` 在当前位置 `startswith` 这个词，就扣一次计数往下搜，全部用完就算命中，回溯时把 `need` 加回去。最坏时间 $O(|s|\cdot n\cdot n!)$，只在 $n$ 很小或词很稀疏时能过。也可以把 `words` 插进 Trie，按字符走，遇到词尾就进下一层，本质还是搜索。

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

**只要判断存不存在一个起点呢？**
算法不变，`count == n` 时立刻 `return True`，不用收集全部下标。最坏还是可能扫完整串，复杂度仍是 $O(|s|\cdot w)$，只是最好情况能提前退出。空 `words` 或 `s` 不够长可以先剪枝。别为了判断存在性改成枚举排列再 `s.find`，排列有 $n!$ 个，比滑窗差一个量级。
