---
id: tencent-generate-parens
section: coding
order: 211
level: A
title: 腾讯混元一面：生成所有合法括号组合
quick: >-
  回溯，已放的左括号数小于 $n$ 才能再放 `(`，右括号数小于左括号数才能放 `)`，复杂度按卡特兰数算。先写递归再补剪枝，别先生成全部再过滤。
tags:
  - Tencent
  - Hunyuan
  - Coding
  - Backtracking
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
---

## 题目描述

给定整数 n，生成由 **n 对圆括号**构成的所有合法括号字符串。合法表示每个左括号都能与其后的右括号配对，且任意前缀中的右括号数不超过左括号数。

实现 `generate_parenthesis(n: int) -> List[str]`，返回没有重复项的字符串列表，每条长度为2n。此题对应 LeetCode 22“括号生成”；以下是独立中文题面表述。标准练习范围为 `1 <= n <= 8`。为方便与当前手册的断言一致，本地接口按字典序返回（字符 `(` 在 `)` 之前）；原题本身允许任意顺序。若扩展接受 n=0，约定返回 `['']`。

### 示例

```text
输入：n=3
输出：["((()))","(()())","(())()","()(())","()()()"]

输入：n=1
输出：["()"]
```

## 解题思路与参考答案

用回溯，每一步只放合法的括号：已放的 `(` 少于 $n$ 才能再放 `(`，已放的 `)` 少于 `(` 才能放 `)`，放满就是一个答案。这样每条路径都合法，不用先生成 $2^{2n}$ 个串再过滤合法性。

这是腾讯混元大模型日常实习一面的题，来自牛客候选人原帖，可信度 A，原话是**“手撕：括号生成”**，同场还有手写 MHA。题目就是 LeetCode 22。同一面如果接着写 Attention，括号题先 5 分钟写完，把白板留给张量形状。

## 思路

状态是 `(open, close, path)`。合法前缀有一个不变量：任意前缀里 `(` 不少于 `)`，全程两者都不超过 $n$。所以 `open < n` 时才能再放 `(`，`close < open` 时才能再放 `)`。拿 $n=2$ 走一遍：开头只能放 `(`；放成 `((` 之后只能放 `)`；放成 `()` 之后只能再放 `(`；最后得到 `(())` 和 `()()`。递归终止条件是 `open == close == n`，这时把当前路径加进答案。答案一共卡特兰数 $C_n$ 条，剪枝保证每条路径都合法。

## 参考代码

```python
from typing import List


def generate_parenthesis(n: int) -> List[str]:
    ans: List[str] = []

    def dfs(path: List[str], open_n: int, close_n: int) -> None:
        if open_n == close_n == n:
            ans.append("".join(path))
            return
        if open_n < n:
            path.append("(")
            dfs(path, open_n + 1, close_n)
            path.pop()
        if close_n < open_n:
            path.append(")")
            dfs(path, open_n, close_n + 1)
            path.pop()

    dfs([], 0, 0)
    return ans


if __name__ == "__main__":
    assert generate_parenthesis(1) == ["()"]
    assert generate_parenthesis(2) == ["(())", "()()"]
    assert generate_parenthesis(3) == [
        "((()))",
        "(()())",
        "(())()",
        "()(())",
        "()()()",
    ]
    print("ok")
```

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert generate_parenthesis(1) == ["()"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

答案条数是卡特兰数 $C_n=\frac{1}{n+1}\binom{2n}{n}$，每条长度 $2n$，时间 $O(n\cdot C_n)$，递归栈 $O(n)$。先生成再过滤是 $O(4^n)$，面试时主动对比一下。

## 追问

**$n=0$ 怎么办？**
如果题目允许，返回 `[""]`，先确认题目允不允许。$n=1$ 只有 `()`。

**怎么判断一个串是否合法？**
用计数或栈，遇到 `)` 时计数不能为负，结束时必须为 $0$。

**分数括号、多色括号呢？**
状态里加一个种类维度，剪枝规则同类。同场还有 MHA 的话，这题五分钟收工。
