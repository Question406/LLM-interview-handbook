---
id: align-kto
section: alignment
order: 18
level: A
title: 对齐：KTO 只用 binary 反馈
quick: >-
  KTO 用单条回答的好 / 坏标签训练，不要求同一题的成对偏好。它将 $\log(\pi/\pi_{\mathrm{ref}})$ 与 KL
  基线比较，好样本向上推、坏样本向下推；两类覆盖、标签噪声和基线估计都会影响更新。
tags:
  - KTO
  - DPO
  - Preference
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: KTO — Model Alignment as Prospect Theoretic Optimization
    url: 'https://arxiv.org/abs/2402.01306'
    type: primary
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: >-
      A General Theoretical Paradigm to Understand Learning from Human
      Preferences
    url: 'https://arxiv.org/abs/2310.12036'
    type: primary
---

KTO 适合只有单条回答点赞、点踩的数据，不需要为每条反馈再找同一题的另一条候选。它保留相对 $\pi_{\mathrm{ref}}$ 的隐式奖励 $\log(\pi/\pi_{\mathrm{ref}})$，让好回答高于一条 KL 基线、坏回答低于基线。

DPO / IPO 要同一 $x$ 的 $y_w$、$y_l$ 才能构造 $\Delta$ 并消去 $Z(x)$，线上日志却常只有 $(x,y,\text{good/bad})$。Ethayarajh 等人的 KTO 用前景理论处理这种 unpaired 反馈，隐式奖励为：

$$
r_\theta(x,y)=\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)},
$$

再与参考 KL 基线 $z_0$ 比较。$z_0$ 是 batch 上 $r_\theta$ 的估计，常用停梯度均值，表示策略偏离参考的程度。好样本希望 $r_\theta>z_0$，坏样本希望 $r_\theta<z_0$，经 $\sigma$ 映射后，用 $\lambda_D,\lambda_U$ 分别加权。前景理论的损失厌恶对应坏反馈往往权更大。

因此一条点赞不再需要匹配某个点踩，但整批判断会受基线影响。$z_0$ 必须 `detach`，否则模型可能靠移动基线减小损失。$r$ 只统计回答 token，prompt 不参与好坏信号：

```python
def kto_terms(r, z0, lam_d, lam_u, desirable):
    # r: logpi - logref, z0 detached KL baseline
    pos = lam_d * torch.sigmoid(r - z0)
    neg = lam_u * torch.sigmoid(z0 - r)
    return torch.where(desirable, pos, neg).mean()
```

## 数据和监控怎样准备

两类反馈都要覆盖。只有赞会进一步强化原有文风，难压坏模式；只有踩可能让回答过短、over-refusal。实际生产里，点踩可能偏安全或失败工具调用，点赞偏闲聊，切片失衡就改变了训练目标。

不能随便给一条赞配一条踩做 DPO：不同输入不满足同一 $x$ 的比较假设，BT 间隔没有对应含义。有真实 pair 时，DPO / IPO 通常更直接，见 `align-dpo`、`align-ipo`。点赞点踩也有误点、讽刺和长度噪声，低一致率来源应降权或丢弃，长度偏见见 `align-length-bias`。

模型也可以生成 binary 标签，但要隔离反馈 critic，见 `align-rlaif`。当前策略给自己贴赞的 self-rewarding 会让标签、基线与策略一起漂。KTO 仍是离线或准离线更新，策略离开数据分布后需要迭代刷新，见 `align-online-dpo`；真正在线 rollout 且奖励可验证时，可考虑 GRPO / PPO，见 `align-grpo`。

我会监控好样本 $r-z_0$、坏样本 $z_0-r$、KL、长度和 held-out 任务。损失下降但两边 $r$ 一起下降，可能只是整体位移；$\lambda_U$ 过大则可能 over-refusal，见 `align-over-refuse`。reference model 也必须保留，否则 $r$ 绝对尺度漂移，点赞容易退化成提高所有 token 似然，直接用 logp 做 binary 分类可能破坏原来的生成能力。

## 追问

**$z_0$ 能固定吗？**
早期可以尝试，策略移动后应随 batch 估计并停梯度，否则基线不再匹配当前策略。

**能与 DPO 混用吗？**
能，按来源分别计算 loss，保留真 pair 与真 binary 的语义，别混成假的 $\Delta$。

**点踩比 pair 更真实吗？**
它便宜、贴近使用分布，也更噪。可靠性取决于谁在什么情境下点，而非二进制形式本身。

## 相关题

- [[align-dpo]]：隐式奖励来源。
- [[align-ipo]]：仍用 pair、改变损失形状。
- [[msft-orpo]]：省 reference model 与省成对标注的区别。
- [[align-online-dpo]]：持续收集并使用 online feedback。
