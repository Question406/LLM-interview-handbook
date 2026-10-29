---
id: drustz-f90760ae0c1857bf6f
section: openai
order: 31
level: A
title: Points Of Interest Yelp
quick: original-structured-preparation-guide · Points Of Interest Yelp
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/points-of-interest-yelp
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Points of Interest / Yelp：五亿地点的附近搜索

## 证据边界

可见题面只确认：设计可扩展的地点服务，让用户发现附近的餐馆、商店和企业，并能承载全球约五亿个 POI；公开预览在 `worldwi...` 处截断。标签还指向 location、geohash、sharding、caching、schema design 和 database。没有可靠证据说明必须实现评论、商家广告、路线导航或用户写点评，因此本稿把“附近检索”作为主线，把商家更新作为必要的后台能力；评分、营业中、类别筛选列为合理澄清项，而不是冒充原题硬约束。开场要问：查询是给定中心点与半径，还是返回固定数量最近点；要求强制按距离还是综合排名；位置多久更新、是否支持临时闭店；读写比与目标延迟是多少。本文的 2km、20 条结果等数字只是演示。成功标准是圆形范围不漏边界点、返回距离准确、分页稳定，且热门市中心与全球稀疏区域都能扩展。

## 完整需求、接口与请求流程

核心读接口可写为 `GET /pois/nearby?lat=&lng=&radius_m=&category=&open_now=&limit=&cursor=`，返回 `poi_id、name、lat/lng、distance_m、category、rating、open_status` 与下一页 cursor；详情接口按 `poi_id` 读取，后台另有创建/更新/关闭 POI 的管理接口。例：用户在旧金山市中心查询“2km 内、现在营业的意大利餐厅、取前 20 个”。API 先校验经纬度与半径，再把查询圆覆盖成一组空间 cell；并行读取这些 cell 中类别为餐厅的候选 ID，批量取轻量字段，用 Haversine 或球面距离做精确过滤，排除 cell 方框内却在圆外的点，检查营业时间，最后按距离、质量和业务规则排序。cursor 应携带版本、最后一个 rank score 与 `poi_id`，而不是简单 offset，避免插入新商家后翻页重复。点击结果时再读照片、菜单和长描述，附近列表不应携带大对象。

## 地理索引、存储与排序

权威 POI 表以 `poi_id` 分片，存经纬度、地址、类别、营业时间、版本和状态；对象存储保存图片。写入经校验后提交主库，再由 CDC/事件流更新地理检索索引与缓存。检索层可用 S2、H3 或 geohash：把地球分层切成 cell，索引键为 `(resolution, cell_id, category)`，值为 POI 的紧凑投影。查询半径决定层级，小半径用细 cell，几十公里用粗 cell，避免枚举成千上万个格子；圆横跨 cell 边界时必须覆盖相邻格，最后再算精确距离。geohash 的前缀邻近不等于真实圆形邻近，不能只查中心点所在格。五亿条记录可按 cell 范围或一致性哈希分片，但高密度市中心需要把一个热 cell 再按子 cell/类别拆分；海洋与乡村则可合并稀疏 cell。热门查询缓存的是“cell + 筛选条件”的候选 ID 短列表，POI 详情独立缓存，更新通过版本号失效，允许可控的秒级陈旧。

## 容量、复杂度与故障测试

设查询覆盖 C 个 cell、取出 P 个候选、最终返回 K 个结果。并行 cell lookup 取决于索引实现，应用侧精确过滤为 `O(P)`，选前 K 可用大小为 K 的堆做到 `O(P log K)`；应以控制 P 为首要目标，而非先优化距离公式。容量估算要从五亿 POI 的每条紧凑索引字节数、复制因子、每日更新量、峰值附近查询 QPS 和热门城市倾斜出发；主库、地理索引和图片存储分别计算，不能把整条商家对象复制进每个分辨率层。测试覆盖：查询圆跨 cell 边界、国际日期变更线和极区；经纬度非法、半径为零或过大；同一商家重复导入、地址移动、永久/临时关闭；夏令时导致 `open_now` 错误；主库已更新但索引/缓存仍旧；一个 downtown cell 突然爆热；分片超时只返回部分 cell 时应明确降级而非悄悄声称完整。质量指标包括 recall（用离线暴力圆查询作真值）、距离误差、零结果率、p95/p99 延迟、候选放大比、索引新鲜度和跨页重复率。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/points-of-interest-yelp)
- [相关来源](https://www.1point3acres.com/bbs/thread-1174549-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
