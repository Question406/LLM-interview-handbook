---
id: lc-125-valid-palindrome
section: two-pointers
order: 1
level: S
title: LC 125 · 验证回文串
quick: >-
  左右指针对撞：跳过非字母数字，比较时忽略大小写。全对上才是回文。时间 $O(n)$，额外空间
  $O(1)$。
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

## 题意

字符串 `s` 只保留字母和数字、并忽略大小写后，判断是否回文。

## 思路

不必先筛出新串。`l`、`r` 从两端往中间走：遇到非 `isalnum` 就跳过，再把两端转小写比较。不相等立刻失败；指针错开即成功。

先 `filter` 再反转要额外 $O(n)$ 空间。白板我会强调「原地对撞、跳过噪声字符」。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个字符最多被看两次。

## 边界

- 空串或只含标点：滤完没有字符，视为回文。
- 单字符恒真；全是数字也按字符对撞，`'0'` 和 `'O'` 不同。

## 追问

- **允许 $O(n)$ 额外空间？** 先筛出字母数字并转小写，再判断 `filtered == filtered[::-1]`。时间仍 $O(n)$，代码短、少踩 `l < r` 与内层跳过写乱的坑。面试若强调原地，还是对撞；这版当「先换正确性再换空间」的退路。注意 `isalnum` 含数字，别只留 `isalpha`。

```python
def isPalindrome(s):
    t = [ch.lower() for ch in s if ch.isalnum()]
    return t == t[::-1]
```

- **最多删一个字符能否变成回文（LC 680）？** 仍从两端对撞。全程相等就是真。第一次 `s[l] != s[r]` 时，两条路只试一次：删左看 `s[l+1:r]`，或删右看 `s[l:r-1]`，任一是回文即可。不能继续递归删第二个。时间 $O(n)$，空间 $O(1)$。这块容易栽：不相等时直接返回假，或两边都删再继续走。这题不允许删，LC 680 才允许一次。

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
