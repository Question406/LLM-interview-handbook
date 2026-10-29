---
id: meta-concurrency-feed
section: meta
order: 12
level: A
title: Meta：信息流后端并发（缓存、一致性），偏工程轮
quick: "Feed 后端通常结合写时扇出与读时聚合，普通用户提前写时间线，大 V 在读取时拉取以控制热点。自己发帖要满足 read-your-writes，好友和计数可稍延迟，隐私变更与删除则要更快失效；重试和扇出都需幂等。"
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

Feed 后端要先把读写路径和一致性要求拆清，再处理热点与重试。普通用户可以写时扇出换快读，大 V 则改成读时聚合，避免一条帖子把写路径打满。这里讨论工程请求路径，多任务排序本身见 `meta-newsfeed-rank`。

打开 Feed 时，大致依次鉴权、取好友或关注对象近期动作的候选库存、取特征、排序、混排广告、下发。人、帖、赞、评论是图里的对象与关联，TAO 公开设计将它们缓存起来，读走缓存，写回存储后更新或失效缓存。流量以读为主，写主要来自发帖、点赞和评论。

写时扇出将新帖推到粉丝时间线，读快但写放大与粉丝数相关；读时扇出在打开页面时拉取并合并关注对象近期帖，写便宜但读延迟受扇出度影响，所以常采用混合方式。2016 客户端排序博客还描述服务端先给候选池，设备根据媒体是否下载、网络状况再调展示顺序，减少空白。产品需接受短时间内服务端权威分与客户端展示顺序不同。

## 按操作设置一致性

自己发帖或点赞后刷新，应满足 read-your-writes，可以写后读主、sticky session，或响应直接携带刚写的对象。好友看到新内容可允许短暂旧数据，TAO 并不要求跨机房全局线性一致。赞数、评论数可异步聚合并读近似值，尽量单调，避免 100 → 98 → 101 跳动。

删除、隐私变更、完整度下架则要更快失效，宁可暂时读不到，也别继续提供已删除或违规内容。两个点赞并发、发帖时从公开切到仅好友、排序缓存仍用旧特征，都要区分权威存储与缓存。隐私和完整度读采用失效或短 TTL，不能为命中率缓存违规内容 10 分钟。

热点包括明星对象的边列表与热帖计数，可以用本地缓存、复制热对象、请求合并（单飞）、分片计数再求和。大 V 删帖或改隐私时也要避免所有读同时穿透存储，利用锁租约等控制失效风暴；一般缓存切换可短暂保留旧值，但不能因此放松前面的删除与隐私要求。

排序侧更适合缓存特征和候选 id，候选可保留秒到分钟，模型分 $V$ 随用户状态变化，最好实时算或极短缓存。客户端候选池处理网络体验，不能拿过期 $V$ 替代完整度过滤。客户端重试与重复扇出都需按 post id 去重，点赞写同样要幂等，避免重复计数。

## 追问

**Cache-aside 还是 write-through？**
TAO 这类路径写存储后更新或失效缓存。纯 cache-aside 并发写下可能短暂脏读，Feed 可容忍部分旧数据，删除则要更严格。

**跨机房怎么办？**
就近读缓存，写主区域再异步传播，自己的写通过 sticky 或主读满足 read-your-writes。

**广告超时呢？**
广告单独设预算与 calibration，见 `meta-ads-calibration`，超时可退成纯非广告内容，避免挡住整屏 Feed。

**排障先看什么？**
看命中率、热 key QPS、失效延迟、重复扇出，以及 p99 究竟花在缓存还是排序。

**点赞计数与删帖同时发生？**
先确保内容消失，计数晚一点可接受，不能反过来。
