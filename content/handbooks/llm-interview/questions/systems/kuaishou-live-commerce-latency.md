---
id: kuaishou-live-commerce-latency
section: systems
order: 180
level: A
title: 快手实习二面：直播带货商品很多时，如何设计方案降低时延？
quick: "我会先用检索把商品库缩成短名单，再缓存商品卡、并行查库存和价格，让模型只处理 top-k。直播画面可以用动态分辨率、关键帧和局部裁剪减少视觉 token；会话复用 KV，但缓存要随商品集版本失效。"
tags:
  - Kuaishou
  - Latency
  - Live Commerce
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手大模型算法二面-实习面经
    url: https://www.nowcoder.com/feed/main/detail/ca3fe5949e0b4ddbb7807e43380ab7a6
    type: candidate-first-hand
  - title: vLLM Automatic Prefix Caching
    url: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
    type: primary
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“场景题：目前有一个带货的直播间，设计一个方案，商品比较多怎么降低时延”**

我会先检索出相关商品，再让模型只看短名单，并把商品资料缓存、库存价格并行查询和生成服务分别优化。比如观众问主播手里这件商品多少钱，系统先对齐当前 SKU，再取商品卡就够了，没必要把全店目录都交给模型。

直播带货要求秒级首包，弹幕和话术还要对应正在讲解的商品。验收时我会同时看首 token、整轮 p95 和推荐错品率：回复很快却推荐错商品，同样会伤害转化。

## 先找对商品，再生成回复

用弹幕或主播话术在商品库里做稀疏检索（标题/类目）和稠密检索（embedding），只留下几十个候选。在播 SKU、货架标签、库存状态做硬过滤。HNSW / IVF 选型同向量卡：要的是短名单延迟，不是全库精确。热卖款可以常驻内存倒排，冷款走向量。禁止把全店 JSON 拼进 prompt：输入预填充（prefill，即处理输入并建立缓存） 随 $N$ 变贵，中间商品会被淹没，见 `pdd-window-not-always-better`。

召回之后才是模型：只看短名单 + 当前问题 + 近几轮记忆。讲解稿、卖点可以预计算，不要现场让模型从零写。多商品对比用「先检索再读相关字段」，不要上 128K 硬看全目录。

## 复用资料，减少现场计算

标题、卖点、讲解稿、类目属性预计算进 Redis；库存、价走短 TTL 或并行 RPC。热卖 SKU 常驻。工具 fan-out：库存、券、物流能并行就并行，见 `kuaishou-tool-chain-latency`。超时降级到检索卡（无生成），总比卡住不返回。会话 KV / prefix cache 复用系统提示和本场直播间模板；key 要带商品集版本，上架变更不能复用旧前缀。

视觉侧：不要对货架全图每帧跑完整 VLM。动态分辨率、只 crop 主播手持区域、关键帧而不是每帧，压视觉 token。讲解中的 SKU 用检测/条码/OCR 对齐商品库，比让 VLM 从全图「找一下」稳且快。



生成侧：continuous batching 处理弹幕流量尖峰；限制 max tokens，讲解回复要短。小模型路由简单问句（「多少钱」走检索卡），复杂对比再上大模型。错品护栏：类目不一致、无货、价格超阈值则拦截或改检索卡。验收：首 token p95、整轮 p95、错品率、降级率。检索和缓存把现场需要处理的商品数量降下来后，再根据这些指标调整 serving。

## 追问

**为什么不把全店塞进长窗口？**
prefill 和 KV 随 $N$ 涨，中间 SKU 易丢（Lost in the Middle），错品风险上升，直播 SLA 也撑不住。先稀疏+稠密检索再生成，窗口只留短名单和近轮记忆。
**每个商品跑 VLM 行不行？**
不行。视觉 token、队列和费用和排队开销会使秒级首包目标难以满足。先检测/条码/OCR 对齐 SKU，模型只对 top-k 商品卡做话术。动态分辨率和关键帧，不要每帧全图。
**库存实时性怎么保证？**
展示缓存短 TTL 抗尖峰；下单回主库。生成用的价/库存带时间戳，过期则降级到检索卡，不要用过期缓存编话术。
**前缀缓存注意什么？**
公共直播间人设和讲解模板可复用；商品集、活动、价格带一变必须换 key，否则旧卖点续进新场。这和 Redis 商品卡缓存是两层。
**成功标准是什么？**
首 token p95、整轮 p95、错品率、降级率。tokens/s 不是直播指标。降级到检索卡算可用，卡住或错推算失败。
