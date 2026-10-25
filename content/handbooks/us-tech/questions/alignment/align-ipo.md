---
id: align-ipo
section: alignment
order: 14
level: A
title: 对齐：IPO 相对 DPO
quick: "DPO 在近乎确定的偏好对上可能持续拉大 log 比间隔，IPO 改用平方损失，让同一间隔回归到有限的 $1/(2\\tau)$。它仍使用参考模型，主要改变偏好损失形状；噪声标签和长度偏见仍需另外处理。"
tags:
  - DeepMind
  - IPO
  - DPO
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: A General Theoretical Paradigm to Understand Learning from Human Preferences
    url: https://arxiv.org/abs/2310.12036
    type: primary
  - title: Direct Preference Optimization — Your Language Model is Secretly a Reward Model
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Training language models to follow instructions with human Feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

IPO 主要改变 DPO 的偏好损失形状：把可能越拉越大的间隔，改为回归到一个有限目标。比如某一偏好对永远是 chosen 赢，DPO 的 logistic 仍希望提高置信度；IPO 达到目标间隔后，就没有继续推大的理由。

两者从 KL 约束奖励最大化出发，最优策略满足 $r(x,y)=\beta\log(\pi/\pi_{\mathrm{ref}})+\beta\log Z(x)$。DPO 使用 Bradley-Terry，损失为 $-\log\sigma(\beta\Delta)$，其中：

$$
\Delta=\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}.
$$

若几乎总有 $y_w\succ y_l$，例如标注极一致或用 RM 生成硬标签，BT 最大似然会把 $\Delta\to\infty$。训练中 rejected 概率被压低、KL 上升，这是目标性质，权重衰减本身不能解释或修复。Azar 等人的 IPO 工作讨论直接拟合偏好，把映射从 $\sigma$ 改为恒等，再在 log 比上回归。DPO 推导见 `align-dpo`。

令 $h_\theta=\Delta$，IPO 的目标为：

$$
\mathcal{L}_{\mathrm{IPO}}=\mathbb{E}\Big[\Big(h_\theta(x,y_w,y_l)-\frac{1}{2\tau}\Big)^2\Big].
$$

$\tau$ 与 DPO 中 $\beta$ 扮演同类 KL 温度角色，越大越贴近参考。目标为有限的 $1/(2\tau)$，不再指向 $\infty$，最优间隔停在 $1/(2\tau)$，偏好再确定，也不必为了再提高 0.001 的 BT 似然继续扩大间隔。

```python
def ipo_loss(pi_w, pi_l, ref_w, ref_l, tau):
    h = (pi_w - ref_w) - (pi_l - ref_l)  # sequence logp
    target = 0.5 / tau
    return ((h - target) ** 2).mean()
```

实现仍只在 response 上求和，$\log Z(x)$ 在差里消掉。序列和改成 token 平均会重新标定 $\tau$，与 DPO 的 $\beta$ 一样，不能直接照抄数值。

| | DPO | IPO |
| --- | --- | --- |
| 偏好模型 | BT + logistic | 直接拟合 log 比 |
| 间隔 | 可被推到无穷 | 回归到 $1/(2\tau)$ |
| 确定性 pair | 易过优化 | 更钝 |
| 实现 | `logsigmoid` | 平方 |

## 如何选择

离线 pair 干净、平局少，DPO 出现 rejected logp 崩溃而胜率不涨时，先查 $\beta$ 是否过小，再试 IPO 或更强 KL。Pair 很噪时，平方损失也会拟合噪声，不保证更好。长度偏见和谄媚仍会进入 $h$，见 `align-length-bias`、`align-sycophancy`。

IPO 显式依赖 $\pi_{\mathrm{ref}}$，没有参考就没有这里的 $h$。KTO 解决没有 pair 的数据形式问题，见 `align-kto`；ORPO 把 SFT 与偏好放进 odds ratio，参考模型可选。在线边采边学则更适合 GRPO / PPO，见 `align-grpo`。

## 追问

**$\tau$ 能照抄 $\beta$ 吗？**
量纲同类，数值要重扫，结合 KL 与长度判断。

**还要额外加 token KL 吗？**
目标已相对参考，再加一项就改变目标，要明确说明。

**直接 clip $\Delta$ 行吗？**
那是优化中的硬截断，IPO 是把有限间隔写进损失本身。

## 相关题

- [[align-dpo]]：隐式奖励与温度推导。
- [[coding-dpo-weighted]]：DPO 梯度及 IPO 梯度系数。
- [[msft-orpo]]：是否需要参考模型的对照。
- [[align-kto]]：数据形式与损失形状的区别。
