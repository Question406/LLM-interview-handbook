---
id: meta-newsfeed-rank
section: meta
order: 6
level: A
title: Meta：News Feed 排序，多目标（停留、互动、违规）怎么权衡
quick: >-
  先级联缩小候选，再用多任务头预测点赞、评论、停留、隐藏、举报等，合成 $V=\sum_k w_k \hat{p}_k$。互动和停留是加权，违规常常是硬过滤或强惩罚，不能和
  like 丢进同一个 softmax。权重靠线上实验调，不是离线 AUC 最大。
tags:
  - Meta
  - News Feed
  - Ranking
  - Multi-objective
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: News Feed ranking, powered by machine learning
    url: https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/
    type: primary
  - title: Scaling the Instagram Explore recommendations system
    url: https://engineering.fb.com/2023/08/09/ml-applications/scaling-the-instagram-explore-recommendations-system/
    type: primary
  - title: Client-side ranking to more efficiently show people stories in feed
    url: https://engineering.fb.com/2016/10/20/networking-traffic/client-side-ranking-to-more-efficiently-show-people-stories-in-feed/
    type: secondary
---

Feed / Integrity / Ranking MLE 的标准设计题。2021 年工程博客把 News Feed 写成「库存 → 多任务预测 → 加权合成 → 多 pass」，足够当口试骨架。不要编一轮具体 onsite 的题面；也不要背一个已经过时的特征名单。

## 级联，而不是对一万条跑大网

博客里的形状：一个人打开 Feed，库存可以上千。不能对每条都跑最贵的多任务网。

- **Integrity 先行：** 违规、垃圾、敏感类用独立模型或规则。很多是硬淘汰，不是「减 0.01 分」。把违规当一个和 like 对打的普通头，权重稍一漂就会漏放。
- **Pass 0：** 轻量模型，从上千收到大约几百，要高召回。
- **Pass 1：** 主模型，候选**独立打分**（没有「已经出了三条视频」这种列表上下文）。
- **Pass 2：** 上下文，做类型多样性、作者打散、已看过。这里才允许列表级特征。

Instagram Explore 公开叙述是同一类两阶段：检索把海量库收到几百，再精排。面试画这张漏斗，比纠结某一层用 GBDT 还是 Transformer 更像 Meta。

## 多目标：先预测，再合成，别一上来 Pareto 课

主模型是多任务：对同一条 $(user, item)$ 预测很多 $Y_k$：点赞、评论、分享、点击、停留、隐藏、举报、完播，等等。共享底层表示，头可以是独立 tower。损失通常是各头 logloss / 回归的加权和，校准见 `meta-ranking-logloss`。

合成公开写成线性：

$$
V_{ijt} = \sum_k w_k \hat{p}_{k,ijt}
$$

这有一个好性质：一个用户几乎从不点赞，则 $\hat{p}_{\mathrm{like}}\approx 0$，这一项自然贡献很小，不必手调「给这个人关 like 权重」。停留（dwell）是连续量，常先变换再进 $V$，不要和 CTR 头直接加。

权衡怎么说：

- **互动**（like / comment）容易刷、也容易让模型推诱导点击的内容。
- **停留** 更接近「看完了」，但会偏长视频、偏标题党。
- **负反馈**（hide / report）权重要足够大，否则正反馈样本多几个数量级，模型会忽略。
- **违规 / 内容安全：** 独立约束。可以 $V$ 里加很大的负项，但线上仍要阈值过滤；这两种是互补，不是二选一。

$w_k$ 不是离线网格搜索的终点。它们改的是产品，要用 A/B（`meta-ab-peeking`）看时长、互动、内容安全投诉、会话深度。离线 AUC 涨、线上 hide 涨，就是权重或标签定义错了。

## 一个具体错法

常见误区是：把所有目标做成一个多类 softmax（「这条是 like 还是 dwell」）。这些事件**不互斥**，一条视频可以又看完又点赞又被别人举报。要用多标签 / 多头。另一个常见误区是：只用点赞训，再口头说「我们也关心健康」：没有负反馈标签和内容安全检查通道，排序模型就无法学到这些目标。

延迟：Pass 1 对几百条并行打分，特征和 embedding 要能缓存；客户端还可以对已下载的故事再排一次（2016 年博客），那是工程，见 `meta-concurrency-feed`。广告插入走单独校准和竞价，见 `meta-ads-calibration`，不要把 pCTR 和 like 概率当同一个 $w$ 能直接加的量。

## 追问

- **权重会不会过拟合实验平台？** 会。一次只动少量 $w_k$，看护栏指标（内容安全、时长、投诉）而不是只看主指标。
- **探索怎么做？** 纯贪心 $V$ 会让新作者和新话题难以获得曝光。用随机探索、Thompson、或单独的 exploration 槽，并和完整性过滤同时存在。
- **标签延迟怎么办？** 停留和内容安全标签比点击慢。训练要用合适的窗口和延迟校正，否则模型会追短平快互动。
- **和 DLRM 是同一个模型吗？** 不是。DLRM（`meta-dlrm`）是稀疏推荐骨架；Feed 是级联 + 多任务 + 规则。骨架可以共享 embedding 思路，产品目标完全不同。
