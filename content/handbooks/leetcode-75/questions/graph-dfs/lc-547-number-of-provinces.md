---
id: lc-547-number-of-provinces
section: graph-dfs
order: 2
level: S
title: LC 547 · 省份数量
quick: >-
  这是邻接矩阵表示的无向图数连通块。对每个没访问过的城市起一次 DFS，把整块标掉，起了几次就是几个省份。时间 $O(n^2)$，额外空间
  $O(n)$；并查集同样是 $O(n^2)$。
tags:
  - Graph
  - DFS
  - Union Find
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 547. Number of Provinces
    url: 'https://leetcode.com/problems/number-of-provinces/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

有 n 个城市，给定 n×n 矩阵 `isConnected`。当 `isConnected[i][j]=1` 时，城市 i 和 j 直接相连。若两个城市能通过若干条直接连接到达彼此，也视为相连。一组所有相互直接或间接连通的城市构成一个省份；孤立城市单独构成一个省份。

### 输入与输出

实现 `findCircleNum(isConnected) -> int`，返回省份总数。输入表示无向关系，不能只统计直接相连的城市对。

### 约束

- `1 <= n <= 200`，矩阵有 n 行且每行 n 个元素。
- 矩阵元素为0或1，对角线元素均为1。
- `isConnected[i][j] == isConnected[j][i]`，即矩阵对称。

### 示例

```text
输入：isConnected = [[1,1,0],[1,1,0],[0,0,1]]
输出：2
```

[LeetCode 原题](https://leetcode.com/problems/number-of-provinces/description/)

## 解题思路与参考答案

## 题意

$n$ 个城市，`isConnected[i][j] = 1` 表示城市 $i$、$j$ 直接相连，矩阵对称且对角线为 $1$。相连具有传递性，直接或间接相连的城市构成一个省份。返回省份数量。

## 思路

省份就是无向图的连通块，我用 DFS 数块。外层按下标扫城市，遇到没访问过的就计数加一，再从它出发 DFS，把同一块的城市全部标记。之后扫到这些城市会被跳过，所以每块只算一次。

拿 `[[1,1,0],[1,1,0],[0,0,1]]` 看：扫到城市 $0$，计数变 1，DFS 顺带把城市 $1$ 标掉；扫到 $1$ 已标记，跳过；扫到 $2$ 没标记，计数变 2。答案 2。

输入是邻接矩阵，找邻居要扫一整行，所以总时间是 $O(n^2)$，这也是读完输入本身的下界。

并查集也常考：对每个 `isConnected[i][j] = 1`（$i\lt j$）做 `union`，每成功合并一次块数减一。两种写法复杂度一样，我先写 DFS，被问到再补并查集。

## 参考代码

```python
from typing import List


def findCircleNum(isConnected: List[List[int]]) -> int:
    n = len(isConnected)
    seen = [False] * n
    provinces = 0
    for start in range(n):
        if seen[start]:
            continue
        provinces += 1
        seen[start] = True
        stack = [start]
        while stack:
            i = stack.pop()
            for j in range(n):
                if isConnected[i][j] and not seen[j]:
                    seen[j] = True
                    stack.append(j)
    return provinces


if __name__ == "__main__":
    assert findCircleNum([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
    assert findCircleNum([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 3
    assert findCircleNum([[1]]) == 1
    assert findCircleNum([[1, 1, 0], [1, 1, 1], [0, 1, 1]]) == 1
    assert findCircleNum([[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]]) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert findCircleNum([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
assert findCircleNum([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 3
assert findCircleNum([[1]]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$，每个城市出栈一次并扫一整行。额外空间 $O(n)$。

## Edge Cases

只有一个城市时，答案是 $1$。

全部孤立，也就是单位矩阵，答案是 $n$。

间接相连的情况，比如 $0$–$1$、$1$–$2$ 相连而 $0$、$2$ 不直接相连，还是同一个省份，DFS 会顺着 $1$ 走到 $2$。

## 追问

**并查集怎么写？**
每个点一开始自成一块，计数为 $n$。对上三角的每条边做 `union`，根不同才合并，并让计数减一。带路径压缩后单次操作近似 $O(1)$，总时间还是被扫矩阵的 $O(n^2)$ 主导。

```python
def findCircleNumUF(isConnected):
    n = len(isConnected)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count = n
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j]:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj
                    count -= 1
    return count
```

**输入换成边表 `edges` 呢？**
先建邻接表，再同样按点起 DFS，时间变成 $O(n+m)$。如果边是一条条在线到来、还要随时回答块数，更适合并查集，DFS 每次都得重跑。
