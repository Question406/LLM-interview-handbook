---
id: ali-algo-prep-list
section: alibaba-oa
order: 30
level: S
title: 阿里校招手撕：哪些题是第一梯队？
quick: >-
  必刷：反转链表 → K 组翻转 → 重排链表、编辑距离、第 K 大、层序、LRU。写完常被追「搜索纠错 / Top-K 推荐 / 流量 ×100」。
tags:
  - Alibaba
  - 手撕
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

## 真题记录

- 来源：公开校招面经统计（博客园 2026 高频总览 + 牛客 Java 面经）

| 梯队 | 题 | 阿里式追问 |
|------|----|------------|
| 必刷 | 206 / 25 / 143，72，215，102，146 | 线上链表损坏怎么修；LRU 加 TTL |
| 高频 | 53 / 56 / 1143 / 46 / 15 / 121 / 42 / 5 | 股票改成手续费；合并区间改日程冲突 |
| 中频 | 200 / 33 / 239 / 64 / 85 | 岛屿改园区连通；滑窗改实时 Top |

陷阱是把「第一梯队」当成再刷一遍力扣原题，或在本导航卡里堆完整解法。阿里校招手撕要的是：白板一次写对、复杂度说清、边界补全，然后接得住「搜索纠错 / Top-K 推荐 / 流量 $\times 100$」。下面按手册题卡 id 排期，解法去对应卡，不要在清单页假写一版代码。

## 必刷：一周内闭卷能写

- `ali-algo-list-family`：206 反转 $\to$ 25 $K$ 组翻转 $\to$ 143 重排。指针断了先画三格，再谈线上链表损坏怎么修。
- `ali-algo-lru`：哈希 + 双向链表。写完立刻接 TTL、并发、容量从进程内扩到分布式。
- `ali-algo-level-order`：102 层序是 BFS 模板；变形是锯齿、右视图、层均值，别只背一个 queue。
- `ali-algo-edit-distance`：72 状态 $dp[i][j]$。阿里爱把编辑距离接到搜索纠错、拼写提示。
- `ali-algo-kth-largest`：215 堆 vs 快选。线上 Top-K 推荐看 `ali-algo-scale-100x`。

## 高频：写完要能改约束

- `ali-algo-subarray-dp`：53 / 121 / 42 / 5 收口成「区间端点 + 是否可拆」。股票加手续费、接雨水改高度流。
- `ali-algo-interval-lcs`：56 合并区间改日程冲突；1143 LCS 别和编辑距离的二维表混。
- `ali-algo-perm-3sum`：46 / 15，防的是重复路径而不是多写一个 set。
- `ali-algo-path-rect`：64 最小路径和、85 最大矩形，二维 DP 的边界要先画。
- `ali-algo-rotate-window`：33 旋转数组、239 滑窗最大值，单调结构说清再写。

## 怎么验收

每张卡闭卷写一遍、说 $O(\cdot)$、举一个会错的边界，才算过。中频 200 岛屿若被问到，回 coding 章图遍历，不要和本章机试卡混。LLM 岗仍可能用这张清单当门槛——写对只是入场，追问才是区分。机试环形 / 方差 / 不相邻走 `ali-oa-prep-map`。

## 追问

- **为什么链表三题要连着刷？** 面试官常从 206 加约束推到 25 / 143，考指针不丢，不是三道新题。
- **刷完原题就够了吗？** 不够。每道必刷题至少准备一个线上变体，见 `ali-algo-scale-100x`。
- **和笔试怎么分工？** 手撕走本清单；环形 DP、区间方差、不相邻计数走 `ali-oa-prep-map`。
