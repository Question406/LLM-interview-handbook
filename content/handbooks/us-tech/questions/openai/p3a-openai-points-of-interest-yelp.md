---
id: p3a-openai-points-of-interest-yelp
section: openai
order: 648
level: A
title: OpenAI：附近地点搜索：地理索引和低延迟
quick: >-
  先用 geohash 或空间树找候选，覆盖与查询圆相交的所有 cell，再按真实球面距离过滤和排序。只查当前格子会漏掉 cell boundaries
  附近的地点；城市与稀疏地区用不同粒度，并按候选数和热点分布安排分片、缓存和副本。
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · points-of-interest-yelp
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/points-of-interest-yelp
    type: secondary
---

附近地点搜索可以先用空间索引缩小候选，再用球面距离精确过滤和排序。比如用户站在网格边缘，隔壁格子的咖啡店可能最近，查询就必须覆盖所有与搜索圆相交的 cell，不能只取当前格子。

这是类似 Yelp、读多写少的检索题。练习假设五亿地点、每秒十万次查询，按经纬度和半径返回最近地点，延迟要求 &lt;100ms。开始确认是否还按类别过滤、按营业时间排序；地理距离也不能无限近似成平面欧氏距离。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

地点变更流负责更新 geohash 或空间树索引。数据可以保存 `POI(id, lat, lon, category, hours, version)`，再用 `cell_members` 记录格子里的地点。查询先召回相交 cell，精确过滤距离后按距离和业务分数重排，结果再进入缓存。

比如用户查 1km 内咖啡店，系统先找到所有与半径 1km 的圆相交的格子，从 `cell_members` 取类别为咖啡的候选。逐个计算球面距离，删除超过 1km 的地点，再按距离和评分返回前 20 个。用户越靠近 cell boundaries，要覆盖的相邻格子越多。

密集城市把 cell 分细并增加只读副本，稀疏地区用较大 cell。索引迁移时双写新旧索引，按 version 去重；暂时查不到索引时也要有一致的降级策略。容量根据真实密度估候选数、热点和缓存命中率，五亿地点平均分片会掩盖城市热点。

验证时看每次候选数的分布、召回遗漏率、P99 延迟和热门 cell QPS，再反过来调网格粒度。

## 追问

**跨 180 度经线或靠近极区怎么办？**
包围框要处理经度环绕，最终统一用球面距离判断。字符串前缀范围不能替代所有地理计算。

**半径内没有结果怎么办？**
按产品约定扩大半径或提高 cell 层级重新召回，并把实际半径返回前端，让用户知道搜索范围已经变化。
