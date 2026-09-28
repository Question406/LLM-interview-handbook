---
id: meta-ads-calibration
section: meta
order: 8
level: A
title: Meta：广告模型校准（predicted vs observed），logloss 和 AUC 各管什么
quick: >-
  拍卖吃的是 $pCTR$ 的绝对大小：出价大约是 $bid \times pCTR$。AUC 只看排序，对单调变换不变；校准看的是「报
  $0.1$ 的那一桶是不是真点 $10\%$。Logloss 是 proper scoring rule，同时罚排序和校准。线上还要有独立的校准层和监控。
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

广告 MLE 的高频题。2014 年的 Practical Lessons 已经把 Facebook 点预测的工业约束写清楚：特征、实时、校准。2024 年工程博客又把「预测稳健性」收成监控和自动缓解，校准是其中一块。和 Feed 多目标（`meta-newsfeed-rank`）同源：都要用概率，不只用名次。更一般的排序为什么盯 logloss，见 `meta-ranking-logloss`。

## 拍卖为什么要校准，而不只要 AUC

简化：广告排序/计费用的是期望价值，形状像 $\mathrm{value} \approx bid \times pCTR \times pCVR$。$p$ 整体偏高，广告主超花、预算提前烧完；$p$ 整体偏低，该赢的拍卖赢不到。这是**水平**问题。AUC 只问正样本是否排在负样本前面，对任意单调变换不变：把所有 $p$ 变成 $p^{10}$，AUC 可以不动，拍卖已经毁了。

校准问的是：模型说 $0.1$ 的那一桶，观测 CTR 是不是也在 $0.1$ 附近。画 reliability diagram（横轴预测分桶，纵轴观测点击率），对角线上是校准好。ECE 是各桶 $|pred - obs|$ 的加权平均。面试要能指出「$0.2$ 那一桶实际只有 $0.08$」这种形状，不要只报一个 ECE 数字。

Logloss（二元交叉熵）

$$
\ell = -y\log p - (1-y)\log(1-p)
$$

是 proper scoring rule：期望损失在真实条件概率处最小。它同时惩罚排反和校准差。AUC 涨、logloss 恶化，典型就是分数被拉伸、校准崩了。现场就说这句话，不要把 logloss 说成「AUC 的平滑版」。

## 工业上怎么做校准层

主模型（GBDT / 深度网 / DLRM 骨架，见 `meta-dlrm`）先学排序和粗概率。上面再接一层**校准器**：Platt scaling、isotonic、按校准键（位置、广告类型、国家）分桶的分段校准。2014 年论文的教训是：数据新鲜、特征在线、树模型很强，但上线仍要盯 predicted vs observed。

2024 年稳健性博客把校准写成实时监控 + 自动缓解：流量分布一变（节日、新广告形态、接合延迟），校准层比主模型更敏感。他们还提到未接合数据上的实时训练，比等点击回传更脆。面试不必背内部系统名，要能说出：**校准是独立组件，要有延迟监控和回滚，不是训练结束算一次 ECE。**

常见错法：用同一天训练数据画校准图，一定好看。要用时间切分的 holdout，并且按位置、设备、新广告切片。位置偏差不修，校准会把「靠前所以点得多」写进 $p$，换到新位置就漂。

## 和 AUC 怎么一起报

我会拆：

- **AUC / NE（normalized entropy）**：排序和整体预测质量。NE 本质是 logloss 相对熵基线，广告里比 AUC 更常当主离线指标。
- **校准图 + 分桶 CTR**：给拍卖看。全局校准好、新广告主那一桶崩了，仍然会出事故。
- **线上**：花费、CPI、预算耗尽速度、广告主投诉。离线 AUC 涨、花费飙，先查校准。

不要说「校准好了 AUC 就一定好」。常数预测 $p=\bar{y}$ 校准完美，AUC 是 $0.5$。两个指标管两件事。

## 追问

- **温度缩放够不够？** 对 in-distribution 的过度自信常常够，一个 $T$ 乘 logits。分布一变 $T$ 失效，要滚动重估。它不提高 AUC。
- **点击延迟怎么影响校准？** 当天未回传的点击会让观测 CTR 偏低，校准器会往下压 $p$。要用延迟窗口或延迟模型，否则晚上的校准和中午的不是同一个量。
- **多目标广告（CTR 和 CVR）？** 两个头分别校准，再相乘。CVR 更稀、更延迟，校准更难；用 CTR 的校准器去套 CVR 会错。
- **和 Feed 的 $V=\sum w_k p_k$ 同构吗？** 同构的是「加权概率需要校准」。不同构的是拍卖约束和完整性硬过滤。
