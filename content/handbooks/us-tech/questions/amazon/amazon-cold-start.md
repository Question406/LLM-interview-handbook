---
id: amazon-cold-start
section: amazon
order: 6
level: A
title: Amazon：冷启动商品 / 新 query，推荐和搜索怎么共用信号？
quick: >-
  新 ASIN 没点击，新 query 没历史。两边都先靠类目、标题、品牌、替代品这些非行为特征给行为指标一个先验，再用曝光后验更新。搜索点击和推荐曝光是同一套反馈，catalog
  embedding 和替代关系一张图，不要各训各的冷启动分支。
tags:
  - Amazon
  - Cold Start
  - Search
  - Recommendations
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Addressing cold start in product search via empirical Bayes
    url: https://www.amazon.science/publications/addressing-cold-start-in-product-search-via-empirical-bayes
    type: primary
  - title: Treating cold start in product search by priors
    url: https://www.amazon.science/publications/treating-cold-start-in-product-search-by-priors
    type: primary
  - title: Behavioral feature boosting via substitute relationships for e-commerce search
    url: https://www.amazon.science/publications/behavioral-feature-boosting-via-substitute-relationships-for-e-commerce-search
    type: primary
---

Search 和 Recs 的 loop 都爱问冷启动，因为头部商品的 nDCG 会把问题藏住。Amazon Science 有一组公开做法：用非行为特征给点击率一类行为特征加 Empirical Bayes 先验；用替代品把老商品的点击 / 加购 / 购买借给新品。论文写的是搜索，推荐里的新 ASIN、新用户是同一数学。不是某次面经逐字题。答的时候要有客户（买不到新品）、卖家（永远没曝光）、业务（探索别把 GMV 砸穿）三边，这是 Customer Obsession 加 Deliver Results，见 `amazon-lp-ml`。

## 缺的是行为，不是文本

学习排序里真正拉动短期名次的是 query–item 上的点击率、转化率。新品 $n$ 次曝光都没有，$m/n$ 未定义或方差炸。Empirical Bayes 的讲法：

$$
\hat{p}=\frac{m+\alpha}{n+\alpha+\beta}
$$

$\alpha,\beta$ 不是全局拍脑袋，而是用类目、价格带、品牌、文本相似邻居，从已有商品上学出来的先验。有曝光后再把 $m,n$ 更新进去。先验让新品能进候选；后验让真不行的品退回去。公开 A/B（约 50M query）写过新商品曝光和购买都有两位数相对提升，总购买还有小正，说明探索不必写成「牺牲 GMV」。

替代品是另一条共用信号：同一 query 下可替换的 ASIN，把它们的行为聚合成新品的暖启动特征。替代图来自联合购买、共同点击、类目属性，推荐的「买了还买」和搜索的 substitute 可以共用这张图，不要搜索团队做一份、首页推荐再做一份。

新 query（尾 query、新品牌词、季节词）镜像对称：query 侧没有点击统计。用改写到头 query、类目预测、query embedding 近邻，把头 query 的行为先验借过来。拼写和空格变体先走词法，见 `amazon-kendra-hybrid`，别把 `iphne 16` 当成语义冷启动。

## 搜索和推荐共用什么，不共用什么

**该共用：**

- **Catalog 内容塔。** 标题、图、品牌、类目路径的 embedding。双塔 item 塔本来就不该依赖用户历史，见 `amazon-two-tower`。同一向量既给搜索召回，也给「相似商品」推荐。
- **替代 / 互补图。** 搜索用来借行为特征，推荐用来填车和详情页。
- **反馈定义。** 点击、加购、购买、退货。搜索的 skip 和推荐的 impress-without-click 都要进同一特征存储，窗口和点时间对齐，见 `amazon-feature-store`。
- **探索预算。** 新品曝光配额、epsilon、或 bandit。搜索结果页和推荐槽位抢同一用户注意力，配额要统一记账，否则两边都「探索 2%」实际打了 4%。

**不该硬共用：**

- **目标。** 搜索先相关性再转化；推荐更偏发现和 GMV。把推荐 CTR 模型直接当搜索 ranker，会出「相关但用户没搜这个」的货。
- **位置偏差。** 搜索第一位和推荐轮播的 propensity 不同，IPS / 位置特征不能抄。
- **新用户。** 推荐更痛（没历史）；搜索至少还有当前 query。新用户推荐走内容 + 类目热门 + 会话内点击，不要等画像。

双塔是结构上的冷启动解：item 塔只用内容，新 ASIN 只要进索引就能被语义召回。但精排若仍以行为特征为主，召回了也会排到第二页。所以冷启动要贯穿召回和排序：内容召回 + 先验行为特征 + 探索曝光，三件套。只做召回、精排照旧，是最常见的假上线。

评测切开：新 ASIN 的曝光、购买、退货；尾 query 的零结果率、成功购买；老商品是否被挤掉过多。只报全局 GMV，冷启动永远上不去——头部品会投票反对。退货和差评要进门禁，乱推新品是卖家友好、客户不友好。

## 追问

- **先验会不会把垃圾新品推上天？** 会，如果 $\alpha,\beta$ 只看类目热度。要加卖家承诺、合规、图文质量，并设探索上限；后验几个负反馈就该打回。论文里总购买仍为正，是因为先验跟踪的是「同类真转化」，不是均匀随机曝光。
- **没有替代品的真正新品呢？** 退回内容 embedding 和类目先验，接受更高不确定度，探索配额单独给。不要伪造替代边。
- **搜索点击能不能当推荐标签？** 能当弱标签，但有 query 条件。无 query 的推荐要用「去掉 query 的边缘」或另训。直接拿搜索购买当推荐正例，会过拟合头 query 品。
- **新 query 要不要上 LLM 改写？** 可以当召回扩充，但改写后仍要走词法保底，避免把品牌词改丢。延迟预算见 `amazon-p99-stream`；改写质量进 `amazon-titan-eval`，不要只看 BLEU。
