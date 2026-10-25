---
id: meta-ads-calibration
section: meta
order: 8
level: A
title: Meta：广告模型校准（predicted vs observed），logloss 和 AUC 各管什么
quick: "广告拍卖需要概率的绝对值，因此既要排序好，也要 predicted 与 observed 对得上。AUC 对单调变换不变，校准要看报 $0.1$ 的样本是否真有约 $10\\%$ 点击；logloss 同时约束概率质量，线上还需独立校准、分组监控和回滚。"
tags:
  - Meta
  - Ads
  - Calibration
  - Logloss
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Practical Lessons from Predicting Clicks on Ads at Facebook
    url: https://dl.acm.org/doi/10.1145/2648584.2648589
    type: primary
  - title: Meta’s approach to machine learning prediction robustness
    url: https://engineering.fb.com/2024/07/10/data-infrastructure/machine-learning-ml-prediction-robustness-meta/
    type: primary
  - title: On Calibration of Modern Neural Networks
    url: https://arxiv.org/abs/1706.04599
    type: secondary
---

广告模型要校准，是因为拍卖使用预测概率的绝对值。模型即使排序不错，若所有点击概率都偏高，也可能让广告主多花钱、预算提前耗尽；偏低则可能错失本应赢下的拍卖。

以点击计价时，拍卖值近似是 $bid \times pCTR$，其中 $pCTR$ 是预测点击率；再计入转化概率时，简化期望价值可写成 $\mathrm{value} \approx bid \times pCTR \times pCVR$，而 AUC 只看正样本是否排在负样本前，对单调变换不变。把所有概率变成 $p^{10}$，AUC 可能不动，期望价值却变了。因此还要检查预测概率 $p$ 为 $0.1$ 的样本，实际 CTR 是否也接近 $0.1$。

Reliability diagram 横轴为预测分组统计、纵轴为观测 CTR，靠近对角线说明校准较好。ECE 是各桶 $|pred - obs|$ 的加权平均，仍要看具体桶，例如预测 $0.2$ 却只点击 $0.08$，一个总分会藏住这种问题。二元交叉熵为：

$$
\ell = -y\log p - (1-y)\log(1-p)
$$

Logloss 是 proper scoring rule，真实条件概率使期望损失最小，会同时惩罚排序错误与概率失准。AUC 上升、logloss 变差，可能是分数拉伸过度。相反，常数 $p=\bar{y}$ 可以全局校准却只有 $0.5$ AUC，两者要一起看，logloss 也不能简单称为 AUC 的平滑版。

## 如何部署和验证

主模型可用 GBDT、深度网或 DLRM，先学排序与粗概率，再接 Platt scaling、isotonic 或按位置、广告类型、国家分组的分段校准，见 `meta-dlrm`。2014 Practical Lessons 讨论新鲜数据、在线特征与强树模型，也强调 predicted vs observed；Meta 2024 稳健性博客继续把校准作为实时监控与自动缓解的一部分，特别提醒未接合数据上的实时训练更脆弱。

节日、新广告形态或接合延迟改变分布，校准器也要滚动重估，并有延迟监控与回滚。评估使用时间切分 holdout，按位置、设备、新广告切片，不能用同一天训练数据画一张好看的图。位置偏差不修，模型可能把“排前面所以点击多”当成概率规律，换位置就漂。

离线同时报 AUC 与 NE（normalized entropy，logloss 相对熵基线，广告中常用作主指标），再给校准图和分组 CTR。全局正常、新广告主桶失准，仍会造成问题。线上看花费、CPI、预算耗尽速度、投诉和时延，AUC 涨但花费飙升时先查校准。Feed 的加权多目标也需要概率质量，见 `meta-newsfeed-rank`，一般排序为何盯 logloss 见 `meta-ranking-logloss`。

## 追问

**温度缩放够吗？**
同分布的过度自信常可用单一 $T$ 调 logits，但不提高 AUC，分布变了要重估。

**点击延迟会怎样？**
尚未回传的点击让观测 CTR 偏低，校准器会错误下调概率，应使用延迟窗口或延迟模型。

**CTR 与 CVR 怎样处理？**
分别校准两个头再相乘。CVR 更稀疏、延迟更长，不能直接套 CTR 校准器。

**和 Feed 的 $V=\sum w_k p_k$ 一样吗？**
共同点是加权概率要校准，拍卖约束与完整度硬过滤则不同。
