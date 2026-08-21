---
id: stepfun-grpo-loss-handwrite
section: coding
order: 185
level: S
title: 阶跃星辰：手撕 GRPO 时 loss 和组内优势分别怎么写？
quick: >-
  同一 prompt 采 $G$ 条，奖励组内标准化得 $A_i$，再用
  $\min(\rho A,\mathrm{clip}(\rho)A)$（可加 KL）。$\mathrm{std}=0$ 时整组梯度为
  0，要过滤或改采样，不能只加 `eps` 假装有信号。
tags:
  - StepFun
  - GRPO
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：手撕 **“top-p sampling、grpo”**

陷阱是把 GRPO 写成带 critic 的 PPO，或 `std=0` 时只加 `eps`。GRPO **不训 value**，baseline 是组内均值；完整采样见 `code-sampling`，组优势边角见 `code-grpo`、`stepfun-grpo-group-advantage`。同面先写优势张量，再写 `ratio.clamp` 与 `min`。MoE+RL 见 `stepfun-rl-moe-gspo`，不要和 loss 公式混在一起。

## 优势：在 $G$ 维标准化

同一 prompt 采 $G$ 条，$r\in\mathbb{R}^{N\times G}$：

$$
A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

`std` 用 population（`unbiased=False`），与论文/框架对齐。全对/全错则分子为 0，$A=0$，这一 step 无效——记录并动态换题，见 `byte-grpo-all-same-zero-adv`。

## Loss：clipped surrogate，无 critic

$$
\rho=\exp(\log\pi_\theta-\log\pi_{\mathrm{old}}),\qquad
L=\min\bigl(\rho A,\;\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A\bigr).
$$

最大化 $L$（代码里 `-L.mean()`）。可加 KL 到 ref，系数单独拧，见 `xiaohongshu-grpo-drop-kl`。Clip 不把真实 $\rho$ 拉回区间，只让越界且「有利」一侧梯度为 0，见 `code-ppo-clip`。

```python
import torch

def grpo_loss(logp, old_logp, rewards, clip_eps=0.2, adv_eps=1e-6):
    # logp/old_logp/rewards: [N, G]  (token 级则先在 seq 维 reduce 再广播 A)
    mean = rewards.mean(dim=-1, keepdim=True)
    std = rewards.std(dim=-1, keepdim=True, unbiased=False)
    adv = (rewards - mean) / (std + adv_eps)
    rho = (logp - old_logp).exp()
    unclipped = rho * adv
    clipped = rho.clamp(1 - clip_eps, 1 + clip_eps) * adv
    return -torch.minimum(unclipped, clipped).mean()
```

token 级 $\log\pi$ 应对齐 completion token；序列级 $\rho$ 则先对 token 求和再进 clip（GSPO 把比率收到序列级，见 `stepfun-rl-moe-gspo`）。两题一起出时：优势形状 `[N,G]` → `rho` 同形 → `minimum`。不要写 value loss。

## 追问

- **和 PPO 差在哪？** 没有 critic / GAE；组内均值当 baseline。PPO 可以 $n=1$，GRPO 不行，见 `sys-rl-group-n`。
- **KL 放哪？** 加在 surrogate 外作正则，或像部分实现那样从 reward 里扣。要说清你们用哪一种。
- **$\log\pi$ 用 token 平均还是求和？** 必须与采样长度、loss agg 一致，见 `baidu-grpo-loss-agg`。混用会偏长/偏短。
- **std=0 怎么办？** 过滤该组或改采样。eps 防 NaN 不制造信号。
- **top-p 和 GRPO 顺序？** 先能写出 nucleus 采样再写 loss。采样错了，优势再对也是错分布上的更新。
