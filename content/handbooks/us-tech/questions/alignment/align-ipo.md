---
id: align-ipo
section: alignment
order: 14
level: A
title: 对齐：IPO 相对 DPO
quick: >-
  DPO 把 BT 概率拟合到 $\sigma(\beta\Delta)$，偏好接近确定时会把间隔往无穷推。IPO 用平方损失把同一 log 比回归到
  $1/(2\tau)$，过拟合确定性标签更轻。$\tau$ 仍是 KL 温度，不是第二套隐式奖励定义。
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

DeepMind 的 IPO 论文是冲着「从偏好学策略」的目标函数去的，不是又一个刷榜变体。对齐岗在 DPO 之后追 IPO，是看你有没有注意到 logistic 在确定性 pair 上的病态。先把 `align-dpo` 的隐式奖励写对，再谈平方损失改了哪一项。

## DPO 在确定性偏好上会怎样

两边都从「KL 约束的奖励最大」出发，最优策略满足 $r(x,y)=\beta\log(\pi/\pi_{\mathrm{ref}})+\beta\log Z(x)$。DPO 假设人标来自 Bradley-Terry，把差塞进 $\sigma$，得到 $-\log\sigma(\beta\Delta)$，其中

$$
\Delta=\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}.
$$

若数据里几乎总是 $y_w\succ y_l$（标注员很一致，或你用 RM 造的硬间隔），BT 的最大似然希望 $\Delta\to\infty$。训练上就是 rejected 被打穿、chosen 间隔被无限拉大，KL 狂飙。这是目标的性质，不是「忘了加权重衰减」。

Azar 等人指出：你真正想拟合的往往是偏好概率本身，而不是一个无界的 BT 奖励。把映射从 $\sigma$ 换成恒等，再在 log 比上做回归，就得到 IPO。

## IPO：把间隔钉在有限靶上

记 $h_\theta=\Delta$（同一个 implicit log 比）。IPO 损失是

$$
\mathcal{L}_{\mathrm{IPO}}=\mathbb{E}\Big[\Big(h_\theta(x,y_w,y_l)-\frac{1}{2\tau}\Big)^2\Big].
$$

$\tau$ 扮演 DPO 里 $\beta$ 一类的温度：越大，最优策略越贴参考。平方损失的靶是常数，不是 $\infty$。偏好再确定，最优 $h$ 仍停在 $1/(2\tau)$，不会为了再涨 0.001 的 BT 似然把策略推到参考支撑外面。

```python
def ipo_loss(pi_w, pi_l, ref_w, ref_l, tau):
    h = (pi_w - ref_w) - (pi_l - ref_l)  # sequence logp
    target = 0.5 / tau
    return ((h - target) ** 2).mean()
```

和 DPO 一样：只在 response 上求和；$\log Z(x)$ 在差里消掉。换 token 平均还是序列和，等于偷改 $\tau$，见 `align-dpo` 对 $\beta$ 的同一警告。

面试对照：

| | DPO | IPO |
| --- | --- | --- |
| 偏好模型 | BT + logistic | 直接拟合 log 比 |
| 间隔 | 可被推到无穷 | 回归到 $1/(2\tau)$ |
| 确定性 pair | 易过优化 | 更钝 |
| 实现 | `logsigmoid` | 平方 |

IPO 不是「不需要参考模型」。没有 $\pi_{\mathrm{ref}}$，$h$ 的定义就没了。也不是保证不 hack：数据里的长度偏见、谄媚照样进 $h$，见 `align-length-bias`、`align-sycophancy`。

## 什么时候我会提 IPO

离线 pair 很干净、几乎没有平局、DPO 出现 rejected logp 崩溃而 win-rate 不涨：先怀疑 $\beta$ 过小，再试 IPO 或加更强的 KL。pair 本身很噪，平方损失会认真拟合噪声靶，未必比 logistic 更好。KTO 解决的是「没有 pair」，见 `align-kto`，和 IPO 改损失形状不是同一问题。在线要边采边学，GRPO / PPO 仍更自然，见 `align-grpo`。

白板收尾：DPO 把 RM 解析掉了，但仍继承 BT 的无界性；IPO 在同一换元下换了一个有界靶。能说到这一句，比报一个榜上的点差有用。

## 追问

- **$\tau$ 和 $\beta$ 能混用吗？** 量纲同类，数值不能抄。换损失先重扫，并盯 KL 与长度。
- **IPO 还要单独加 token KL 吗？** 目标里已经相对 $\pi_{\mathrm{ref}}$。再减一项要声明你改了目标。
- **为什么不直接 clip $\Delta$？** 硬 clip 是优化 hack；IPO 把有限间隔写进目标。
- **和 ORPO 一句话？** ORPO 把 SFT 和偏好并进 odds ratio，参考模型可选。IPO 仍显式要 ref，改的是偏好项形状。
