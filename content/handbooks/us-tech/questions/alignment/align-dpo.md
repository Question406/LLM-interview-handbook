---
id: align-dpo
section: alignment
order: 2
level: S
title: 对齐：DPO 的 implicit reward，β 太大太小
quick: "DPO 从 KL 约束的奖励目标得到隐式奖励 $\\beta\\log(\\pi_\\theta/\\pi_{\\mathrm{ref}})+\\beta\\log Z(x)$，同一输入的偏好差里 $Z$ 会抵消。$\\beta$ 过大可能学不进偏好，过小可能偏离参考并压低 rejected 概率，应结合 KL、两侧 logp、长度和独立胜率调整。"
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

DPO 把策略相对参考模型的 log 概率比当作隐式奖励，因此可以直接用离线偏好对训练，不必另外训练 RM 或在线 rollout。偏好损失可写作 $-\log\sigma(\beta\Delta)$。理解它时，我会先推清为什么同一题的归一化项会抵消，再解释 $\beta$ 怎样影响策略。

KL 约束的 RLHF 最优策略满足：

$$
\pi^*(y\mid x)=\frac{1}{Z(x)}\pi_{\mathrm{ref}}(y\mid x)\exp\big(r(x,y)/\beta\big),
$$

其中 $Z(x)=\sum_{y'}\pi_{\mathrm{ref}}(y'\mid x)\exp(r(x,y')/\beta)$。反解得到：

$$
r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}+\beta\log Z(x).
$$

隐式奖励由策略与参考的 log 比，以及只依赖输入 $x$ 的配分函数组成。比如同一道题两条回答分别为 chosen 与 rejected，Bradley-Terry 只比较 $r(x,y_w)-r(x,y_l)$，共同的 $Z(x)$ 就消掉了，得到：

$$
\mathcal{L}_{\mathrm{DPO}}=-\mathbb{E}\Big[\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big)\Big].
$$

这套换元依赖正确的 KL 方向，若写成正向 KL，闭式就不再是参考乘 $\exp(r/\beta)$，见 `align-rlhf-kl`。隐式奖励只确定到一个输入函数，不能把 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 跨 prompt 当绝对分，也不能未经 baseline 对齐就与另一 RM 比大小。同一 $x$ 的 best-of-n 可以用，因为它们共享 $Z$。

下面输入已经在 response token 上求和的 logp，prompt 不进偏好损失：

```python
def dpo_loss(pi_w, pi_l, ref_w, ref_l, beta):
    # logp of sequences, already summed over response tokens
    delta = beta * ((pi_w - ref_w) - (pi_l - ref_l))
    return -torch.nn.functional.logsigmoid(delta).mean()
```

## 怎样理解和调整 $\beta$

理论上 $\beta$ 控制 KL 强度：越大，最优 $\pi^*$ 越靠近 $\pi_{\mathrm{ref}}$，$r/\beta$ 的倾斜越弱；太小则把概率集中到少数高奖励句子，容易刷奖励。

有限步训练还要看梯度。$\beta$ 同时缩放 $\sigma$ 的 logit，太大时 $|\beta\Delta|$ 容易饱和，偏好没学进去，win-rate 仍接近 SFT。太小时可能出现 likelihood displacement：rejected likelihood 接近 0，chosen logp 却不升甚至下降。损失只要求相对间隔，因此两侧都要监控，再配合相对参考的 KL、长度和人工或 held-out win-rate。

经验量级常在 $0.1$ 到 $0.5$，但 pair margin、reference 质量和长度归一化都会改变有效尺度。按 token 平均或按序列求和，相当于重新标定 $\beta$，换实现先对齐这一点，不能照抄论文的 $0.1$。$\beta$ 与学习率也不同：LR 控制优化器步长，$\beta$ 改目标。KL 几乎为 0 可怀疑 $\beta$ 过大或数据无信息；KL 狂飙且 gold 下降，则查 $\beta$ 过小或 pair 噪声。观察到的 KL 在有限步、不同 LR 和 pair 难度下不保证严格单调。

有现成 HH 式 pair、资源有限时，DPO 很直接；数据过旧，隐式 RM 也会过拟合旧 pair。要持续探索新能力或奖励变化较大时，PPO / GRPO 在线采样更自然，但成本更高。DPO 是 RLHF 的一条实现路线。这是 OpenAI / DeepMind 对齐岗常用的公开推导主题，公司章实现要沿用同一套符号。

## 追问

**$Z(x)$ 为什么不用算？**
同一题两条回答共享 $Z$，BT 奖励差抵消它；要绝对分数才涉及这一项。

**chosen logp 下降正常吗？**
短训练可能发生，目标只保证相对间隔。长期两侧一起下降，要查 $\beta$、长度归一化和 pair 噪声。

**还要额外加 token KL 吗？**
标准目标已包含 ref。再加一项就改变了目标，需要明确说明。

## 相关题

- [[openai-dpo-loss]]：相对 PPO 去掉哪些组件。
- [[coding-dpo-weighted]]：写梯度，看 $\beta$ 与 $\sigma(-z)$ 如何加权样本。
- [[align-ipo]]：把同一 log 比回归到有限目标。
- [[align-online-dpo]]：处理旧 pair 与新策略脱节。
- [[msft-orpo]]：去掉参考模型后的对照。
- [[align-kto]]：只有单条好 / 坏反馈时的做法。
