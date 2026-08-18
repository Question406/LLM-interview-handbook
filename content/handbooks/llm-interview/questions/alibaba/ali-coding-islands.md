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
          <div class="full-answer"><div class="mini-title">完整答案</div><p>阿里 LLM 岗仍常手撕经典题（岛屿数量、无重复最长子串、平方根等）。</p>
<p>岛屿数量：对每个未访问的 <code>1</code> 启动搜索，将连通块标记为已访问，计数 +1。时间 O(mn)。</p>
<p>面试加分：讨论并查集写法、以及与“连通分量”在图上的对应。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
