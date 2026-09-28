---
id: lc-547-number-of-provinces
section: graph-dfs
order: 2
level: S
title: LC 547 · 省份数量
quick: >-
  邻接矩阵表示的无向图数连通块。对每个没访问过的城市起一次 DFS，把整块标掉，起了几次就是几个省份。时间
  $O(n^2)$，额外空间 $O(n)$。并查集同样 $O(n^2)$。
tags:
  - Graph
  - DFS
  - Union Find
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 547. Number of Provinces
    url: https://leetcode.com/problems/number-of-provinces/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

$n$ 个城市，`isConnected[i][j] = 1` 表示城市 $i$、$j$ 直接相连，矩阵对称且对角线为 $1$。相连具有传递性，直接或间接相连的城市构成一个省份。返回省份数量。

## 思路

省份就是无向图的连通块。外层按下标扫城市，遇到没访问过的就计数加一，再从它 DFS 把同一块的城市全部标记。之后扫到这些城市会被跳过，所以每个块只计一次。

输入是邻接矩阵，找邻居要扫一整行，所以总时间是 $O(n^2)$，这也是读输入本身的下界。

并查集也常考：对每个 `isConnected[i][j] = 1`（$i\lt j$）做 `union`，合并成功一次块数减一。两种写法复杂度一样，我先写 DFS，被问到再补并查集。

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

## 复杂度

时间 $O(n^2)$，每个城市出栈一次并扫一整行。额外空间 $O(n)$。

## 边界

- 只有一个城市：答案 $1$。
- 全部孤立（单位矩阵）：答案 $n$。
- 间接相连：$0$–$1$、$1$–$2$ 相连但 $0$、$2$ 不直接相连，仍是同一省份，DFS 会顺着 $1$ 走到 $2$。

## 追问

- **并查集怎么写？** 每个点初始自成一块，计数为 $n$。对上三角的每条边 `union`，根不同才合并并让计数减一。带路径压缩后单次操作近似 $O(1)$，总时间仍被扫矩阵的 $O(n^2)$ 主导。

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

- **输入换成边表 `edges`？** 先建邻接表，再同样按点起 DFS，时间变成 $O(n+m)$。边是在线逐条到来的场景（还要随时回答块数）更适合并查集，DFS 需要每次重跑。
