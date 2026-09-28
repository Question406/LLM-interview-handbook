---
id: anthropic-grpo-debug
section: anthropic
order: 25
level: S
title: Anthropic：RL Fundamentals，修一段有 bug 的 GRPO
quick: >-
  招聘官把这轮叫做 RL Fundamentals。给你一段大约一两百行的 GRPO，自己跑。
  报告点名的两处是：multinomial 吃了原始 logits；一组奖励完全一样时优势变成 NaN。
  第三处脚本没公开。修完会问重要性采样比为什么不是 1。
tags:
  - Anthropic
  - GRPO
  - PPO
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: RL Fundamentals — GRPO Debug，1Point3Acres，last asked 2026-03-02
    url: https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug
    type: candidate-first-hand
  - title: Debug GRPO / RL Training Code, AceOffer
    url: https://aceoffer.app/interviews/debug_grpo_rl_training_code_technical_deep_dive
    type: secondary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 真题记录

一亩三分地把这题标成 Anthropic 的 RL Fundamentals，电话面、技术面、onsite coding 都出现过，频率低，最近一次 2026-03-02。正文要登录。AceOffer 说他们看到两份候选人报告，2025 年 10 月和 2026 年 3 月，招聘官和候选人自己都用 RL Fundamentals 这个名字。脚本大约 100 到 200 行，PyTorch，包含采样、组内优势、PPO 式的 ratio 和 clip。脚本原文没有公开。AceOffer 写明：两份报告点名了下面前两处；第三处报告只说「还有一个 bug」，具体哪一行是他们按追问反推的，不是原话。

同一轮后面还有别的 coding，AceOffer 提到加权 batch、分布式里找中位数。那些不是这道 GRPO。

## 跑起来就能看见的两处

`torch.multinomial` 要的是非负权重，不是 logits。logits 里有负数，直接传入会 `RuntimeError`。一行碰巧全是非负，它不崩，但按原始 logits 的比例抽样，不是 softmax 之后的策略。全相等的正 logits 两种抽法都是均匀分布，单测会放过。

```python
action = torch.multinomial(torch.softmax(logits, dim=-1), num_samples=1)
# 或 Categorical(logits=logits).sample()，它内部做 log_softmax
```

一组回报完全一样时，标准差是 0，`(r - mean) / std` 是 NaN。PyTorch 默认 `std` 是无偏的，组大小为 1 时分母 `n-1` 也是 NaN，加 eps 救不了。组大小至少为 2，用总体标准差。分子在全相同的时候本来就是 0，除以 `std + eps` 得到 0，这一组不该有更新。eps 只是避免 0 除 0，不是把「全对」变成一个学习信号。

```python
def group_advantage(rewards, group_size):
    r = rewards.view(-1, group_size)
    mean = r.mean(dim=1, keepdim=True)
    std = r.std(dim=1, keepdim=True, correction=0)
    centered = r - mean
    adv = torch.where(std < 1e-8, torch.zeros_like(r), centered / std)
    return adv.reshape(-1)
```

## 第三处和修完之后的追问

报告没有贴出第三行。修完前两处之后，面试官会问重要性采样比。正确写法是

$$
\rho = \exp(\log\pi_\theta - \log\pi_{\mathrm{old}})
$$

把 $\log\pi_\theta - \log\pi_{\mathrm{old}}$ 直接当成 $\rho$，clip 的区间 $[1-\varepsilon, 1+\varepsilon]$ 对一个在 0 附近的数没有意义。AceOffer 认为这就是被藏住的第三处，并说面试官会问：如果 ratio 写成对数差，模型还能不能训。这是追问，不是一份贴出来的 diff。

名义上 on-policy，第一步更新前 $\pi_\theta$ 和采样策略是同一个，$\rho$ 应该是 1。同一批 rollout 上再做第二个 mini-epoch，$\pi_\theta$ 已经动了，$\rho$ 离开 1。这不是 bug。另外两条也会让第一步就不是 1：采样引擎和训练前向不是同一套 kernel；采样时用了 temperature 或 top-p，重算 logprob 时用了裸 logits。打印 `ratio.mean()` 之前先确认 old logprob 是采样当时存下来的，并且 `detach` 了。

优势是一条回答一个数，要广播到 response token，再乘 mask。prompt、pad、工具返回的原文不进损失。优势本身 `detach`，否则梯度会穿进奖励。

```python
def clipped_loss(new_logp, old_logp, adv, mask, eps=0.2):
    adv = adv.detach()[:, None]
    rho = torch.exp(new_logp - old_logp)
    unclipped = rho * adv
    clipped = torch.clamp(rho, 1.0 - eps, 1.0 + eps) * adv
    per_tok = -torch.minimum(unclipped, clipped)
    return (per_tok * mask).sum() / mask.sum().clamp(min=1)
```

Clip 只在「这一步还想往更远推」的那一侧把梯度掐掉。$A>0$ 且 $\rho>1+\varepsilon$，或 $A<0$ 且 $\rho<1-\varepsilon$。它不保证 $\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{old}})$ 有上界。GRPO 论文里另外加了对参考模型的 KL。token 级 KL 的 reduction 见 `coding-kl-div`。偏好模型的 logistic 损失见 `anthropic-pref-bt`，那是另一轮，不是这段脚本。

## 追问

**全对的一组加了 eps 之后优势是不是很小的正数？** 不是。每个回报减去组均值之后是 0，再除以任何正的分母仍是 0。eps 解决的是 NaN。

**为什么不把优势放进 logprob 的图里？** 优势是这批样本上的权重。让它跟着 $\pi_\theta$ 变，等于多了一条没有推导过的梯度。

**第一步 ratio 就是 1，clip 还有什么用？** 第一步没有用。第二个 epoch，或者采样和打分不是同一次前向时，才有 token 的 $\rho$ 离开 1。只做一次更新、并且 logprob 来自同一次前向，clip 是空的。
