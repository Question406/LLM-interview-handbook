---
id: meituan-grpo-why-clip
section: posttrain
order: 180
level: A
title: 美团秋招二面：GRPO 为什么还要 clip？SFT 后直接上会不会仍不稳定？
quick: >-
  GRPO 只换了 advantage 的构造，信任域还得靠 clip：它限制一步更新的幅度，防止高优势样本让 $\rho$ 变化过大。SFT
  只给了格式和基本能力，on-policy sampling 仍会偏、组内方差大时照样震荡；要改的是优势本身，比如过程奖励、过滤全同组或用 DAPO 动态
  sampling，clip 留着。
tags:
  - Meituan
  - GRPO
  - Clip
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 美团大模型算法二面-秋招面经
    url: 'https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177'
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“GRPO 为什么要做 clip，直接用 SFT 后的模型还会不稳定吗？优势度可以怎样改进？”**

GRPO 只是换了 advantage 的构造，clipped importance-weighted surrogate 原样留着，所以 clip 照样要。组内 $A$ 很大时，不 clip 一步就能毁掉刚通过 SFT 学会的格式。SFT 只是让解析噪声的先验低一些，证明不了训练稳定。这题三问要连起来答：为什么 clip、SFT 之后为什么还抖、优势怎么改，后两问的答案都不是把 clip 拆掉。

先看 clip 管的是什么。Surrogate 和 PPO 同构：

$$
L(\theta)=\mathbb{E}\big[\min\big(\rho\hat{A},\ \mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\hat{A}\big)\big],
\quad \rho=\frac{\pi_\theta}{\pi_{\mathrm{old}}}.
$$

$\hat{A}\gt 0$ 时它限制 $\rho$ 别太大，免得好样本的概率一步变化过大；$\hat{A}\lt 0$ 时限制 $\rho$ 别太小，免得坏样本概率被压没以后数值不稳。Clip 作用在目标函数上，真实的概率比并没有被强制截进区间。没有价值评估模型（critic）也不等于没有信任域：组均值 baseline 只降低了「相对谁」的方差，并没有限制 $\theta$ 相对行为策略能走多远。多个 epoch 复用同一批 sampling 轨迹（rollout）时 $\rho$ 更容易偏，clip 更省不得。$\varepsilon$ 太大近似没 clip，太小正优势又涨不动，探索就死了。

组内 standardization 还让 clip 更必要。比如一个组里 $\sigma$ 很小，几条回答只有一点点差别，这点差别会被放大成巨大的 $\hat{A}$，再乘上没裁剪的 $\rho$，少数几条轨迹就主导了梯度。这是 GRPO 特有的放大，所以 clip 并不只是 PPO 才需要。

第二问，SFT 之后为什么还会不稳。SFT 给了格式和基本能力，可 on-policy sampling 仍会偏出示范：奖励有噪声、组内全对或全错、KL / 熵塌缩、难度突变、parser 偶尔判零分。高 $\hat{A}$ 乘未裁剪的 $\rho$，少数轨迹主导更新，表现就是 clip fraction 打满、熵骤降、格式合法率往下掉。SFT 和 RL 的模板要是不一致，看着像算法不稳，其实分布一开始就错了。还有 exposure bias：SFT 训练时看的是金标准前缀，RL 看的是自生成前缀，一开始 rollout 质量的方差就大。这些靠去掉 clip 修不好，要靠课程和稳定的验证器（verifier）。

第三问，改进优势。过程分能让「全错组」内部仍然排出先后；长度归一减轻长回复对梯度的主导；过滤 $\sigma\approx 0$ 的组；增大 $G$；再就是 DAPO 的 clip-higher、动态 sampling 和 token 级归约。这些改的是 $A$ 的质量和哪些样本能进 batch，替代不了 clip 对 $\rho$ 的限制。Clip-higher 是把 $\varepsilon$ 改成不对称，clip 还在。验收看 clip fraction、到 old 的 KL、holdout 格式和成功率，训练 $L$ 平不平滑说明不了什么。

这些改法也会失败：过滤之后有效 batch 太小；过程分本身能被 hack；clip-higher 开太大等于没 clip。所以改优势之前，先确认 verifier 对同一条轨迹重打分是一致的。

## 追问

**Advantage standardization 会不会让 clip 更必要？**
会。$\sigma$ 小会把 $A$ 放大，更需要限制 $\rho$。

**GSPO 的序列 clip 还要 token clip 吗？**
两者作用的层不同，要说清 clip 是作用在 $\rho_t$ 上还是 $s(y)$ 上。

**能不能光用 KL、不用 clip？**
不行。KL 相对 $\pi_{\mathrm{ref}}$，clip 相对 $\pi_{\mathrm{old}}$，是两个约束。可以并存，拿一个替代另一个会漏掉一步偏离。

**SFT 很强的话能不能加大 $\varepsilon$？**
可以稍微放宽，但要看 clip fraction 和格式率来定，别按「SFT loss 低」来决定。
