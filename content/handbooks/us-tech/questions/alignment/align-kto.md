---
id: align-kto
section: alignment
order: 18
level: A
title: 对齐：KTO 只用 binary 反馈
quick: >-
  KTO 不需要 $(y_w,y_l)$ pair，只要「这条好 / 这条坏」。隐式奖励仍是 $\log(\pi/\pi_{\mathrm{ref}})$，损失按前景理论把好样本推到
  KL 基线之上、坏样本推到之下。适合线上点赞点踩；两类都要有，且 $z_0$ 估计漂了会整锅偏。
tags:
  - KTO
  - DPO
  - Preference
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: KTO — Model Alignment as Prospect Theoretic Optimization
    url: https://arxiv.org/abs/2402.01306
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: A General Theoretical Paradigm to Understand Learning from Human Preferences
    url: https://arxiv.org/abs/2310.12036
    type: primary
---

生产日志经常是一条回复上的赞/踩，不是同一 prompt 下两条候选的对比。KTO（Ethayarajh 等人）把前景理论搬到达成：人对损失比收益敏感，且反馈可以 unpaired。对齐岗追这题，是看你会不会在没有 pair 时硬套 DPO。对比 `align-dpo`、`align-ipo`。

## 没有 pair 时目标还剩什么

DPO / IPO 的 $\Delta$ 需要同一 $x$ 上的 $y_w$ 和 $y_l$，$Z(x)$ 才能消掉。线上往往只有 $(x,y,\text{good/bad})$。KTO 仍用隐式奖励

$$
r_\theta(x,y)=\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)},
$$

再和一个 **参考 KL 基线** $z_0$ 比。$z_0$ 是 batch 上 $r_\theta$ 的估计（实现里常用停梯度的均值），扮演「当前策略相对参考有多偏」的锚。好样本希望 $r_\theta>z_0$，坏样本希望 $r_\theta<z_0$。再用 $\sigma$ 包一层，并给好/坏不同权重 $\lambda_D,\lambda_U$（损失厌恶：踩往往权更大）。

直观：你没有「谁赢谁输」的间隔，只有「这点该在锚的哪一侧」。锚漂了，所有点一起错边。这是面试要盯的实现细节，不是背 prospect theory 名词。

```python
def kto_terms(r, z0, lam_d, lam_u, desirable):
    # r: logpi - logref, z0 detached KL baseline
    pos = lam_d * torch.sigmoid(r - z0)
    neg = lam_u * torch.sigmoid(z0 - r)
    return torch.where(desirable, pos, neg).mean()
```

只在 response token 上算 $r$。Prompt 进 $r$ 会把「读懂题」当好坏信号。$z_0$ 必须 `detach`，否则模型会靠改锚而不是改策略来刷损失。

## 数据：两类都要，且不是假 pair

只有赞、没有踩，模型会把已有文风再推高，坏模式压不掉。只有踩，容易过度拒绝和短回复。生产上踩还偏安全与失败工具调用，赞偏闲聊，切片不平衡等于偷偷改目标。

不要把 KTO 数据「合成」成 DPO pair 再训：随机给一条踩配一条赞，破坏了同一 $x$ 的对比假设，BT 间隔没有意义。反过来，有真 pair 时 DPO / IPO 通常更直接，KTO 不是免费升级。

Binary 标签噪声很大：误点、讽刺、长度。KTO 会认真把噪声点推到锚的某一侧。一致率低的来源降权或丢掉。长度偏见照样在：更长更容易被赞，见 `align-length-bias`。

和 RLAIF 的关系：可以用模型打 binary 标签，但仍要隔离 critic，见 `align-rlaif`。Self-rewarding 用当前策略给自己贴赞，锚和策略一起漂，最险。

## 什么时候选 KTO

有大规模 unpaired 反馈、凑 pair 要重采样太贵：KTO 合理。有现成 HH 式 pair：先 DPO / IPO。要在线 rollout 且奖励可验证：GRPO / PPO，见 `align-grpo`。KTO 仍是离线（或准离线）更新，策略一离数据分布，$r_\theta$ 和 $z_0$ 的含义都变，需要迭代刷新，见 `align-online-dpo`。

监控：好样本 $r-z_0$、坏样本 $z_0-r$、KL、长度、held-out 任务。损失下降但两边 $r$ 一起掉，是位移而不是对齐。$\lambda_U$ 过大表现为过度拒绝，见 `align-over-refuse`。

白板一句话：DPO 拟合相对间隔；KTO 拟合相对一条 KL 锚的符号。没有锚的 binary 交叉熵（直接把 logp 当分类）会把参考语言模型冲掉。

## 追问

- **为什么还要 $\pi_{\mathrm{ref}}$？** 没有参考，$r$ 绝对尺度漂，赞会变成「提高所有 token 的似然」。
- **$z_0$ 用全局常数行吗？** 早期能跑。策略移动后要用 batch 估计，且 detach，否则学锚不学策略。
- **能和 DPO 混吗？** 可以按数据源分 loss。不要把假 pair 和真 binary 搅成一个 $\Delta$。
- **点踩是不是比 pair 更真？** 更便宜，更噪，更偏使用分布。真不真取决于谁点、何时点，不是二进制本身。
