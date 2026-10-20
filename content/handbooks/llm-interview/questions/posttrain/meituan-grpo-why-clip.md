---
id: meituan-grpo-why-clip
section: posttrain
order: 180
level: A
title: 美团秋招二面：GRPO 为什么还要 clip？SFT 后直接上会不会仍不稳定？
quick: "Clip 限制一步更新幅度，防止高优势样本使 $\\rho$ 变化过大。监督微调（SFT） 只给了格式和基本能力，on-policy 采样分布仍会偏，组内方差大时一样震荡。优势可改过程奖励、过滤全同组或换 DAPO 动态采样。"
tags:
  - Meituan
  - GRPO
  - Clip
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法二面-秋招面经
    url: https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“GRPO为什么要做clip，直接用SFT后的模型还会不稳定吗？优势度可以怎样改进？”**

常见误区是：答「有 SFT 就可以去掉 clip」或「没有 critic 就不需要信任域」。GRPO 只换了 advantage 的构造，clipped importance-weighted surrogate 原样留下。组内 $A$ 很大时，不 clip 会一步毁掉刚通过监督微调（SFT）学会的格式。SFT 降低的是解析噪声的先验，不是稳定性证明。这题三问要一起答：为什么 clip、SFT 后为何仍抖、优势怎么改。后两问不是让你把 clip 拆掉。

## 1. Clip 管的是相对 $\pi_{\mathrm{old}}$ 的一步偏离

Surrogate 与 PPO 同构：

$$
L(\theta)=\mathbb{E}\big[\min\big(\rho\hat{A},\ \mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\hat{A}\big)\big],
\quad \rho=\frac{\pi_\theta}{\pi_{\mathrm{old}}}.
$$

$\hat{A}\gt 0$ 时限制 $\rho$ 不要过大，别把好样本概率变化过大；$\hat{A}\lt 0$ 时限制 $\rho$ 不要过小，别把坏样本概率压没后数值不稳。Clip 的是目标函数，不是把真实概率比强制截进区间。没有 价值评估模型（critic） 不等于没有信任域：组均值 baseline 只降了「相对谁」的方差，没有限制 $\theta$ 相对行为策略走多远。多 epoch 复用同一批 采样轨迹（rollout） 时 $\rho$ 更容易偏，clip 更不能省。$\varepsilon$ 太大近似未 clip；太小则正优势涨不动，探索死。

组内标准化会让 clip 更必要：$\sigma$ 很小的组里，少数差异会被放大成巨大 $\hat{A}$，再乘未裁剪的 $\rho$，少数轨迹主导梯度。这是 GRPO 特有的放大，不是 PPO 才需要 clip。

## 2. SFT 后仍会不稳：采样分布和奖励噪声都还在

SFT 给了格式和基本能力，但 on-policy 采样仍会偏出示范：奖励噪声、组内全对 / 全错、KL / 熵塌缩、难度突变、parser 偶发零分。高 $\hat{A}$ 乘未裁剪 $\rho$ 会让少数轨迹主导。失败表现是 clip fraction 打满、熵骤降、格式合法率掉。SFT 与 强化学习（RL） 的模板不一致时，看起来像算法不稳，其实是分布一开始就错了。

「直接用 SFT 后的模型」不稳定，还因为 SFT 的曝光偏差：训练看金标准前缀，RL 看自生成前缀，一开始 rollout 质量方差就大。这不是去掉 clip 能修的，要课程和 验证器（verifier） 稳定。

## 3. 改进优势，而不是拆 clip

过程分让「全错组」内部仍可排序；长度归一减轻长回复对梯度的主导；过滤 $\sigma\approx 0$ 的组；增大 $G$；DAPO 的 clip-higher、动态采样、token 级归约。这些改的是 $A$ 的质量和哪些样本进 batch，替代不了 clip 对 $\rho$ 的限制。Clip-higher 是改 $\varepsilon$ 的不对称，不是取消 clip。验收看 clip fraction、KL 到 old、holdout 格式和成功率，而不是训练 $L$ 是否更平滑。

方法失败：过滤后有效 batch 过小；过程分可 hack；clip-higher 过大等于没 clip。改优势之前先确认 verifier 对同一轨迹重打分一致。

## 追问

- **Advantage 标准化会不会让 clip 更必要？** 会。小 $\sigma$ 放大 $A$，更需要限制 $\rho$。
- **GSPO 的序列 clip 还要 token clip 吗？** 作用层不同；说清 clip 在 $\rho_t$ 还是 $s(y)$。
- **能不能只用 KL 不用 clip？** KL 相对 $\pi_{\mathrm{ref}}$，clip 相对 $\pi_{\mathrm{old}}$，不是同一个约束。可以并存，互相替代会漏掉一步偏离。
- **SFT 很强是否可加大 $\varepsilon$？** 可以略放宽，但要用 clip fraction 和格式率看，不要按「SFT loss 低」决定。
