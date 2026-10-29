---
id: lc-242-valid-anagram
section: hashmap
order: 4
level: S
title: LC 242 · 有效的字母异位词
quick: >-
  长度不等直接返回否。开 26 个桶，对 $s$ 的字符加一、对 $t$ 的字符减一，最后全为 $0$ 就是异位词，时间 $O(n)$；排序后比较也行，时间
  $O(n\log n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 242. 有效的字母异位词
    url: 'https://leetcode.cn/problems/valid-anagram/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两个字符串，判断它们是否是字母异位词：每一种字母在两个字符串中出现的次数都完全相同，只允许字符排列顺序不同。字符种类相同但次数不同不算异位词。

### 输入与输出

实现 `isAnagram(s, t) -> bool`，符合条件返回 True，否则返回 False。

### 约束与约定

- `1 <= len(s),len(t) <= 50000`。
- 本题输入只包含小写英文字母。

### 示例

```text
输入：s = "anagram", t = "nagaram"
输出：true
```

anagram 与 nagaram 的字母及各自出现次数相同。

[官方原题与完整题面](https://leetcode.com/problems/valid-anagram/description/)。

## 解题思路与参考答案

## 题意

判断 $t$ 是不是 $s$ 的字母异位词，也就是字符种类和次数完全相同，顺序可以不同。默认只有小写字母。

## 思路

我会用哈希计数，异位词只关心每个字母出现几次。先比长度剪枝，再开一个 26 维数组，对 $s$ 的字符加一、对 $t$ 的字符减一，最后全为零就是异位词。

比如 `anagram` 和 `nagaram`，每个字母加减之后正好抵消，是真；`aacc` 和 `ccac` 长度一样，但 `a` 和 `c` 的次数对不上，桶里会留下非零，不是异位词。

排序后比较也行，少写几行，但多一个 $\log n$。白板上我会先问清字符集：只有小写就用数组，否则用哈希表。

## 参考代码

```python
def isAnagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    cnt = [0] * 26
    for a, b in zip(s, t):
        cnt[ord(a) - 97] += 1
        cnt[ord(b) - 97] -= 1
    return all(c == 0 for c in cnt)


if __name__ == "__main__":
    assert isAnagram("anagram", "nagaram") is True
    assert isAnagram("rat", "car") is False
    assert isAnagram("a", "ab") is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isAnagram("anagram", "nagaram") is True
assert isAnagram("rat", "car") is False
assert isAnagram("a", "ab") is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。排序写法的时间是 $O(n\log n)$。

## Edge Cases

空串对空串是真；长度不等直接是假。只要有一个字符不同，或者某个字母次数差一，26 个桶扫完就会留下非零。

## 追问

**字符集是 Unicode 或任意字符呢？**
26 个桶会越界，改用哈希表对 $s$ 加、$t$ 减，或者直接 `Counter(s) == Counter(t)`。还是先比长度，不相等必假。时间 $O(n)$，空间 $O(|\Sigma|)$，$\Sigma$ 是实际出现过的字符。大小写敏感要先问清，如果忽略大小写，两边先 `.lower()`。排序后比串是 $O(n\log n)$，别说成 $O(n)$。

```python
from collections import Counter


def isAnagram(s, t):
    return len(s) == len(t) and Counter(s) == Counter(t)
```

**要把所有异位词分组（LC 49）呢？**
给每个词做一个可哈希的签名，签名相同的放进同一个桶。小写字母用计数元组 `tuple(cnt)`，总时间 $O(nk)$；字母表很大就用排序串 `''.join(sorted(s))`，时间 $O(nk\log k)$。`eat`/`tea`/`ate` 在同一组。别用质数乘积当签名，次数一大就溢出。单独一张卡 `lc-49-group-anagrams`。

```python
from collections import defaultdict


def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1
        groups[tuple(cnt)].append(s)
    return list(groups.values())
```
