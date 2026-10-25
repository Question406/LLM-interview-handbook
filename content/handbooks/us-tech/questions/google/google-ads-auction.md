---
id: google-ads-auction
section: google
order: 13
level: S
title: Google：广告拍卖 + 预测 CTR/CVR，校准为什么比「模型更大」先说
quick: "广告预测的概率会直接进入排序与出价，因此先检查校准，再谈模型容量。预测 0.1 的样本应有约 10% 点击率；若概率整体偏高，即使 AUC 好，也可能算错 eCPM、分错广告位和花错预算。"
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

广告 CTR/CVR 预测要先讲校准，因为概率直接参与排序、出价和计费。比如预测整体高了一倍，广告顺序可能没变，预算与成交决策却已经偏了。McMahan 的 Ad Click Prediction — a View from the Trenches 讨论工业点击预测，GSP 那条线解释拍卖，两部分在预测概率上接起来。

简化到每次展示，候选广告有出价 $b$、预测点击率 $p_{\mathrm{CTR}}$，有时还包括 $p_{\mathrm{CVR}}$，排序分可以先理解成出价 $\times$ 点击率 $\times$ 转化率 $\times$ 质量，近似为：

$$
\mathrm{score}=b\cdot p_{\mathrm{CTR}}\cdot p_{\mathrm{CVR}}\cdot q
$$

$q$ 表示落地页 / 创意质量。Google 历史上采用广义第二价格（GSP）的变体，支付的是压过下一名所需的价格，谁赢、排第几仍由 score 决定；第一价格化后，预测偏差会更直接影响实付金额。

eCPM 视角是最大化 $p_{\mathrm{CTR}}\times$ 每点价值。$p$ 系统性偏大，会抬高低价值广告、挤走高价值广告；广告主用它出价也会超买，偏低则丢量。搜索 NDCG 允许不改变排序的单调变换，拍卖需要概率的绝对值：$\sigma(z)$ 和 $2\sigma(z)$ 排序相同，付费结果却可能不同。

校准就是检查预测 0.1 的那一桶，实际点击是否约 10%。画可靠性图，并计算 ECE：

$$
\mathrm{ECE}=\sum_m \frac{|B_m|}{n}\left|\hat{p}_m-y_m\right|
$$

这里每个桶 $B_m$ 按样本占比加权，比较预测均值 $\hat{p}_m$ 与实际点击率 $y_m$。Guo et al. 指出，现代网络可能在 NLL / AUC 变好的同时更过自信、ECE 变差。View from the Trenches 也说明，特征、偏差、校准与工程经常比继续加深网络更影响业务。

我会先按位置、国家、设备、新旧广告切片，拟合 isotonic / Platt / 温度校准，并让训练位置分布与服务对齐。全局温度处理不了新广告偏高、品牌广告偏低这类方向不同的偏差。CVR 还要处理延迟标签，用等待窗口或重要性加权，避免把尚未回传的转化算负例。然后再通过交叉、深度和序列提高模型分辨力，容量变化后重新拟合校准层；Wide & Deep 的记忆侧也常贡献头部 ID 准确率。

上线按切片看预测均值与实际 CTR、ECE、校准后 AUC、花费和胜率。若第一周已按偏高概率成交，预算耗尽后才发现实际 CTR 只有预测的一半，单看 AUC 就发现得太晚。

## 追问

**AUC 很好却亏钱，先查哪里？**
先查概率校准，再查出价和预算。排序正确不能保证概率值正确，更大的 Transformer 也不自动解决非平稳流量下的校准。

**探索会影响校准吗？**
会。随机放量改变位置分布，校准集应包含探索流量，或做策略纠偏，避免一直拟合旧策略。

**如何兼顾搜索质量？**
广告槽位还需质量阈值，防止高 pCTR 的低质广告。搜索相关性和 eCPM 分开评，不能用一个 NDCG 代替两者。

相关：`google-wide-deep`、`google-search-quality`
