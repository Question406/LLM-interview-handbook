---
id: ali-algo-prep-list
section: alibaba-oa
order: 30
level: S
title: 阿里校招手撕：哪些题是第一梯队？
quick: >-
  第一梯队是反转链表 → K 组翻转 → 重排链表、编辑距离、第 K 大、层序和 LRU，一周内要能闭卷写出来。写完常被追问「搜索纠错 / Top-K 推荐
  / 流量 ×100」，所以每道题还要备一个线上变体。
tags:
  - Alibaba
  - 手撕
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: 'https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6'
    type: candidate-first-hand
---

第一梯队是 206 / 25 / 143、72、215、102、146 这几道，一周内要能闭卷写出来；高频和中频题写完以后要能改约束。这张卡只排顺序，解法都在对应的题卡里，这页不再写一版代码。题目统计来自公开校招面经（博客园 2026 高频总览和牛客 Java 面经）。

| 梯队 | 题 | 阿里式追问 |
|------|----|------------|
| 必刷 | 206 / 25 / 143，72，215，102，146 | 线上链表损坏怎么修；LRU 加 TTL |
| 高频 | 53 / 56 / 1143 / 46 / 15 / 121 / 42 / 5 | 股票改成手续费；合并区间改日程冲突 |
| 中频 | 200 / 33 / 239 / 64 / 85 | 岛屿改园区连通；滑窗改实时 Top |

阿里校招手撕要的是白板一次写对、复杂度说清、edge-case coverage 完整，然后接得住「搜索纠错 / Top-K 推荐 / 流量 $\times 100$」这类追问。光把力扣原题再刷一遍不够，所以下面按题卡 id 排期，每道题都多准备一个变体。

## 必刷：一周内闭卷能写

- `ali-algo-list-family` 讲 206 反转 $\to$ 25 $K$ 组翻转 $\to$ 143 重排。指针断了先画三格，再谈线上链表损坏怎么修。
- `ali-algo-lru` 是哈希加双向链表。写完马上会接 TTL、并发、容量从进程内扩到分布式。
- `ali-algo-level-order` 的 102 层序是 BFS 模板，变形有锯齿、右视图、层均值，光背一个 queue 应付不了。
- `ali-algo-edit-distance` 的 72 状态是 $dp[i][j]$。阿里爱把编辑距离接到搜索纠错、拼写提示上。
- `ali-algo-kth-largest` 的 215 讲堆和快选的取舍。线上 Top-K 推荐看 `ali-algo-scale-100x`。

## 高频：写完要能改约束

- `ali-algo-subarray-dp` 把 53 / 121 / 42 / 5 收到「区间端点 + 是否可拆」上。会被改成股票加手续费、接雨水改高度流。
- `ali-algo-interval-lcs` 里 56 合并区间会改成日程冲突；1143 LCS 别和编辑距离的二维表弄混。
- `ali-algo-perm-3sum` 的 46 / 15 防的是重复路径，多写一个 set 解决不了。
- `ali-algo-path-rect` 是 64 最小路径和、85 最大矩形，二维 DP base cases 要先画出来。
- `ali-algo-rotate-window` 是 33 旋转数组、239 滑窗最大值，先把单调结构说清再写。

## 怎么验收

每张卡闭卷写一遍、说出 $O(\cdot)$、举一个容易写错的 edge case，才算过。中频的 200 岛屿如果被问到，回 coding 章看图遍历，别和这一章的机试卡混在一起。LLM 岗也可能拿这张清单当 threshold：写对只是入场，追问才拉开差距。

## 追问

**为什么链表三题要连着刷？**
面试官常从 206 加约束推到 25、143，考的是指针不丢，算不上三道新题。

**刷完原题就够了吗？**
不够。每道必刷题至少准备一个线上变体，见 `ali-algo-scale-100x`。

**和笔试怎么分工？**
手撕走这张清单；机试里的环形 DP、区间方差、不相邻计数走 `ali-oa-prep-map`。
