---
id: ali-coding-islands
section: coding
order: 35
level: B
title: 淘天校招手撕：岛屿数量（思路卡）
quick: "用网格 DFS/BFS（或并查集）数连通分量：扫到没访问过的陆地就计数一次，再把整座岛淹掉。开口先问清是四连通还是八连通，说好是改输入淹没还是另开 visited。时间 O(mn)，递归最坏栈深 O(mn)，所以要准备迭代 BFS。"
tags:
  - Alibaba
  - Coding
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

## 题目描述

给定一个由字符 `"1"` 和 `"0"` 组成的等宽二维网格，分别表示陆地与水。一个岛屿是上下左右相连的陆地集合；斜对角接触不算相连。网格外部均视为水，返回网格中的岛屿个数。

### 接口与约定

本卡提供 `num_islands_dfs(grid)` 与 `num_islands_bfs(grid)` 两个同语义接口，各返回一个整数。允许在输入网格上做访问标记；比较两个接口时要分别传入网格副本。空网格或全水网格返回 0。

### 示例

```text
grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
任一接口的返回值 -> 3
num_islands_dfs([["0"]]) -> 0
```

这里给出的是与本卡代码一致的手册练习接口；返回数量，不要求返回各岛屿的坐标或面积。

<!-- problem-statement:end -->

<h2>解题思路与参考答案</h2>

<div class="quick"><div class="mini-title">30 秒回答</div><p>用网格 DFS/BFS（或并查集）数连通分量：扫到没访问过的陆地就计数一次，再把整座岛淹掉。开口先问清是四连通还是八连通，说好是改输入淹没还是另开 visited。时间 O(mn)，递归最坏栈深 O(mn)，所以要准备迭代 BFS。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div>
<p>这题就是数二维网格里的连通分量：从左到右扫格子，碰到还没访问过的陆地就 <code>ans += 1</code>，然后用 DFS 或 BFS 把这座岛整个淹掉。同一座岛只会在第一次碰到时计数一次。题目是 LeetCode 200，来自淘天大模型 Agent 校招面经里的手撕；网格按四连通算，陆地是 <code>"1"</code>，水是 <code>"0"</code>。阿里 LLM 岗常考这道，和最长无重复子串、平方根是同一档：会写、能讲复杂度，就过了门槛。</p>
<p>淹岛可以直接把格子改成 <code>"0"</code>，也可以另开 <code>visited</code>。四连通和八连通别搞混，开口先问清。并查集也能做：每块陆地和上下左右的陆地 union，最后数根的个数。现场我更稳的写法是 DFS/BFS。</p>
<p>下面的代码可以直接跑。用淹没写法就省掉了额外的 <code>visited</code>。递归版最坏的情况是一条蛇形岛，递归深度到 $O(mn)$，所以我会主动给一个迭代 BFS 防栈溢出。</p>
<pre><code>from collections import deque
from typing import List


def num_islands_dfs(grid: List[List[str]]) -> int:
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])

    def dfs(i: int, j: int) -> None:
        if i &lt; 0 or i &gt;= m or j &lt; 0 or j &gt;= n or grid[i][j] != "1":
            return
        grid[i][j] = "0"
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    ans = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1":
                ans += 1
                dfs(i, j)
    return ans


def num_islands_bfs(grid: List[List[str]]) -> int:
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    ans = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] != "1":
                continue
            ans += 1
            grid[i][j] = "0"
            q = deque([(i, j)])
            while q:
                x, y = q.popleft()
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 &lt;= nx &lt; m and 0 &lt;= ny &lt; n and grid[nx][ny] == "1":
                        grid[nx][ny] = "0"
                        q.append((nx, ny))
    return ans


if __name__ == "__main__":
    g1 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    g2 = [row[:] for row in g1]
    assert num_islands_dfs(g1) == 3
    assert num_islands_bfs(g2) == 3
    assert num_islands_dfs([["0"]]) == 0
    print("ok")
</code></pre>
<p>复杂度方面，每个格子最多入队或被递归访问一次，时间 $O(mn)$。额外空间上，DFS 最坏递归栈 $O(mn)$，BFS 队列最坏也是 $O(mn)$。并查集同样接近线性。</p>
<p>边界和常见追问：</p>
<ol>
<li><strong>要测哪些边界？</strong>空网格、全水、全陆地、单格，还有细长的蛇形岛。递归 DFS 在蛇形岛上可能栈溢出，面试时补一句改成 BFS 或显式栈。</li>
<li><strong>换成八连通，或者问最大岛屿面积呢？</strong>八连通就是对角线也算相连，方向数组扩到 8 个。最大岛屿面积是在搜索时累加格子数，维护一个全局 max，骨架不变。</li>
<li><strong>并查集怎么写？</strong>把 $i\cdot n+j$ 当节点，只和右边、下边 union，避免重复；水格子不进集合，最后数的就是图上的连通分量个数。岛屿周长（463）是另一回事，数陆地相邻的水边就行，不用再套一遍淹岛。</li>
</ol>
<p>想加分的话，先在纸上画一个 $3\times 3$ 的网格走一遍计数，再写代码，并主动说清是改输入淹没还是另开 <code>visited</code>。如果和「无重复最长子串」连着考，这题五分钟写完，把时间留给滑窗的 invariant。</p>
</div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>

<h2>简单测试怎么写</h2>
<p>把完整参考实现和题中的可执行测试按顺序放进 solution.py，运行 python3 solution.py。测试依赖的库与参考实现相同。</p>
<p>例如，测试中的 assert num_islands_dfs(g1) == 3 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。</p>
<p>先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，assert 能在不符合预期时直接报错。</p>
<p>先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。</p>
