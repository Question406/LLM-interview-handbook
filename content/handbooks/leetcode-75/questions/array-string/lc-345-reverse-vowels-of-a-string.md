---
id: lc-345-reverse-vowels-of-a-string
section: array-string
order: 5
level: A
title: LC 345 · 反转字符串中的元音字母
quick: >-
  转成字符数组，左右指针各自跳过非元音，两边都停在元音上就交换再内收。元音含大小写。时间 $O(n)$，额外空间
  $O(n)$（Python 字符串不可变）。
tags:
  - String
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 345. Reverse Vowels of a String
    url: https://leetcode.com/problems/reverse-vowels-of-a-string/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

只反转字符串 `s` 中元音字母的顺序，其他字符位置不变。元音是 `a e i o u`，大小写都算。长度在 $[1, 3\cdot 10^5]$，由可打印 ASCII 字符组成。

## 思路

对撞双指针：`l` 从左找下一个元音，`r` 从右找下一个元音，`l < r` 时交换，然后两边各进一步。每个字符最多被每个指针看一次。

也可以先把所有元音按顺序取出来，再倒序填回元音位置，同样 $O(n)$，但要多存一份元音列表。我会写双指针，顺带提醒元音集合要包含大写。

## 参考代码

```python
def reverseVowels(s: str) -> str:
    vowels = set("aeiouAEIOU")
    a = list(s)
    l, r = 0, len(a) - 1
    while l < r:
        while l < r and a[l] not in vowels:
            l += 1
        while l < r and a[r] not in vowels:
            r -= 1
        a[l], a[r] = a[r], a[l]
        l += 1
        r -= 1
    return "".join(a)


if __name__ == "__main__":
    assert reverseVowels("IceCreAm") == "AceCreIm"
    assert reverseVowels("leetcode") == "leotcede"
    assert reverseVowels("hello") == "holle"
    assert reverseVowels("bcd") == "bcd"
    assert reverseVowels("a") == "a"
    assert reverseVowels("aA") == "Aa"
    print("ok")
```

## 复杂度

时间 $O(n)$，两个指针合计走 $n$ 步。额外空间 $O(n)$，是字符数组；换成可变字符数组的语言就是 $O(1)$。

## 边界

- 没有元音：内层循环让 `l`、`r` 相遇，最后一次交换是自己和自己，结果不变。
- 只有一个元音：同样不动。
- 大小写混合如 `"aA"`：必须把大写放进集合，否则不会交换。

## 追问

- **只反转字母、其他字符留在原位（LC 917）？** 同一个模板，把「是否元音」换成 `isalpha()`。不在本手册里，但面试常作为换皮题出现，判定函数抽出来即可复用。

```python
def reverseOnlyLetters(s):
    a = list(s)
    l, r = 0, len(a) - 1
    while l < r:
        if not a[l].isalpha():
            l += 1
        elif not a[r].isalpha():
            r -= 1
        else:
            a[l], a[r] = a[r], a[l]
            l += 1
            r -= 1
    return "".join(a)
```
