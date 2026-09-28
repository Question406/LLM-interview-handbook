---
id: design-recsys
section: design
order: 2
level: S
title: 设计：推荐系统召回-排序-重排，多目标与探索
quick: >-
  三截：召回保覆盖、排序打分、重排处理多样性和规则。多目标不要假装一个 AUC 能代表时长、点击和伤害。探索单独预算，否则反馈环只会推热门。训练-serving 一致性比再叠一层模型更值钱。
tags:
  - RecSys
  - Meta
  - Google
  - Ranking
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Deep Neural Networks for YouTube Recommendations
    url: https://dl.acm.org/doi/10.1145/2959100.2959190
    type: primary
  - title: Deep Learning Recommendation Model for Personalization and Recommendation Systems
    url: https://arxiv.org/abs/1906.00091
    type: primary
  - title: System Design in a Hurry
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

YouTube 双塔召回、Meta 信息流 / DLRM、Amazon 首页、Microsoft Feed 都会问这题。公开论文给的是「召回再排序」骨架；白板要的是候选规模、延迟、多目标冲突和探索。和广告近亲但目标不同：推荐优化长期体验，广告还要花广告主的钱，见 `design-ads-rank`。特征点查走 `design-feature-store`。

## 三截漏斗，数字先写上

我会先问：库存量级、每用户每次要露出几条、端到端 p95、要优化哪些业务指标、有没有监管/完整性红线。缺这些就画「双塔+XGBoost」，面试官会追问你候选从 $10^{8}$ 怎么到 10 条。

典型切法：

1. **召回。** 多路：双塔（用户塔 / 物品塔点积）、协同过滤、热门、图走几跳、编辑池。每路几百到几千，合并去重后 $O(10^{3})$。双塔用 ANN（HNSW / IVF）点查，用户塔在线算或缓存，物品塔离线灌索引。物品更新频率决定索引 SLO。
2. **排序。** 交叉特征、序列、多模态侧信息，DLRM 式稀疏 embedding + MLP。打分必须在预算内，例如 50–80 ms 打完两千条。这里才用到交叉，召回阶段交叉会爆。
3. **重排。** 多样性（同作者/同话题打压）、位置偏差修正、完整性规则、广告插入、探索槽位。规则在模型外面，不要把「政治敏感降权」默默塞进一个隐式 label。

冷启动：新物品走内容塔 + 探索流量；新用户走上下文和热门，不要等交互矩阵长好再服务。

双塔形状我会写上：用户塔输出 `[B, D]`，物品塔离线产出 `[N, D]`，在线用 ANN 取内积最大的 $k$ 个。$D$ 常见 64–256。排序模型才把交叉特征打成标量；不要在召回里对全库做 MLP。候选日志必须留下路标（哪一路召回的），否则你无法诊断「热门路把探索路打死」。

## 多目标和探索

线上要的不是一个 AUC。常见目标互相打架：点击 vs 完播 vs 停留 vs 隐藏/举报 vs 作者健康。我会写成显式加权

$$
s = \sum_i w_i \hat{m}_i
$$

$w$ 由产品定，并在 A/B 里动，不在训练 loss 里偷偷改。完整性（暴力、误导）是约束不是奖励：超过阈值直接不可露出，不参与加权。位置偏差：用户总点第一条，用 IPS 或位置特征，否则模型学会「排前面的就是好的」。

延迟反馈：完播、复购要小时到天。训练用窗口和重要性加权，serving 仍用当前特征。别把未来的完播漏进训练行，那是泄漏，线下怎好线上都会掉。

探索：纯贪心会把新物品和长尾掐死，反馈环放大头部。给召回或重排一个明确探索预算（$\varepsilon$-greedy、Thompson、或单独探索配额），探索流量也要完整性过滤。短视 CTR 上升、周留存掉，是没探索或权重只认点击的典型症状。

## 失败模式和指标

离线：召回 recall@$k$ / hit rate（注意随机切会泄漏，按时间切）；排序 AUC、logloss、校准；重排后的多样性、规则命中。线上：人均时长、互动、隐藏率、完整性事故、作者侧覆盖。校准差时，多目标加权没有物理意义，因为 $\hat{m}_i$ 不在同一尺度。

失败模式：训练-serving 特征不一致（一个用实时计数、一个用 T+1）；popularity bias；物品塔索引落后，新内容永远进不了 ANN；重排规则和模型对着干，离线增益被规则吃光。Meta / Google 风格是你能指出反馈环，而不是再报一个模型名字。

延迟反馈我会给一个具体错法：用「点击后 24h 完播」当 label，却把点击当时还没有的完播特征 join 进来。线下 AUC 会很好，上线完播掉。按时间切分还不够，还要点查 $t_{\mathrm{feat}} \le t_{\mathrm{event}}$，见 `design-feature-store`。

## 追问

- **为什么不端到端一个大模型打全库？** 延迟和算力不允许对 $10^{8}$ 物品做交叉。漏斗是延迟和算力约束。
- **多目标权重怎么定？** 产品给方向，用 Pareto / 网格在 A/B 上看护栏；不要把权重藏进 label 定义里事后解释。
- **探索会伤短期 CTR？** 会。把探索当成本，用留存和覆盖回收。不允许探索的系统，三个月后全是头部。
- **和特征平台怎么接？** 排序 p95 往往死在点查不是 GEMM。见 `design-feature-store`。
