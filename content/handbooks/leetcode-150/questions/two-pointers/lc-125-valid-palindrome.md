---
id: lc-125-valid-palindrome
section: two-pointers
order: 1
level: S
title: LC 125 · 验证回文串
quick: "左右指针从两端对撞，跳过非字母数字的字符，比较时忽略大小写，全对上就是回文。不用先筛出新串，所以时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Two Pointers
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 125. 验证回文串
    url: https://leetcode.cn/problems/valid-palindrome/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定字符串 `s`，忽略所有非英文字母、非数字字符，并把字母大小写视为相同，判断剩余字符序列是否为回文。回文表示从左向右与从右向左读得到相同序列；清理后没有字符时，也视为回文。

### 输入与输出

实现 `isPalindrome(s) -> bool`，返回 True 或 False。原字符串中的空格和标点不会参与比较，不需要返回清理后的字符串。

### 约束

- `1 <= len(s) <= 2 * 10^5`。
- 输入只包含可打印的 ASCII 字符。

### 示例

```text
输入：s = "A man, a plan, a canal: Panama"
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/valid-palindrome/description/)

## 解题思路与参考答案

## 题意

字符串 `s` 只保留字母和数字、并忽略大小写后，判断是否回文。

## 思路

我会原地用左右指针对撞，不先筛出新串。`l`、`r` 从两端往中间走，遇到不满足 `isalnum` 的字符就跳过，然后把两端都转成小写比较。不相等立刻返回假，两个指针错开就是回文。

拿 `"race a car"` 看。两端的 `r` 和 `r` 相等，`a` 和 `a` 相等，`c` 和 `c` 相等；右边接下来是空格，跳过，于是变成 `e` 对 `a`，对不上，返回假。

先 `filter` 再反转也能做，只是要额外 $O(n)$ 空间。

## 参考代码

```python
def isPalindrome(s: str) -> bool:
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum():
            l += 1
        while l < r and not s[r].isalnum():
            r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l += 1
        r -= 1
    return True


if __name__ == "__main__":
    assert isPalindrome("A man, a plan, a canal: Panama") is True
    assert isPalindrome("race a car") is False
    assert isPalindrome(" ") is True
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isPalindrome("A man, a plan, a canal: Panama") is True
assert isPalindrome("race a car") is False
assert isPalindrome(" ") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个字符最多被看两次。

## 边界

空串或者只含标点时，滤完没有字符，算回文。

单个字符一定是回文。全是数字也按字符对撞，`'0'` 和 `'O'` 是不同的字符。

## 追问

**允许 $O(n)$ 额外空间呢？**
那就先筛出字母数字并转小写，再判断 `filtered == filtered[::-1]`。时间仍是 $O(n)$，代码短，也不容易把 `l < r` 和内层跳过写乱。面试要求原地的话还是写对撞，这一版当作先保证正确、再优化空间的退路。另外 `isalnum` 包含数字，别只留 `isalpha`。

```python
def isPalindrome(s):
    t = [ch.lower() for ch in s if ch.isalnum()]
    return t == t[::-1]
```

**最多删一个字符能不能变成回文（LC 680）？**
还是从两端对撞，全程相等就是真。第一次遇到 `s[l] != s[r]` 时，两条路各试一次：删左边看 `s[l+1:r]`，或者删右边看 `s[l:r-1]`，任一是回文就行，不能继续递归去删第二个。时间 $O(n)$，空间 $O(1)$。容易栽的地方是不相等时直接返回假，或者两边都删了再继续走。本题不允许删字符，LC 680 才允许删一次。

```python
def validPalindrome(s):
    def check(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1
            r -= 1
        return True

    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]:
            return check(l + 1, r) or check(l, r - 1)
        l += 1
        r -= 1
    return True
```
