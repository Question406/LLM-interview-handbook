---
id: amazon-cold-start
section: amazon
order: 6
level: A
title: Amazon：冷启动商品 / 新 query，推荐和搜索怎么共用信号？
quick: >-
  新品和新 query 都缺行为数据，可以先从内容和相似对象学一个先验，再用真实曝光反馈更新。搜索与推荐共享 catalog
  embedding、替代关系和反馈定义，但排序目标与 position bias 要分开；探索预算也要统一记账。
tags:
  - Amazon
  - Cold Start
  - Search
  - Recommendations
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Addressing cold start in product search via empirical Bayes
    url: >-
      https://www.amazon.science/publications/addressing-cold-start-in-product-search-via-empirical-bayes
    type: primary
  - title: Treating cold start in product search by priors
    url: >-
      https://www.amazon.science/publications/treating-cold-start-in-product-search-by-priors
    type: primary
  - title: >-
      Behavioral feature boosting via substitute relationships for e-commerce
      search
    url: >-
      https://www.amazon.science/publications/behavioral-feature-boosting-via-substitute-relationships-for-e-commerce-search
    type: primary
---

## 可以这样回答

新品和新 query 都可以先靠内容及相似对象得到行为先验，再根据真实曝光更新。比如新品还没有点击率，直接按历史转化排序，它就很难获得第一批曝光。Amazon Science 的公开搜索工作用 Empirical Bayes 和替代品关系处理这个问题；推荐里的新 ASIN、新用户也有类似的信号缺失，但两边的最终目标仍要区分。

$\alpha,\beta$ 不是全局拍脑袋，而是用类目、价格带、品牌、文本相似邻居，从已有商品上学出来的先验。有曝光后再把 $m,n$ 更新进去。先验让新品能进候选；后验让真不行的品退回去。公开 A/B（约 50M query）写过新商品曝光和购买都有两位数相对提升，总购买还有小正，说明探索不必写成「牺牲 GMV」。

## 技术备查

新品和新 query 都可以先靠内容及相似对象得到行为先验，再根据真实曝光更新。比如新品还没有点击率，直接按历史转化排序，它就很难获得第一批曝光。Amazon Science 的公开搜索工作用 Empirical Bayes 和替代品关系处理这个问题；推荐里的新 ASIN、新用户也有类似的信号缺失，但两边的最终目标仍要区分。

## 先验怎样帮新品得到第一批曝光

学习排序里真正拉动短期名次的是 query–item 上的点击率、转化率。新品 $n$ 次曝光都没有，$m/n$ 未定义或方差炸。Empirical Bayes 的讲法：

$$
\hat{p}=\frac{m+\alpha}{n+\alpha+\beta}
$$

$\alpha,\beta$ 不是全局拍脑袋，而是用类目、价格带、品牌、文本相似邻居，从已有商品上学出来的先验。有曝光后再把 $m,n$ 更新进去。先验让新品能进候选；后验让真不行的品退回去。公开 A/B（约 50M query）写过新商品曝光和购买都有两位数相对提升，总购买还有小正，说明探索不必写成「牺牲 GMV」。

替代品是另一条共用信号：同一 query 下可替换的 ASIN，把它们的行为聚合成新品的暖启动特征。替代图来自联合购买、共同点击、类目属性，推荐的「买了还买」和搜索的 substitute 可以共用这张图，不要搜索团队做一份、首页推荐再做一份。

新 query（尾 query、新品牌词、季节词）镜像对称：query 侧没有点击统计。用改写到头 query、类目预测、query embedding 近邻，把头 query 的行为先验借过来。拼写和空格变体先走词法，见 `amazon-kendra-hybrid`，别把 `iphne 16` 当成语义冷启动。

## 搜索和推荐怎么分工

我会共享下面这些底层信号：

- **Catalog 内容塔。** 标题、图、品牌、类目路径的 embedding。双塔 item 塔本来就不该依赖用户历史，见 `amazon-two-tower`。同一向量既给搜索召回，也给「相似商品」推荐。
- **替代 / 互补图。** 搜索用来借行为特征，推荐用来填车和详情页。
- **反馈定义。** 点击、加购、购买、退货。搜索的 skip 和推荐的 impress-without-click 都要进同一特征存储，窗口和点时间对齐，见 `amazon-feature-store`。
- **探索预算。** 新品曝光配额、epsilon、或 bandit。搜索结果页和推荐槽位抢同一用户 attention，配额要统一记账，否则两边都「探索 2%」实际打了 4%。

最终目标和偏差处理则分别设计：

- **目标。** 搜索先相关性再转化；推荐更偏发现和 GMV。把推荐 CTR 模型直接当搜索 ranker，会出「相关但用户没搜这个」的货。
- **position bias。** 搜索第一位和推荐轮播的 propensity 不同，IPS / 位置特征不能抄。
- **新用户。** 推荐更痛（没历史）；搜索至少还有当前 query。新用户推荐走内容 + 类目热门 + 会话内点击，不要等画像。

双塔的 item 塔只用内容，新 ASIN 进索引后就能被语义召回。但精排若仍被历史行为主导，新品可能继续排到第二页。因此要把内容召回、先验行为特征和探索曝光一起设计，让召回与排序都能处理冷启动。

评测分别看新 ASIN 的曝光、购买和退货，尾 query 的零结果率与成功购买，以及老商品是否被挤掉过多。全局 GMV 容易被头部商品主导，掩盖冷启动效果；退货和差评也要进 acceptance checks，避免用低质量新品消耗客户体验。

相关：`amazon-lp-ml`。

## 追问

**先验会不会把垃圾新品推上天？**
会，如果 $\alpha,\beta$ 只看类目热度。要加卖家承诺、合规、图文质量，并设探索上限；后验几个负反馈就该打回。论文里总购买仍为正，是因为先验跟踪的是「同类真转化」，不是均匀随机曝光。
**没有替代品的真正新品呢？**
退回内容 embedding 和类目先验，接受更高不确定度，探索配额单独给。不要伪造替代边。
**搜索点击能不能当推荐标签？**
能当弱标签，但有 query 条件。无 query 的推荐要用「去掉 query 的边缘」或另训。直接拿搜索购买当推荐正例，会 overfitting 头 query 品。
**新 query 要不要上 LLM 改写？**
可以当召回扩充，但改写后仍要走词法保底，避免把品牌词改丢。延迟预算见 `amazon-p99-stream`；改写质量进 `amazon-titan-eval`，不要只看 BLEU。
