---
id: google-ads-auction
section: google
order: 13
level: S
title: Google：广告拍卖 + 预测 CTR/CVR，校准为什么比「模型更大」先说
quick: >-
  排序分大约是出价 $\times$ 预测点击率 $\times$ 预测转化率 $\times$ 质量。预测若整体偏高一倍，你会买错位置、算错
  eCPM。ECE / 可靠性曲线先看；更大的模型如果更自信但更偏，钱先亏完。
tags:
  - Google
  - Ads
  - Auction
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
  - title: Internet Advertising and the Generalized Second-Price Auction
    url: https://www.nber.org/papers/w11765
    type: secondary
---

广告 MLE / 预测岗。McMahan 的「trenches」讲的是工业点击预测；拍卖理论是 GSP 那条线。面试把两段接上：预测进入出价，校准错误直接改分配和计费。搜广推记忆泛化见 `google-wide-deep`。

## 拍卖里模型站在哪

简化：每次展示，候选广告有出价 $b$、预测点击率 $p_{\mathrm{CTR}}$、有时还有 $p_{\mathrm{CVR}}$。排序分数近似

$$
\mathrm{score}=b\cdot p_{\mathrm{CTR}}\cdot p_{\mathrm{CVR}}\cdot q
$$

$q$ 是落地页 / 创意质量一类。Google 历史上是广义第二价格（GSP）的变体：你付的是「压过下一名所需」而不是自己的全价，但 谁赢、排第几 仍由 score 决定。第一价格化之后，预测偏差更直接影响实付金额。

eCPM 视角：平台要最大化 $p_{\mathrm{CTR}}\times$ 每点价值。$p$ 若系统性偏大，低价值广告被抬上去，高价值广告被挤走，长期拍卖效率掉。广告主侧：用你的 $p$ 做出价，偏高就超买，偏低就丢量。所以 pCTR 是经济量，不是排行榜上的任意单调分。

搜索 NDCG 可以容忍单调变换（排序对就行）。拍卖不行。$\sigma(z)$ 和 $2\sigma(z)$ 排序相同，付钱完全不同。这是「校准先于更大模型」的原因。

## 校准比容量先讲

校准：预测 0.1 的那一桶，真实点击是否约 10%。画可靠性图，算 ECE：

$$
\mathrm{ECE}=\sum_m \frac{|B_m|}{n}\left|\hat{p}_m-y_m\right|
$$

「View from the Trenches」的教训是：特征、偏差、校准、工程系统，比换一个更深的网络更常决定钱。现代网络还容易 过自信（Guo et al.）：NLL / AUC 变好，ECE 变差。

更大模型可以学到更好的排序（AUC、logloss 的排序部分）。若温度错了、切片漂移了（新广告、新设备、新位置），它会用更高的置信度犯同样的偏。上线第一周你按偏高的 $p$ 成交，预算烧完才发现 CTR 只有预测的一半。

做法，按优先级：

1. **切片校准。** 全局一组温度不够。位置、国家、设备、新广告 vs 老广告，偏的方向不同。分组统计 isotonic / Platt / 温度，且 **训练时的位置要对齐服务**。
2. **延迟转化。** CVR 标签几天后才到。用等待窗口、重要性加权，别把「还没回来」当负。
3. **再谈模型容量。** 交叉、深度、序列，用来提高分辨力。分辨力涨了仍要重新拟合校准层。Wide & Deep 的记忆侧经常是头部 ID 的准确率来源，见 `google-wide-deep`。

监控：预测均值 vs 实际 CTR（分切片）、ECE、校准后 AUC 不应掉、花费和胜率。只报 AUC 是红旗。

## 现场错法

把广告题答成「就是个二分类」。二分类可以只优化 AUC；拍卖要概率。说「单调就够，拍卖只看排序」：GSP 排序和定价都吃 $p$ 的绝对值。说「上 Transformer 点击率自然准」：容量不保证校准，尤其非平稳流量。

## 追问

- **AUC 很好但亏钱？** 排序对、概率偏。先校准再查出价和预算。
- **温度缩放够吗？** 全局温度救不了「新广告全偏高、品牌广告全偏低」。要分切片，或把偏差特征显式喂进模型。
- **和搜索 NDCG 冲突怎么权衡？** 广告槽位有质量阈值，避免高 pCTR 垃圾广告。搜索相关性见 `google-search-quality`。不要用一个 NDCG 代替 eCPM。
- **探索会不会弄坏校准？** 会。随机放量改变位置分布。校准集要含探索流量，或对策略做纠偏，否则线上 $p$ 对着旧策略拟合。
