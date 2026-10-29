---
id: xai-double-base-palindrome-enumeration
section: xai
order: 938
level: A
title: "xAI：判断 decimal / binary palindrome，并按序生成前 K 个"
quick: "我会先把两个接口对零的规则说清楚，避免 predicate 和生成函数看起来矛盾。生成时不必测试所有正整数，只构造 decimal palindrome 候选。"
companies:
  - xai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：xAI：判断 decimal / binary palindrome，并按序生成前 K 个"
    url: "https://aceoffer.app/interviews/xai_palindromes_decimal_binary"
    type: secondary
---

## 题目描述

来源：AceOffer 公开目录列出 decimal and binary palindromes。下面先实现 predicate，再增加按数值升序生成前 K 个的练习接口。

### 输入、接口与规则

实现 `is_double_palindrome(n)->bool` 与 `first_double_palindromes(k)->list[int]`。n 为非负整数；把 n 转成无前导零的 decimal 与 binary 表示，两者都是 palindrome 则为 True；0 的表示分别为 "0" 和 "0"，因此 predicate 对 0 返回 True。

生成函数只返回正整数，从小到大取前 k 个，0≤k≤30；k=0 返回 []，越界抛 ValueError。不能只给出一个固定答案列表。希望先生成 decimal palindromes 再检查 binary，而不是逐个枚举所有正整数。请说明 odd-length 和 even-length decimal palindrome 如何从前半部分构造，以及为什么生成顺序正确。

### 输入输出示例

```text
is_double_palindrome(9) -> True，因为 decimal="9"、binary="1001"。
is_double_palindrome(10) -> False。
first_double_palindromes(10) -> [1,3,5,7,9,33,99,313,585,717]。
```

## 回答思路

> **Situation / Task：** Predicate 包含 0，但生成函数只列正整数。  
> **Approach / Why：** 按 decimal digits 数与 prefix 升序构造 palindrome，再检查 binary。  
> **Result / Check：** 前若干项与逐整数 brute force 对照，检查 odd/even digits。

## 解题思路与参考答案

我会先把两个接口对零的规则说清楚，避免 predicate 和生成函数看起来矛盾。生成时不必测试所有正整数，只构造 decimal palindrome 候选。

固定总位数后，按前半部分从小到大枚举，镜像生成完整数字；奇数位时中心位只使用一次。候选在同一位数内递增，不同位数也递增，所以通过 binary 检查的结果自然有序。

### 完整参考实现

```python
def is_double_palindrome(n):
    if n < 0:
        raise ValueError('nonnegative integer required')
    decimal = str(n)
    binary = bin(n)[2:]
    return decimal == decimal[::-1] and binary == binary[::-1]


def first_double_palindromes(k):
    if not 0 <= k <= 30:
        raise ValueError('k outside 0..30')
    result = []
    digits = 1
    while len(result) < k:
        half = (digits + 1) // 2
        for prefix in range(10 ** (half - 1), 10**half):
            text = str(prefix)
            reflected = text[:-1] if digits % 2 else text
            candidate = int(text + reflected[::-1])
            binary = bin(candidate)[2:]
            if binary == binary[::-1]:
                result.append(candidate)
                if len(result) == k:
                    return result
        digits += 1
    return result
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert is_double_palindrome(0)
assert is_double_palindrome(9)
assert not is_double_palindrome(10)
assert first_double_palindromes(0) == []
assert first_double_palindromes(10) == [1, 3, 5, 7, 9, 33, 99, 313, 585, 717]
expected = [n for n in range(1, 1000000) if is_double_palindrome(n)]
assert first_double_palindromes(len(expected)) == expected
assert first_double_palindromes(30) == sorted(set(first_double_palindromes(30)))
print('double palindrome tests passed')
```

## 复杂度与追问

若枚举 P 个 decimal palindrome 候选、最大位数 D，时间约 `O(P*D)`，除输出和转换字符串外空间 `O(D)`。K 不能直接当作运行时间上界，因为两种 base 同时为 palindrome 的密度并不恒定。
