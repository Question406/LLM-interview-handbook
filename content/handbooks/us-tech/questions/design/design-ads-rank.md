---
id: design-ads-rank
section: design
order: 4
level: A
title: 设计：广告预测与拍卖，校准、延迟、探索
quick: >-
  预测的是钱：pCTR / pCVR 必须校准，否则拍卖排序和出价全歪。延迟预算主要死在特征点查。探索要单独记账，避免只训「被展示过的广告」。拍卖规则和模型分开讲，不要把 GSP 画成一层 softmax。
tags:
  - Ads
  - Google
  - Meta
  - Calibration
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Ad Click Prediction — a View from the Trenches
    url: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/41159.pdf
    type: primary
  - title: On Calibration of Modern Neural Networks
    url: https://arxiv.org/abs/1706.04599
    type: primary
  - title: System Design in a Hurry
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

Google Ads、Meta Ads、Amazon 广告、Microsoft Bing Ads 的 MLE 白板常见题。McMahan 那篇 trenches 论文的精神是：特征、校准、系统和延迟，不是再发明一个网络。Hello Interview 式系统题会把拍卖和预测绑在一起问。不是某次现场逐字题。推荐漏斗同构见 `design-recsys`，但广告的 label 是钱，校准失败直接错账。

## 预测、拍卖、钱的单位

我会先问：计费是 CPC / CPM / CPA、是否有转化延迟、候选是怎样召回的、端到端预算（常见是几十毫秒级预测 + 拍卖）、监管（品牌安全、频次）。然后把链路拆开，避免画成「一个模型输出广告」。

1. 候选。 广告主定向、库存、预算、频次、品牌安全先过滤，再对剩下做 pCTR / pCVR。全库神经网络打分不现实。
2. 预测。 点击 $\hat{p}_{\mathrm{CTR}}$、转化 $\hat{p}_{\mathrm{CVR}}$（常级联，因为转化以点击为条件）。训练 logloss 或交叉熵，但上线看的是钱，不是 AUC 单点。
3. 排序分。 例如 $\mathrm{eCPM} \propto \hat{p}_{\mathrm{CTR}} \times \mathrm{bid}$（CPA 再乘转化）。有的系统对 bid 做幂次 $\alpha$ 来折中广告主价值和用户体验。$\alpha$ 是产品旋钮，要 A/B，不要写进网络最后一层假装学到了。
4. 拍卖。 一价或 GSP：排序用 eCPM，扣费按规则，不一定等于 bid。模型和拍卖是两个模块。把 GSP 画进 softmax 里，面试官会认为你没做过广告。

延迟转化：购买可能 T+1 到 T+7。用窗口、延迟校正、或两阶段（点击模型实时、转化模型滞后更新）。把未观察的转化当负例，模型会系统性低估高延迟品类。

## 校准和延迟

校准：分桶后 $\hat{p}$ 的均值要贴近真实点击率。ECE / 可靠性图是广告题必提的图，比「我们 AUC 0.9」重要。不准的后果：高估的广告占满库存、广告主赔钱或平台少收、探索也歪。上线用 Platt / 保序回归按位置、设备、广告类型分层校准，因为绝对概率进了 eCPM。

$$
\mathrm{ECE} = \sum_b \frac{n_b}{n} \lvert \mathrm{acc}_b - \mathrm{conf}_b \rvert
$$

总体 ECE 低不够：新广告、新位置、新设备要单独看。拍卖里 0.02 的 CTR 偏差乘上高 bid，就是真金白银。

延迟：特征点查往往占掉大半预算，模型前向反而小。用户即时特征（刚搜了什么、刚买了什么）要有新鲜度 SLO，过期特征和训练不一致，见 `design-feature-store`。p95 / p99 超了就降级：砍交叉特征、砍候选、用缓存的用户塔，不要拖住整页。预测超时返回的默认分必须保守，乱给 0.5 会把拍卖打穿。

探索：只训练被展示的广告，是选择偏差。用随机流量、Thompson、或偏差校正（IPS）。探索要受品牌安全和预算约束，不能拿违禁广告练胆。短期 eCPM 可能掉，长期校准和覆盖会回来，和推荐一样要单独记账。

## 失败模式

- 校准在总体很好、在新广告主或新位置很差，钱从这漏。
- 训练用「点击=1、没点=0」，忽略没获得展示的广告，模型变成「学竞价胜出者」。
- 频次和疲劳没进重排，用户被同一条广告打穿，体验指标掉、广告主还以为模型准。
- 完整性 / 违禁分类延迟于创意上传，违法创意先赢几次拍卖再下线，是事故。
- 日志和训练时钟不一致，用了点击之后才生成的特征，泄漏。

离线 AUC 用来看排序，线上看 RPM、广告主 ROI、用户隐藏、违规率、延迟。缺校准报告的广告模型，我不会同意全量。

错法：购买 T+7 才到，训练在 T+1 把没转化当负例，高客单品类会被系统性压价。用延迟校正或「只对已成熟窗口算 CVR」；未成熟样本不要当硬负。探索流量要记账：随机 1% 的 RPM 损失 vs 新广告主冷启动覆盖，产品得认这笔成本。

## 追问

- **AUC 很高但收入掉？** 先看校准和位置分布。AUC 不关心绝对概率，拍卖关心。
- **为什么探索伤短期收入还要做？** 否则新广告和新广告主进不去，长期库存质量塌。
- **和推荐模型能否共用？** 底层特征平台可以共用，目标和校准不行。点击内容不等于点击广告。
- **p99 超时怎么降级？** 预设保守分、缩小候选、跳过可变特征；降级策略要可复盘，不能静默。
