---
id: data-preference-ties-uncertainty
section: data
order: 218
level: A
title: 偏好标注中的 tie 与不确定该丢掉、当相等，还是进特殊 loss？
quick: >-
  Tie 是信息不是垃圾。可学「无差异」区间、降权或用于校准；强行拆成胜负会注入标注噪声，直接丢光则浪费「别过度区分」的监督。报告 tie 率与分层 consistency，并与 annotator agreement 一起看。
tags:
  - Preference Data
  - Annotation
  - Uncertainty
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

陷阱是把 tie / 「不确定」当成脏数据丢掉，或强制标注员选边再送进 DPO。两个回答都可接受或都差时，强制胜负等于注入随机噪声；全部丢光则模型缺少「别为微小风格差拉大 logit」的监督，容易放大长度和文风。DPO 的 Bradley-Terry 假设是严格序

$$
p(y_w \succ y_l)=\sigma\Big(\beta\log\frac{\pi_\theta(y_w)}{\pi_{\mathrm{ref}}(y_w)}-\beta\log\frac{\pi_\theta(y_l)}{\pi_{\mathrm{ref}}(y_l)}\Big),
$$

tie 并不满足该式。正确做法是把无差异当成第三类，而不是假装总有赢家。这和 `data-annotator-agreement` 同一诊断：先分清任务本身难分、rubric 打架，还是真随机噪声。

## Tie 是难度信号，先分层再入 loss

界面应提供「明显更好 / 略好 / 难分 / 都差」。高置信严格序才进硬 DPO。Tie 与低置信三种用法：

1. **第三类 / 相等**：鼓励两个回复的隐式奖励接近，例如当 $|r_1-r_2|\lt\delta$ 时用 $\mathcal{L}_{\mathrm{tie}}=(r_1-r_2)^2$，或在 list-wise 里允许并列，不编造全序。
2. **降权**：软标签 $p(y_1\succ y_2)=0.5$，梯度很小，避免零信息 pair 主导 batch。
3. **只用于评测校准**：不进训练，用来测 RM / judge 是否在无差异区乱排序（`fund-judge` 的 verbosity 往往在这里暴露）。

「不确定」若来自缺上下文，应加第三选项「需更多信息」，而不是标成偏好。真随机（同一人重标也不稳）才隔离。不要为了硬偏好覆盖率，把略好和明显更好压成同一 $0/1$。

## 和 BT / DPO 怎么接

标准 DPO 对 tie 没有项：硬塞随机赢家会让 $\pi_\theta$ 拟合噪声。工程上最小改动是 mask 掉 tie pair，另加相等损失；或对 $\{y_w,y_l,\mathrm{tie}\}$ 做三路分类。List-wise / 排序学习天然允许并列名次，比把所有 pair 二值化更诚实。报告必须含 tie 率、分层 IAA、以及「去掉 tie 后 win-rate 还剩多少」——tie 率 $30\%$ 却宣称 $70\%$ 一致，数字是假的。

强制选边还会污染 judge 蒸馏：教师被逼投票，学生学会在无差异区仍给出极端分，阈值门禁会抖。产品 persona 没写清时（要短还是要全），tie 其实是目标冲突，应改 rubric，而不是加 loss 权重。

## 面试收口

保留 soft / tie，让模型学会「不必区分」；硬偏好只吃高一致严格序。丢掉全部 tie 会失去边界；强制拆边是在教噪声。和分歧题的分工：`data-annotator-agreement` 决定谁该进硬监督；本题决定无差异标签在 loss 里怎么写。发布前单独报 tie 切片上的 RM 准确率——那里「很准」往往是过拟合强制投票。标注界面把「略好」默认成必须二选一会系统性压低 tie 率，看起来 IAA 变高，实际是在制造假序；应允许并列并事后抽检默认项是否被滥用。风格类 tie 多，说明 persona 没写进指南，先改目标再改 loss。

## 追问

- **全部丢掉 tie 有什么代价？** 训练集变成「一眼能分」，模型在近等价回复上仍会为长度、列表、礼貌程度拉分，线上表现为啰嗦。
- **为什么不能强制选边？** 等于把标注噪声写成硬标签。DPO 对这类 pair 的梯度并不比真偏好小，噪声会被放大。
- **$\delta$ 怎么定？** 用重复标注的分数差分布：人类也说不清的分差区间当 $\delta$，不要在验证集上刷 win-rate 来调。
- **List-wise 如何处理并列？** 允许相同秩，loss 只惩罚逆序，不惩罚并列。不要把并列展开成假的全序 pair。
- **不确定要不要进训练？** 缺上下文的不确定应改成澄清动作标签；只有「两个都不错」的 tie 才进相等 loss。混在一起会把「该问一句」学成「随便挑一个」。
