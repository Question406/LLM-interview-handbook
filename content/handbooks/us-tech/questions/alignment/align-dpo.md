---
id: align-dpo
section: alignment
order: 2
level: S
title: 对齐：DPO 的 implicit reward，β 太大太小
quick: >-
  DPO 把「RM + 反向 KL」解析成 $r(x,y)=\beta\log(\pi_\theta/\pi_{\mathrm{ref}})+\beta\log Z(x)$。$Z(x)$
  在 Bradley-Terry 里消掉。$\beta$ 太大贴参考、学不动偏好；太小偏离爆炸，rejected 概率被打穿，chosen 也不一定升。
tags:
  - OpenAI
  - DPO
  - RLHF
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Direct Preference Optimization — Your Language Model is Secretly a Reward Model
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

OpenAI / DeepMind 对齐和 post-training 岗会把 DPO 当「你能不能从 RLHF 目标推到分类 loss」。别背 $-\log\sigma(\beta\Delta)$ 交差。要能写出隐式奖励、说清 $Z(x)$ 为什么消失、以及 $\beta$ 在理论和训练动态里不是同一件事。KL 方向见 `align-rlhf-kl`。公司章若写了 DPO 实现细节，和本题对照着讲，不要两套符号。

## 隐式奖励从哪来

KL 约束的 RLHF 最优策略满足

$$
\pi^*(y\mid x)=\frac{1}{Z(x)}\pi_{\mathrm{ref}}(y\mid x)\exp\big(r(x,y)/\beta\big),
$$

$Z(x)=\sum_{y'}\pi_{\mathrm{ref}}(y'\mid x)\exp(r(x,y')/\beta)$。反解奖励：

$$
r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}+\beta\log Z(x).
$$

这就是 implicit reward：策略相对参考的 log 比，加上只依赖 $x$ 的配分函数。Bradley-Terry 只看差值 $r(x,y_w)-r(x,y_l)$，$Z(x)$ 消掉，得到

$$
\mathcal{L}_{\mathrm{DPO}}=-\mathbb{E}\Big[\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big)\Big].
$$

现场若只能背 loss、说不清这一步比例关系，评委会认为你没推过。把 KL 写成正向，闭式不再是「参考乘 $\exp(r/\beta)$」，整段换元报废。

隐式奖励只识别到 $x$ 的函数。你不能拿 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 当绝对打分去和另一个 RM 比大小，除非先对齐同一 prompt 的 baseline。用它做 best-of-n 可以，因为同一 $x$ 下 $Z$ 公共。

```python
def dpo_loss(pi_w, pi_l, ref_w, ref_l, beta):
    # logp of sequences, already summed over response tokens
    delta = beta * ((pi_w - ref_w) - (pi_l - ref_l))
    return -torch.nn.functional.logsigmoid(delta).mean()
```

只在 response token 上求和。Prompt 进 loss 会把「读懂题」当偏好信号。

## $\beta$ 太大、太小

理论上 $\beta$ 是 KL 强度：越大，最优 $\pi^*$ 越贴 $\pi_{\mathrm{ref}}$，reward tilt $r/\beta$ 越弱。太小则 $\exp(r/\beta)$ 把质量堆到极少数高奖励句子上，容易 hack。

训练动态里 $\beta$ 还缩放 $\sigma$ 的 logit。$\beta$ 太大：$|\beta\Delta|$ 很容易饱和，梯度变没，看起来像「很稳」，其实偏好没学进去，win-rate 贴 SFT。$\beta$ 太小：implicit reward 尺度爆炸，策略远离参考；常见失败是 rejected 的 likelihood 被打到接近 0，chosen 的 logp 不升甚至掉（likelihood displacement）。监控要同时看 chosen/rejected logp、相对 ref 的 KL、长度、人工或 held-out win-rate，不要只盯 DPO loss。

经验量级常在 $0.1$ 到 $0.5$，但有效 $\beta$ 被长度归一化、pair 的 margin、reference 质量改掉。logp 按 token 平均还是按序列求和，等于偷偷重标定 $\beta$。换实现先对齐这一项，再谈「论文里的 $0.1$」。

$\beta$ 不是学习率。LR 太大是优化器问题；$\beta$ 太大是目标本身不允许离参考远。两者都会「学不动」，归因要看 KL 曲线：KL 几乎为 0 更像 $\beta$ 过大或数据没信息；KL 狂飙、gold 掉，更像 $\beta$ 过小或 pair 噪声。

## 和 PPO 比，面试怎么收

DPO 不 rollout、不训单独 RM，离线偏好就能训。代价是数据覆盖当前策略：off-policy 偏好过旧，隐式 RM 会过拟合那批 pair。PPO 在线、贵，但能边采边更新。资源紧、有现成 HH 式 pair，DPO 合理；要持续打新能力、奖励会漂，PPO / GRPO 更合适。DPO 没有淘汰 RLHF。

## 追问

- **$Z(x)$ 为什么不用算？** 同一 prompt 的 chosen/rejected 共享 $Z$，BT 差值里抵消。要绝对分数才需要。
- **$\beta$ 和观察到的 KL 单调吗？** 稳态方向清楚，有限步、LR、pair 难度下不保证。用 win-rate + KL + 长度一起调。
- **chosen logp 下降正常吗？** 短训常见，因为 loss 只保证相对间隔。长期 chosen 和 rejected 一起掉，要查 $\beta$、长度归一和 pair 噪声。
- **还要单独加 token KL 吗？** 目标里已经有 ref；再减一项要声明你改了目标，不能当默认 DPO。
