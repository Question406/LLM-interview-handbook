---
id: code-leetcode
section: coding
order: 11
level: A
title: 传统 Coding 要准备到什么范围？LLM 岗还会不会问 LeetCode？
quick: >-
  会。公开混元、阿里这些面经里，仍有链表、滑窗、DFS/DP。目标不是刷 500 道，而是常见 pattern
  能稳定写对，并能讲复杂度和边界。逐题讲法见资料库里的「面试经典 150」。
tags:
  - Coding
  - Algorithms
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 腾讯混元公开面经
    url: 'https://www.nowcoder.com/feed/main/detail/42fba762c2374372bcae72245f45f942'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>会。公开混元、阿里这些面经里，仍有链表、滑窗、DFS/DP。目标不是刷 500 道，而是常见 pattern 能稳定写对，并能讲复杂度和边界。逐题讲法见资料库里的「面试经典 150」。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>Pattern</th><th>代表题型</th><th>面试最低标准</th></tr></thead><tbody><tr><td>Hash / Sliding Window</td><td>Two Sum、Longest Substring、Min Window</td><td>能维护 invariant，O(n) 思路清晰</td></tr><tr><td>Linked List</td><td>Reverse、Merge、Cycle、LRU</td><td>指针边界不出错</td></tr><tr><td>Tree / Graph</td><td>DFS/BFS、LCA、Topo Sort、Islands</td><td>递归/迭代均会，visited 语义正确</td></tr><tr><td>Heap</td><td>Top-K、Merge K Lists</td><td>知道 O(n log k) 与 heap invariant</td></tr><tr><td>Binary Search</td><td>Search Range、Answer Search</td><td>左右边界模板不混</td></tr><tr><td>DP</td><td>Coin Change、Edit Distance、LIS</td><td>先定义 state/transition/base case</td></tr><tr><td>Backtracking</td><td>Parentheses、Permutation</td><td>剪枝、状态恢复正确</td></tr><tr><td>Parsing / Systems</td><td>stream parser、LRU/TTL、rate limiter</td><td>更贴近 Agent/infra 岗</td></tr></tbody></table></div><p>LLM 算法岗通常更值得把额外时间放到 Attention、RoPE、GAE、DPO、GRPO、Agent parser 这类领域手撕上，但传统算法题仍可能是基本 coding 门槛。逐题 30 秒讲法、参考代码和追问，已经收进资料库切换器里的「面试经典 150」（力扣官方 <a href="https://leetcode.cn/studyplan/top-interview-150/" target="_blank" rel="noopener noreferrer">Top Interview 150</a>）。</p></div>
          
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/42fba762c2374372bcae72245f45f942" target="_blank" rel="noopener noreferrer">↗ 腾讯混元公开面经</a></div>
