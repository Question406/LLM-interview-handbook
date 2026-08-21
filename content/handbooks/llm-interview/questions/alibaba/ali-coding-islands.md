---
id: ali-coding-islands
section: alibaba
order: 35
level: B
title: 淘天校招手撕：岛屿数量（思路卡）
quick: 网格 DFS/BFS 或并查集：遍历到陆地就淹没整座岛并计数。注意边界与访问标记。
tags:
  - Alibaba
  - Coding
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>网格 DFS/BFS 或并查集：遍历到陆地就淹没整座岛并计数。注意边界与访问标记。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div>
<p><strong>真题 / 考点。</strong>淘天大模型 Agent 校招面经里的手撕：岛屿数量（LeetCode 200）。网格四连通，陆地是 <code>"1"</code>、水是 <code>"0"</code>。本质是二维图连通分量计数。阿里 LLM 岗仍常手撕这道，和最长无重复子串、平方根同一档「会写、能讲复杂度」的门槛题。</p>
<p><strong>思路。</strong>扫每一个格子。遇到未访问的陆地就 <code>ans += 1</code>，然后用 DFS 或 BFS 把四连通整座岛淹掉（改成 <code>"0"</code> 或打 <code>visited</code>）。同一座岛只在第一次碰到时计数。不要把八连通和四连通搞混，开口先问清。并查集也能做：每个陆地与上下左右陆地 union，最后数根的个数；现场 DFS/BFS 更稳。</p>
<p><strong>DFS 参考代码（可运行）。</strong>淹没写法省掉额外 <code>visited</code>。递归最坏是一条蛇形岛，深度 $O(mn)$，要主动提迭代 BFS 防栈溢出。</p>
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
<p><strong>复杂度。</strong>每个格子入队 / 递归至多一次，时间 $O(mn)$。额外空间：DFS 最坏递归栈 $O(mn)$，BFS 队列最坏 $O(mn)$。并查集也是近似线性。</p>
<p><strong>边界与追问。</strong></p>
<ol>
<li>空网格、全水、全陆地、单格、细长蛇形岛。递归 DFS 在蛇形岛上可能栈溢出，面试补一句改 BFS 或显式栈。</li>
<li>追问八连通：对角线也算陆地，方向数组扩到 8 个。追问「最大岛屿面积」：搜索时累加格子数，维护全局 max，骨架不变。</li>
<li>追问并查集：把 $i\cdot n+j$ 当节点，只和右/下 union 避免重复；水格子不入集。对应图上的连通分量个数。周长题（463）改成数相邻水边，不要再套一遍淹岛。</li>
</ol>
<p>面试加分：先画 $3\times 3$ 走一遍计数，再写代码；主动区分子岛修改输入 vs 另开 <code>visited</code>。和「无重复最长子串」连着考时，这题五分钟写完，把时间留给滑窗 invariant。</p>
</div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
