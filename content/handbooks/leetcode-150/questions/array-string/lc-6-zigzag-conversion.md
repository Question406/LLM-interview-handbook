---
id: lc-6-zigzag-conversion
section: array-string
order: 22
level: A
title: LC 6 · Z 字形变换
quick: >-
  按行模拟：每行一个缓冲区，字符依次落进当前行，走到第 $0$ 行或第 `numRows-1` 行就折返方向，最后把各行拼起来，不用建二维网格。时间
  $O(n)$。
tags:
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 6. Z 字形变换
    url: 'https://leetcode.cn/problems/zigzag-conversion/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

把字符串 s 的字符依次写入 numRows 行形成折返的 Z 字形：先从第一行向下写，到最后一行后沿对角线向上写，回到第一行后再次向下，直到写完。随后按行从上到下、每行从左到右读取，得到新的字符串。

### 接口与输出

实现 `convert(s: str, numRows: int) -> str`。输出包含原字符串的全部字符及相同出现次数，只改变排列顺序；`numRows=1` 时字符串保持原样。

### 合法输入与约束

`1 <= len(s) <= 1000`，`1 <= numRows <= 1000`。字符为大小写英文字母、逗号或句号；numRows 可以大于字符串长度。

### 示例

```text
输入：s = "PAYPALISHIRING", numRows = 3
输出："PAHNAPLSIIGYIR"
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/zigzag-conversion/description/)。

## 解题思路与参考答案

## 题意

把字符串 `s` 按 Z 字形排成 `numRows` 行，再按行读出新串。`numRows=1` 时原样返回。

## 思路

我会按行模拟，不必建二维网格。开 `rows[0..numRows)` 各攒一行字符，行号 `r` 从 $0$ 出发、方向 `dir=1`，每写入一个字符就 `r += dir`，碰到顶或底就 `dir = -dir`，最后 `"".join(rows)`。

拿 `"PAYPALISHIRING"`、`numRows=3` 走一遍：行号按 $0,1,2,1,0,1,2,\ldots$ 往复，第 $0$ 行攒到 `PAHN`，第 $1$ 行 `APLSIIG`，第 $2$ 行 `YIR`，拼起来是 `PAHNAPLSIIGYIR`。

也可以用周期 $2(\texttt{numRows}-1)$ 直接算每个字符属于哪一行，不过模拟更好讲。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert convert("PAYPALISHIRING", 3) == "PAHNAPLSIIGYIR"
assert convert("PAYPALISHIRING", 4) == "PINALSIGYAHRPI"
assert convert("A", 1) == "A"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（各行字符）。

## Edge Cases

`numRows=1` 时没有折返，原样返回。`numRows \ge len(s)` 时竖着一列就写完了，读出来仍是原串。两行时周期为 $2$，奇偶下标分别落在第 $0$、$1$ 行。

## 追问

**只要某一行的字符呢？**
按周期跳着取，不用开 `numRows` 个缓冲区。周期 `cycle = 2*(numRows-1)`，第 `row` 行在每个周期里先取 `k*cycle + row`；中间行在同一周期还有斜上的那个字符，下标是 `k*cycle + cycle - row`；首行和末行每个周期只有一个字符。这样是 $O(n/\texttt{numRows})$ 量级地跳着取，最坏仍 $O(n)$，额外空间只存这一行。中间行容易漏掉斜上的那个下标；`numRows=1` 时周期是 $0$，不能做模。`row` 越界应返回空串。

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

**要打印带空格的 Z 字形图呢？**
这时就得真的落二维网格，按行读出的压缩串不够。竖直向下时列不变，斜向上时每次列加一、行减一，碰到顶或底就换方向；字符按这个坐标写入，其余格子填空格，最后按行 `join`。网格宽度最坏 $O(n)$，所以时间 $O(\texttt{numRows} \cdot n)$，额外空间同阶。斜上时忘了加列，图会叠在同一列；`numRows=1` 也不该去走折返。输出给人看时记得 `rstrip` 掉行尾空格，判题的原题并不要这张图。

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
