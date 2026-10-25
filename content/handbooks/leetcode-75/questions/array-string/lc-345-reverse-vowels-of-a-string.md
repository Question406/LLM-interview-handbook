---
id: lc-345-reverse-vowels-of-a-string
section: array-string
order: 5
level: A
title: LC 345 · 反转字符串中的元音字母
quick: >-
  用对撞双指针：转成字符数组，左右指针各自跳过非元音，两边都停在元音上就交换再内收，元音集合要含大写。时间 $O(n)$，额外空间 $O(n)$，因为 Python 字符串不可变。
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

## 题目描述

给定字符串 s，只把其中所有元音字母出现的先后顺序反转，其他字符的位置和值保持不变。元音为 a、e、i、o、u，大小写形式都算元音；反转时字符的大小写随该字符一起移动。

### 接口与输出

实现 `reverseVowels(s: str) -> str`。返回与输入等长的新字符串，不能反转整个字符串或改动非元音字符。

### 合法输入与约束

`1 <= len(s) <= 300000`，s 由可打印 ASCII 字符组成。元音可以重复，也可以没有元音。

### 示例

```text
输入：s = "IceCreAm"
输出："AceCreIm"
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/reverse-vowels-of-a-string/description/)。

## 解题思路与参考答案

## 题意

只反转字符串 `s` 中元音字母的顺序，其他字符位置不变。元音是 `a e i o u`，大小写都算。长度在 $[1, 3\cdot 10^5]$，由可打印 ASCII 字符组成。

## 思路

我会用对撞双指针，每个字符最多被每个指针看一次，一遍就做完。`l` 从左找下一个元音，`r` 从右找下一个元音，`l < r` 时交换，然后两边各进一步。开口先提一句，元音集合要把大写也放进去。

拿 `"IceCreAm"` 走一遍：`l` 停在 `I`，`r` 停在 `A`，交换；接着 `l` 停在第一个 `e`，`r` 往左停在第二个 `e`，交换后不变；两个指针相遇就结束，得到 `"AceCreIm"`。

也可以先把所有元音按顺序取出来，再倒序填回元音位置，同样 $O(n)$，只是要多存一份元音列表。我会写双指针。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert reverseVowels("IceCreAm") == "AceCreIm"
assert reverseVowels("leetcode") == "leotcede"
assert reverseVowels("hello") == "holle"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，两个指针合计走 $n$ 步。额外空间 $O(n)$，是那份字符数组；换成字符数组可变的语言就是 $O(1)$。

## 边界

- 没有元音时，内层循环让 `l`、`r` 相遇，最后一次交换是自己和自己，结果不变。
- 只有一个元音，同样不动。
- 大小写混合如 `"aA"`，集合里必须有大写，否则不会交换。

## 追问

**只反转字母、其他字符留在原位（LC 917）怎么写？**
同一个模板，把「是否元音」换成 `isalpha()`。这题不在本手册里，但面试常作为换皮题出现，把判定函数抽出来就能复用。

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
