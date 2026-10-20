---
id: p3a-cohere-delete-digit-five
section: overview
order: 804
level: A
title: "Cohere：删除数字 5 的题目线索"
quick: "只有标题线索，无法确定是删一个 5、删全部 5 还是可以选择删几个；先和面试官确认题意，再选字符串过滤或枚举删除位置的做法，并处理好负号和删空的情况。"
companies:
  - cohere
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - cohere
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Cohere：删除数字 5 的题目线索"
    url: https://www.1point3acres.com/interview/problems/7db16bf3-5b95-55de-a7dc-7da080f1a1e3
    type: secondary
---

## 题目

一亩三分地的 Cohere 目录里有一道题，标题是 Remove All Digit Fives to Maximize a Number，大意是从一个整数里删掉数字 5，让结果尽量大。完整题干没有看到。

> 来源：一亩三分地 Cohere 公司目录（2026-10-18 用 Chrome 读取），只读到标题，完整题干未核实，因此不标为已核实真题（`realInterview: false`）；网站收录也不等于公司官方确认，不能把它归到 Cohere 的具体岗位。下面的两个接口、约束和测试是手册补的练习约定，不是原题。

## 思路

单看标题有歧义：「Remove All」像是删掉所有 5，但如果全删，结果是唯一的，谈不上「Maximize」；「Maximize」更像是要在几个 5 里选一个删。也可能允许删任意多个。所以第一步是问清楚到底是哪种。

这份练习把两种最可能的理解都写出来：

- 删全部 5：直接对数字串做过滤，再处理负号和删空（比如 `55` 删完是空串，约定为 0）。
- 恰好删一个 5：枚举每个 5 的位置，删掉后转成带符号整数，取最大值。

负数要特别小心：结果是负数时，「最大」意味着绝对值最小，贪心方向正好和正数相反。枚举所有位置再比较带符号的整数，可以避开这个陷阱，也方便用来核对更快的贪心写法。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `remove_all_fives(n)`：删除 $|n|$ 的十进制表示中所有的 5，保留原符号；删空时结果为 0。
- `remove_one_five(n)`：恰好删除一个 5，返回能得到的最大整数；$n$ 中没有 5 时抛 `ValueError`。
- $n$ 为整数，$|n| \le 10^{18}$。
- 两个接口只是对标题两种理解的练习，不代表原题就是其中之一。

### 输入输出示例

```text
remove_all_fives(515)   -> 1
remove_one_five(515)    -> 51     # 候选 15 和 51
remove_one_five(-515)   -> -15    # 候选 -15 和 -51，取较大的 -15
remove_all_fives(-55)   -> 0
remove_one_five(5)      -> 0
```

### 解题思路与正确性

删全部 5 的结果唯一，字符串过滤就是正确答案。

删一个 5 时，候选集合就是「删掉第 $i$ 个 5」对应的所有结果。代码把每个候选都还原成带符号整数再取最大值，比较的就是题目要求的量本身，所以正数和负数都不需要单独推理。

### 完整参考实现（Python 3）

```python
def to_signed_int(digits, negative):
    """把去掉若干位后的数字串转回整数；串为空时视为 0。"""
    value = int(digits or "0")
    return -value if negative else value


def remove_all_fives(n):
    """删除 n 的十进制表示（不含负号）中所有的 5，保留符号。"""
    digits = str(abs(n)).replace("5", "")
    return to_signed_int(digits, n < 0)


def remove_one_five(n):
    """恰好删除一个 5，返回能得到的最大整数；n 中没有 5 时抛 ValueError。"""
    digits = str(abs(n))
    candidates = [
        to_signed_int(digits[:i] + digits[i + 1:], n < 0)
        for i, digit in enumerate(digits)
        if digit == "5"
    ]
    if not candidates:
        raise ValueError(f"{n} contains no digit 5")
    # 每个候选都转成带符号整数再比较，负数时自然选出绝对值最小的那个
    return max(candidates)
```

### 可执行测试

```python
# 删全部和删一个的区别
assert remove_all_fives(515) == 1
assert remove_one_five(515) == 51

# 负数：删一个时要让绝对值尽量小
assert remove_one_five(-515) == -15
assert remove_all_fives(-55) == 0

# 删完为空的情况视为 0
assert remove_one_five(5) == 0
assert remove_all_fives(0) == 0

# 没有 5 时删一个报错
try:
    remove_one_five(123)
except ValueError:
    pass
else:
    raise AssertionError("remove_one_five(123) should raise ValueError")
```

### 复杂度与追问

设数字位数为 $D$。删全部是 $O(D)$；删一个要枚举最多 $D$ 个位置，每次复制字符串 $O(D)$，总共 $O(D^2)$。$D \le 19$，完全够用。

- 能不能做到 $O(D)$？可以用贪心。正数时，从左往右找第一个「后面紧跟的数字比 5 大」的 5，删掉它，那一位就变大了；找不到就删最后一个 5，因为此时删掉靠前的 5 会让较高位变小或不变，删最后一个能保留最长的不变前缀。负数时方向相反：找第一个后面跟着比 5 小的数字的 5，找不到就删最后一个。
- 如果允许删任意多个 5（包括不删）：位数越少的数绝对值越小，所以正数的最优解是一个都不删，负数的最优解是把 5 全部删掉。这个变体答案很直接，但值得在澄清题意时顺口排除。
