---
id: lc-6-zigzag-conversion
section: array-string
order: 22
level: A
title: LC 6 · Z 字形变换
quick: >-
  按行模拟：字符依次落入当前行，到第 $0$ 或第 `numRows-1` 行就折返方向。最后拼接各行。时间 $O(n)$。
tags:
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 6. Z 字形变换
    url: https://leetcode.cn/problems/zigzag-conversion/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把字符串 `s` 按 Z 字形排成 `numRows` 行，再按行读出新串。`numRows=1` 时原样返回。

## 思路

不必真的建二维网格。`rows[0..numRows)` 各攒一行字符。下标 `r` 从 $0$ 出发，方向 `dir=1`；写入后 `r += dir`，碰到顶或底则 `dir = -dir`。最后 `"".join(rows)`。

也可用周期 $2(\texttt{numRows}-1)$ 直接算每个字符属于哪一行。模拟更好讲。

## 参考代码

```python
def convert(s: str, numRows: int) -> str:
    if numRows == 1 or numRows >= len(s):
        return s
    rows = [""] * numRows
    r, dir_ = 0, 1
    for ch in s:
        rows[r] += ch
        if r == 0:
            dir_ = 1
        elif r == numRows - 1:
            dir_ = -1
        r += dir_
    return "".join(rows)


if __name__ == "__main__":
    assert convert("PAYPALISHIRING", 3) == "PAHNAPLSIIGYIR"
    assert convert("PAYPALISHIRING", 4) == "PINALSIGYAHRPI"
    assert convert("A", 1) == "A"
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（各行字符）。

## 边界

- `numRows=1`：没有折返，原样返回。
- `numRows \ge len(s)`：垂直一列写完就结束，读出来仍是原串。
- 两行：周期为 $2$，奇偶下标分别落在第 $0$、$1$ 行。

## 追问

- **只要某一行的字符？** 不必开 `numRows` 个缓冲区。周期 `cycle = 2*(numRows-1)`。第 `row` 行在每个周期里先取 `k*cycle + row`；若是中间行，同一周期还有斜上的那个字符，下标是 `k*cycle + cycle - row`。首行和末行每个周期只有一个字符。时间 $O(n/\texttt{numRows})$ 量级地跳着取，最坏仍 $O(n)$，额外空间只保存这一行。这块容易栽：中间行漏掉斜上那个下标，以及 `numRows=1` 时周期变成 $0$ 不能做模。`row` 越界应返回空串。

```python
def nth_row(s, numRows, row):
    if numRows == 1:
        return s if row == 0 else ""
    if row < 0 or row >= numRows:
        return ""
    cycle = 2 * (numRows - 1)
    chars = []
    j = row
    n = len(s)
    while j < n:
        chars.append(s[j])
        if 0 < row < numRows - 1:
            mid = j + cycle - 2 * row
            if mid < n:
                chars.append(s[mid])
        j += cycle
    return "".join(chars)
```

- **要打印带空格的 Z 字形图？** 按行读出的压缩串不够，必须真的落二维网格。列在竖直向下时不变，斜向上时每次列加一、行减一；碰到顶或底就换方向。字符按这个坐标写入，其余填空格，最后按行 `join`。时间 $O(\texttt{numRows} \cdot n)$（网格宽度最坏 $O(n)$），额外空间同阶。这块容易栽：斜上时忘了加列，图会叠在同一列；以及 `numRows=1` 仍去走折返。输出给人工看时记得 `rstrip` 掉行尾空格，判题版原题并不要这张图。

```python
def zigzag_grid(s, numRows):
    if numRows == 1:
        return s
    n = len(s)
    grid = [[" "] * n for _ in range(numRows)]
    r = c = 0
    going_down = True
    for ch in s:
        grid[r][c] = ch
        if going_down:
            if r == numRows - 1:
                going_down = False
                r -= 1
                c += 1
            else:
                r += 1
        else:
            if r == 0:
                going_down = True
                r += 1
            else:
                r -= 1
                c += 1
    width = c + 1
    return "\n".join("".join(row[:width]).rstrip() for row in grid)
```
