---
id: data-preference-ties-uncertainty
section: data
order: 218
level: A
title: 偏好标注中的 tie 与不确定该丢掉、当相等，还是进特殊 loss？
quick: >-
  Tie 别丢也别强行选边，当成「无差异」这第三类来用：可以进相等损失、降权成 soft labels，或者只拿来 calibration
  评分。强行选赢家等于把标注噪声写成 hard labels，全丢掉又会让模型继续为微小风格差拉分。同时报告 tie
  比例、分层一致性，并结合标注者间一致性判断。
tags:
  - Preference Data
  - Annotation
  - Uncertainty
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---

我会把 tie 当成第三类标签保留下来，按来源分别处理：高置信的严格序才进硬 DPO，tie 进相等损失或者降权，缺上下文造成的「不确定」单独标成需要澄清。直接丢掉和强制标注员选边都会出问题。

比如两个回答都对，一个多了一段礼貌的总结。强制选边的话，标注员基本是在随机投票，这就等于往训练里注入噪声；把这类 pair 全丢掉，训练集只剩「一眼能分」的样本，模型学不到「这种风格差别不值得拉大 logit」，长度和文风偏好会被放大。

从公式上看也是这样。DPO 用的 Bradley-Terry 假设是严格序：

$$
p(y_w \succ y_l)=\sigma\Big(\beta\log\frac{\pi_\theta(y_w)}{\pi_{\mathrm{ref}}(y_w)}-\beta\log\frac{\pi_\theta(y_l)}{\pi_{\mathrm{ref}}(y_l)}\Big),
$$

tie 不满足这个式子，硬塞一个随机赢家，$\pi_\theta$ 就会去拟合噪声。所以别假装总有赢家。诊断思路和 `data-annotator-agreement` 一样，先分清是任务本身难分、评分标准的几个维度互相冲突，还是纯随机噪声。

## 先分层，再决定怎么进 loss

标注界面就要给够选项：明显更好、略好、难分、都差。略好和明显更好别压成同一个 $0/1$，否则硬偏好的覆盖率是拿精度换来的。tie 和低置信样本有三种用法。一是当相等处理，让两个回复的隐式奖励接近，比如当 $|r_1-r_2|\lt\delta$ 时用 $\mathcal{L}_{\mathrm{tie}}=(r_1-r_2)^2$，或者在 list-wise 里允许并列，别编出一个全序。二是降权，用 soft labels $p(y_1\succ y_2)=0.5$，梯度很小，零信息的 pair 不会主导 batch。三是只用来做评测 calibration，不进训练，检查 reward model（RM）或 judge 会不会给无差异的回答排出不合理的序，`fund-judge` 里讲的 verbosity 偏差往往就在这里暴露。

「不确定」如果来自缺上下文，加一个「需更多信息」的选项，别把它标成偏好。只有同一个人重标都不稳定的真随机样本，才隔离出去。

工程上最小的改动是把 tie pair mask 掉，另外加相等损失；也可以对 $\{y_w,y_l,\mathrm{tie}\}$ 做三路分类。List-wise 或排序学习天然允许并列名次，比把所有 pair 都二值化更诚实。这题和分歧题的分工是：`data-annotator-agreement` 决定谁能进硬监督，这题决定无差异标签在 loss 里怎么写。

## 报告和容易出错的地方

报告里要有 tie 率、分层 IAA，以及去掉 tie 以后 win-rate 还剩多少。tie 率 $30\%$ 却宣称 $70\%$ 一致，这个数字就是假的。发布前单独报 RM 在 tie 切片上的准确率，这个切片上准确率很高，可能是 overfitting 了强制投票的结果。

强制选边还会污染 judge distillation：教师被逼着投票，学生就学会在无差异区也给极端分，基于阈值的筛选随之变得不稳。标注界面如果默认把「略好」做成必须二选一，tie 率会被系统性压低，IAA 看着提高了，其实是造出了不存在的偏好顺序；应该允许并列，事后抽检默认项有没有被滥用。另外，产品要求的回答风格没写清楚时，比如简短和完整哪个优先，tie 反映的是目标冲突。风格类 tie 多，说明 persona 没写进指南，先改 rubric 和目标，再谈 loss 权重。

## 追问

**全部丢掉 tie 有什么代价？**
训练集变成「一眼能分」的样本，模型在近似等价的回复上照样为长度、列表、礼貌程度拉分，线上表现就是啰嗦。

**为什么不能强制选边？**
那等于把标注噪声写成 hard labels。DPO 对这类 pair 的梯度并不比真偏好小，噪声会被放大。

**$\delta$ 怎么定？**
用重复标注的分数差分布来定：人类自己也说不清的分差区间就是 $\delta$。别在验证集上刷 win-rate 来调。

**List-wise 怎么处理并列？**
允许相同的秩，loss 只惩罚逆序，不惩罚并列。别把并列展开成假的全序 pair。

**不确定的样本要不要进训练？**
缺上下文的不确定，改成澄清动作的标签；只有「两个都不错」的 tie 才进相等损失。两者混在一起，模型会把「该问一句」学成「随便挑一个」。
