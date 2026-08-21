---
id: tencent-generate-parens
section: coding
order: 211
level: A
title: 腾讯混元一面：生成所有合法括号组合
quick: >-
  回溯：已放左括号数小于 $n$ 才能再放 `(`，右括号数小于左括号数才能放 `)`。复杂度按卡特兰数。先写递归再补剪枝，不要先生成再过滤。
tags:
  - Tencent
  - Hunyuan
  - Coding
  - Backtracking
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
---

## 真题 / 考点说明

- 公司：腾讯 · 混元
- 岗位：大模型日常实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手撕：括号生成”**（同场还有手写 MHA）

LeetCode 22。状态是 `(open, close, path)`。出口 `open == close == n`。同面若接着写 Attention，括号题先 5 分钟写完，把白板留给张量形状。不要先生成 $2^{2n}$ 再过滤合法性。

## 思路

合法前缀的不变量：任意前缀里 `(` 不少于 `)`；全程两者都不超过 $n$。因此：

- `open < n` 才能再放 `(`。
- `close < open` 才能再放 `)`。

回溯到 `open == close == n` 收一条。卡特兰数 $C_n$ 条答案，剪枝保证每条路径都合法。

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

## 复杂度

答案条数是卡特兰数 $C_n=\frac{1}{n+1}\binom{2n}{n}$，每条长度 $2n$，时间 $O(n\cdot C_n)$，递归栈 $O(n)$。先生成再过滤是 $O(4^n)$，面试里要主动对比。

## 边界与追问

1. $n=1$ 只有 `()`；$n=0$ 若允许则返回 `[""]`，开口问清。
2. 追问「判断一串是否合法」：计数或栈，遇到 `)` 时计数不能为负，结束必须为 $0$。
3. 同场 MHA：这题五分钟收工。追问分数括号 / 多色括号：状态加种类维度，剪枝规则同类。
