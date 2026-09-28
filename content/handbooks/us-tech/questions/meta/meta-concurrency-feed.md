---
id: meta-concurrency-feed
section: meta
order: 12
level: A
title: Meta：信息流后端并发（缓存、一致性），偏工程轮
quick: >-
  Feed 读多写少、热点极不均匀。图数据走 TAO 这类缓存，时间线常常是写时扇出加读时聚合。一致性是「自己发的帖要立刻看见」，不是全局线性。缓存失效、热 key、重复扇出是这轮的分点。
tags:
  - Meta
  - Feed
  - Caching
  - Consistency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: TAO — The power of the graph
    url: https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/
    type: primary
  - title: Client-side ranking to more efficiently show people stories in feed
    url: https://engineering.fb.com/2016/10/20/networking-traffic/client-side-ranking-to-more-efficiently-show-people-stories-in-feed/
    type: primary
  - title: News Feed ranking, powered by machine learning
    url: https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/
    type: secondary
---

信息流后端是 Meta 工程轮的老题：不是再讲一遍多任务排序（那是 `meta-newsfeed-rank`），而是请求路径上的缓存、并发和一致性。公开材料够用：TAO 管图读取，2016 年博客写过客户端再排序。不要编造内部服务名。

## 读写路径先画清楚

一次打开 Feed 大约是：鉴权 → 取候选库存（好友/关注的近期动作） → 特征 → 排序 → 混排广告 → 下发。库存从社交图来：人、帖、赞、评论是点和边。TAO 的公开叙述：对象和关联缓存在分布式缓存里，读走缓存，写回存储再失效/更新缓存。QPS 以读为主，写是点赞、发帖、评论。

两种扇出：

- **写时扇出（fanout-on-write）：** 发帖时把条目推进粉丝的时间线缓存。读快，写时粉丝数就是放大倍数。
- **读时扇出（fanout-on-read）：** 读时去拉关注对象的近期帖再合并。写便宜，读时延迟和扇出度绑在一起。

工业上是混合：普通用户写时扇出；超大 V（celebrity problem）改读时拉，避免一条明星帖打爆写路径。面试要把这个热点说出来，不要只画一个 Redis list。

2016 年客户端排序：服务端下发一个池，设备上再按「媒体是否已下载、网络好坏」插队。这是**读路径上的第二次并发决策**，用来掩盖慢网和灰盒。工程含义：同一用户短时间看到的顺序，服务端权威分和客户端展示分可以不同，产品要能接受。

## 一致性：说清楚谁必须立刻看见

别开口「我们要强一致」。Feed 要的是：

- **Read-your-writes：** 我发完帖、点完赞，刷新要看见。常见实现是写后走主、或 sticky session、或在响应里直接带上刚写的对象。
- **好友可以稍晚看见：** 时间线缓存允许短暂旧数据。TAO 公开就是为社交读做的，不是跨机房线性一致。
- **计数器（赞数、评论数）：** 最终一致可接受，但单调性更好（不要 100 → 98 → 101 乱跳）。常用异步聚合，读走近似值。
- **删除 / 完整度下架：** 必须尽快从缓存拿掉。这是「宁可读不到，不能读到已删/已违规」。失效路径的 SLA 比点赞计数更严。

并发坑：两点赞同时打到同一计数；发帖同时隐私从公开改成仅好友；排序缓存里还是旧特征。我会说：**权威在存储，缓存是加速**；隐私和完整度相关的读，失效或短 TTL，不能为了命中率把违规内容缓存 10 分钟。

热 key：明星对象的边列表、热帖的计数。不加保护，缓存会把同一对象打到同一台机器。手段：本地缓存、复制热对象、请求合并（单飞）、分片计数再加和。失效风暴也要防：大 V 改隐私或删帖时，不要让所有读同时打穿到存储，用锁租约或短暂保留旧值再切。

## 和排序服务怎么切

排序是 CPU/GPU 贵、状态较短。缓存的是**特征**和**候选 id**，不是把 $V$ 分缓存一天：用户状态一直在变。候选缓存可以秒到分钟级；模型分最好现算或极短缓存。客户端池解决的是网络，不是用过期 $V$ 顶替完整度过滤。

重复请求：客户端重试 + 写时扇出会造成重复条目。时间线插入要幂等（post id 去重）。点赞写要幂等，否则计数器被重试打飞。

## 追问

- **Cache-aside 还是 write-through？** TAO 这类是写存储、更新/失效缓存。纯 cache-aside 在并发写下容易短暂脏读；Feed 可接受短暂脏，不可接受已删还在。
- **跨机房？** 读就近缓存，写发到主区域再异步扩。用户自己的写用 sticky / 主读满足 read-your-writes。
- **和广告混排？** 广告请求独立预算和校准（`meta-ads-calibration`），失败时降级成纯有机，不要让广告超时挡住整屏 Feed。
- **排障怎么看？** 命中率、热 key QPS、失效延迟、重复扇出、p99 在缓存还是排序。不要一上来加机器。
- **点赞计数和删帖冲突？** 删帖走完整度失效，计数可以异步。顺序上先让内容消失，计数慢一拍可以接受，反过来不可接受。
