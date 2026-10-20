---
id: coding-loss-atlas
section: coding
order: 44
level: S
title: 白板总览：LLM 训练里常见的 loss，都写成「权重 × logprob」来对照
quick: "落在采样 token 上的 loss，梯度都能写成 $-\\sum_t w_t\\nabla\\log\\pi(y_t)$，各算法只差权重 $w_t$；z-loss、全词表 KL、熵、RM 等要看 logits 或别的头。"
tags:
  - 完整编程练习
  - Coding
  - SFT
  - DPO
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: "SimPO: Simple Preference Optimization with a Reference-Free Reward"
    url: https://arxiv.org/abs/2405.14734
    type: primary
  - title: "KTO: Model Alignment as Prospect Theoretic Optimization"
    url: https://arxiv.org/abs/2402.01306
    type: primary
  - title: "ORPO: Monolithic Preference Optimization without Reference Model"
    url: https://arxiv.org/abs/2403.07691
    type: primary
  - title: A General Theoretical Paradigm to Understand Learning from Human Preferences (IPO)
    url: https://arxiv.org/abs/2310.12036
    type: primary
  - title: Approximating KL Divergence (John Schulman)
    url: http://joschu.net/blog/kl-approx.html
    type: secondary
  - title: "Switch Transformers: Scaling to Trillion Parameter Models"
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `surrogate(logp, w, mask, denom)`：在 mask `[B, T]` 的有效 token 上返回 $-\sum \mathrm{sg}(w)\log\pi / D$，对 `logp` 的梯度和原 loss 一致。`denom` 必须大于 0，否则抛 `ValueError`。
- `w_k3(logp, ref_logp, beta) -> [B, T]`：k3 KL 放进 loss 时，每个采样 token 的权重。
- `w_pairwise(lw, ll, beta, ref_margin, len_w, len_l, gamma) -> (chosen 权重, rejected 权重)`：DPO 和 SimPO 共用。`lw`、`ll` 是 `[B]` 的序列 logprob，pairwise 的序列长度必须大于 0。
- 约束：reference 的 logprob、mask、奖励和采样路径都视为固定；权重必须 detach。不要求替身 loss 的数值等于原 loss。

### 输入输出示例

```text
DPO，margin z = 0, beta = 0.2  -> chosen 权重 +0.1 (= beta/2)，rejected 权重 -0.1
k3 KL，logp == ref_logp         -> 权重 0，梯度 0
SimPO，len_w = 2, len_l = 3     -> 权重分别再除以 2 和 3
```

### 解题思路与正确性

对原 loss 用链式法则求出它对每个 token 的 $\log\pi$ 的偏导，取负号就是这个 token 的权重 $w$；把 $w$ detach 成常数，再乘回 $\log\pi$，替身的梯度就和原 loss 一样。

比如 DPO 的 $L=-\log\sigma(z)$，$\partial L/\partial z=-\sigma(-z)$，而 $z$ 对 chosen 序列 logprob 的导数是 $\beta$，所以 chosen 的权重是 $\beta\sigma(-z)$，rejected 是它的相反数。SimPO 的 $z$ 用长度平均的 logprob，权重再除以各自的长度。

这种等价只针对当前这批固定样本的 logprob 梯度：不包括重新采样带来的变化，也不覆盖需要看整个 logits 的 loss（见下面的表二）。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def surrogate(logp, w, mask, denom):
    """梯度等价的替身 loss：-sum(sg(w) * logp * mask) / denom。

    logp: [B, T]，需要梯度；w: [B, T] 或 [B, 1]；denom 要和原 loss 的归约方式一致，且 > 0。
    替身的数值不等于原 loss，只有对 logp 的梯度相同。
    """
    if denom <= 0:
        raise ValueError(f"denom must be positive, got {denom}")
    return -(w.detach() * logp * mask).sum() / denom


def w_k3(logp, ref_logp, beta):
    """k3 KL 放进 loss 时每个采样 token 的权重 beta * (rho - 1)，rho = pi_ref / pi。[B, T]。"""
    rho = torch.exp(ref_logp - logp).detach()
    return beta * (rho - 1)


def w_pairwise(lw, ll, beta, ref_margin=0.0, len_w=1.0, len_l=1.0, gamma=0.0):
    """DPO / SimPO 每个 token 的权重，返回 (chosen 权重, rejected 权重)，形状 [B]。

    lw, ll: [B]，chosen / rejected 的序列 logprob（token 求和）。
    DPO：len_w = len_l = 1，ref_margin = ref_w - ref_l，gamma = 0。
    SimPO：ref_margin = 0，len_* = 回答长度 |y|，gamma > 0。
    """
    z = beta * (lw / len_w - ll / len_l - ref_margin) - gamma
    coefficient = (beta * torch.sigmoid(-z)).detach()
    return coefficient / len_w, -coefficient / len_l
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def pairwise_case(beta, **kwargs):
    """比较 -logsigmoid(z) 的真实梯度和替身梯度。"""
    chosen = torch.randn(2, 3, requires_grad=True)
    rejected = torch.randn(2, 3, requires_grad=True)
    sum_w = chosen.sum(-1)
    sum_l = rejected.sum(-1)
    z = beta * (sum_w / kwargs.get("len_w", 1) - sum_l / kwargs.get("len_l", 1)
                - kwargs.get("ref_margin", 0)) - kwargs.get("gamma", 0)
    true_grads = torch.autograd.grad(-F.logsigmoid(z).mean(), (chosen, rejected))
    weight_w, weight_l = w_pairwise(sum_w, sum_l, beta, **kwargs)
    full_mask = torch.ones(2, 3)
    sur = surrogate(chosen, weight_w[:, None], full_mask, 2) + surrogate(rejected, weight_l[:, None], full_mask, 2)
    sur_grads = torch.autograd.grad(sur, (chosen, rejected))
    for expected, actual in zip(true_grads, sur_grads):
        assert torch.allclose(expected, actual, atol=1e-6)


torch.set_num_threads(1)
torch.manual_seed(0)
logp = torch.randn(2, 3, requires_grad=True)
ref = torch.randn(2, 3)
mask = torch.ones(2, 3)

# k3 KL：真实 loss 的梯度 == 替身的梯度
rho = (ref - logp).exp()
k3_loss = ((rho - (ref - logp) - 1) * mask).mean() * 0.1
(grad_true,) = torch.autograd.grad(k3_loss, logp)
(grad_sur,) = torch.autograd.grad(surrogate(logp, w_k3(logp, ref, 0.1), mask, mask.sum()), logp)
assert torch.allclose(grad_true, grad_sur, atol=1e-6)

# k3：logp == ref 时权重和梯度都是 0
assert torch.allclose(w_k3(logp, logp.detach(), 0.1), torch.zeros(2, 3))

# DPO（带参考模型的 margin）和 SimPO（长度归一 + gamma）的梯度都对得上
pairwise_case(0.1, ref_margin=torch.tensor([0.1, -0.2]))
pairwise_case(0.1, len_w=torch.tensor([2.0, 3.0]), len_l=torch.tensor([3.0, 2.0]), gamma=0.5)

# DPO margin z = 0：chosen 权重 beta/2，rejected 权重 -beta/2
weight_w, weight_l = w_pairwise(torch.tensor([0.0]), torch.tensor([0.0]), 0.2)
assert torch.allclose(weight_w, torch.tensor([0.1]))
assert torch.allclose(weight_l, torch.tensor([-0.1]))

# mask 外的 token 没有梯度
half_mask = torch.tensor([[1.0, 1.0, 0.0], [1.0, 0.0, 0.0]])
(grad_masked,) = torch.autograd.grad(surrogate(logp, torch.ones(2, 3), half_mask, half_mask.sum()), logp)
assert torch.all(grad_masked[half_mask == 0] == 0)

# 分母必须为正
expect_value_error(surrogate, logp, torch.ones(2, 3), mask, 0)
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$。所有函数的时间和中间空间都是 $O(BT)$；pairwise 权重本身只有 $O(B)$。

- 追问「全词表熵、z-loss、value head 能不能也这么写」：不能。它们的梯度落在整个词表的 logits 或别的输出头上，不是「已采样 token 的常数权重 × logprob」。
- 追问「训练端怎么用」：每步先用一次无梯度前向算出 $w$，再用带权重的 NLL 反传。

## 题怎么来的

面试常把几种损失（loss）放在一起问：「DPO 和 PPO 的梯度有什么共同点」「训练端只支持加权 NLL，哪些算法能跑」「KL 放在 loss 里用 k1 行不行」。每个 loss 单独背公式容易混；统一成同一种写法后，差别就只剩一列权重。`fireworks-grpo-sft-loss` 是这个思路在 GRPO 上的一次展开，这道题把它推到常见的训练 loss 上。

## 统一形式

只看落在具体 token 上的 loss（标注的 token，或者采样出来的 token）。它们的梯度都能写成

$$
\nabla_\theta L = -\frac{1}{D}\sum_{i,t} w_{i,t}\,\nabla_\theta\log\pi_\theta(y_{i,t})
$$

其中 $w$ 在这一步是常数，$D$ 是归约用的分母。所以每个 loss 都有一个梯度等价的替身：

$$
L_{\mathrm{sur}} = -\frac{1}{D}\sum_{i,t}\mathrm{sg}(w_{i,t})\,\log\pi_\theta(y_{i,t})
$$

替身的 loss 数值和原 loss 不一样，只有梯度一样。$w>0$ 把这个 token 的概率往上推，$w<0$ 往下压，$|w|$ 决定力度。

## 每个 loss 的数学表达式

记号：$x$ 是输入提示（prompt），$y$ 是回答，$\pi=\pi_\theta$。$m_{i,t}\in\{0,1\}$ 是 loss mask，标出哪些 token 计入损失，$N=\sum_{i,t}m_{i,t}$ 是有效 token 数。序列 logprob $\log\pi(y\mid x)=\sum_t\log\pi(y_t\mid x,y_{\lt t})$。ratio 写 $r$，奖励写 $R$，$\sigma$ 是 sigmoid。

### 预训练 / 监督微调（SFT）

用交叉熵做 next-token prediction。预训练里 $m$ 只去掉 pad 和文档边界；SFT 里只有 assistant 的 token 为 1：

$$
L_{\mathrm{CE}} = -\frac{1}{N}\sum_{i,t} m_{i,t}\,\log\pi(y_{i,t}\mid x_i, y_{i,\lt t})
$$

### 强化学习（RL）：策略梯度家族

每个 prompt 采样 $G$ 条回答，第 $i$ 条的奖励是 $R_i$。REINFORCE 减去一个 baseline，RLOO 用其余 $G-1$ 条奖励的均值当 baseline：

$$
L_{\mathrm{PG}} = -\frac{1}{D}\sum_{i,t} m_{i,t}\,\mathrm{sg}(A_i)\,\log\pi(y_{i,t})
$$

$$
A_i^{\mathrm{RLOO}} = R_i - \frac{1}{G-1}\sum_{j\ne i}R_j
$$

PPO / GRPO 的 clipped objective，$r_{i,t}=\exp\big(\log\pi(y_{i,t})-\log\pi_{\mathrm{old}}(y_{i,t})\big)$：

$$
L_{\mathrm{PPO}} = -\frac{1}{D}\sum_{i,t} m_{i,t}\,\min\big(r_{i,t}A_{i,t},\ \mathrm{clip}(r_{i,t},1-\varepsilon,1+\varepsilon)\,A_{i,t}\big)
$$

PPO 的 $A$ 来自 GAE（见 `coding-gae`）。GRPO 用组内归一化的 $A_i=(R_i-\mathrm{mean}(R))/\mathrm{std}(R)$，广播到每个 token；原论文还在目标里加了用 k3 估计的 $\beta\,\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$。

CISPO 截断 IS 权重，但不丢弃 token：

$$
L_{\mathrm{CISPO}} = -\frac{1}{N}\sum_{i,t} m_{i,t}\,\mathrm{sg}\big(\mathrm{clip}(r_{i,t},1-\varepsilon_{\mathrm{low}},1+\varepsilon_{\mathrm{high}})\big)\,A_{i,t}\,\log\pi(y_{i,t})
$$

GSPO 用序列级 ratio（token ratio 的几何平均）：

$$
s_i = \exp\Big(\frac{1}{\lvert y_i\rvert}\sum_t\big(\log\pi(y_{i,t})-\log\pi_{\mathrm{old}}(y_{i,t})\big)\Big)
$$

$$
L_{\mathrm{GSPO}} = -\frac{1}{B}\sum_i\min\big(s_iA_i,\ \mathrm{clip}(s_i,1-\varepsilon,1+\varepsilon)\,A_i\big)
$$

### 偏好优化

直接偏好优化（DPO），$(y_w,y_l)$ 是一对 chosen / rejected：

$$
L_{\mathrm{DPO}} = -\log\sigma(z),
\qquad
z = \beta\Big[\log\frac{\pi(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)} - \log\frac{\pi(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big]
$$

SimPO 去掉参考模型，用长度平均的 logprob，加一个目标间隔 $\gamma$：

$$
L_{\mathrm{SimPO}} = -\log\sigma\Big(\frac{\beta}{\lvert y_w\rvert}\log\pi(y_w\mid x) - \frac{\beta}{\lvert y_l\rvert}\log\pi(y_l\mid x) - \gamma\Big)
$$

IPO 把 logistic 换成平方，$h$ 是 DPO 里去掉 $\beta$ 的那个差：

$$
L_{\mathrm{IPO}} = \Big(h - \frac{1}{2\tau}\Big)^2,
\qquad
h = \log\frac{\pi(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)} - \log\frac{\pi(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}
$$

KTO 只需要单条回答的好 / 坏标签。$\hat r_\theta=\log\frac{\pi(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}$，$z_0$ 是 batch 上 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$ 的估计，不回传梯度：

$$
L_{\mathrm{KTO}} = \mathbb{E}\big[\lambda_y - v(x,y)\big]
$$

$$
v(x,y) =
\begin{cases}
\lambda_D\,\sigma\big(\beta(\hat r_\theta - z_0)\big) & y\ \text{是好样本}\\
\lambda_U\,\sigma\big(\beta(z_0 - \hat r_\theta)\big) & y\ \text{是坏样本}
\end{cases}
$$

ORPO 是 SFT 加一个 odds ratio 项，不需要参考模型。$p(y\mid x)=\exp\big(\frac{1}{\lvert y\rvert}\sum_t\log\pi(y_t)\big)$ 是长度平均后的似然：

$$
L_{\mathrm{ORPO}} = L_{\mathrm{SFT}}(y_w) - \lambda\log\sigma\Big(\log\frac{p(y_w\mid x)}{1-p(y_w\mid x)} - \log\frac{p(y_l\mid x)}{1-p(y_l\mid x)}\Big)
$$

### KL 与蒸馏

采样 token 上的三种 KL 估计，$\rho_t=\pi_{\mathrm{ref}}(y_t)/\pi(y_t)$，$y\sim\pi$：

$$
k_1 = -\log\rho_t,\qquad k_2 = \tfrac{1}{2}(\log\rho_t)^2,\qquad k_3 = \rho_t - \log\rho_t - 1
$$

放进 loss 时是 $L_{\mathrm{KL}}=\frac{\beta}{N}\sum_{i,t}m_{i,t}\,k_3$。全词表的精确 KL：

$$
L_{\mathrm{KL}}^{\mathrm{full}} = \frac{1}{N}\sum_{i,t} m_{i,t}\sum_{v}\pi(v)\big(\log\pi(v)-\log\pi_{\mathrm{ref}}(v)\big)
$$

离线蒸馏用全词表的前向 KL。教师模型（teacher）的分布是 $p_T$，学生是 $p_S$，两者在同一个温度 $\tau$ 下取 softmax，Hinton 的写法还要再乘 $\tau^2$：

$$
L_{\mathrm{KD}} = \frac{1}{N}\sum_{i,t} m_{i,t}\sum_v p_T(v)\big(\log p_T(v)-\log p_S(v)\big)
$$

on-policy 蒸馏从学生模型采样，最小化逐 token 的反向 KL 估计：

$$
L_{\mathrm{OPD}} = \mathbb{E}_{y\sim\pi_S}\Big[\frac{1}{N}\sum_t\big(\log\pi_S(y_t)-\log\pi_T(y_t)\big)\Big]
$$

因为采样分布本身依赖 $\pi_S$，不能直接对这个式子反传，要改用策略梯度：把 $-(\log\pi_S-\log\pi_T)$ 当作每个 token 的奖励。

### 辅助 loss 和别的头

z-loss，$z_{t,v}$ 是 logits：

$$
L_z = \frac{\lambda}{N}\sum_{i,t} m_{i,t}\Big(\log\sum_v e^{z_{t,v}}\Big)^2
$$

熵奖励加在 loss 上时带负号：

$$
L_H = -\frac{\alpha}{N}\sum_{i,t} m_{i,t}\,H_t,
\qquad
H_t = -\sum_v\pi(v)\log\pi(v)
$$

Switch 式 MoE 负载均衡，$E$ 个 expert，$T$ 个 token，$p_e(x)$ 是 router 概率：

$$
L_{\mathrm{aux}} = \alpha E\sum_{e=1}^{E} f_e P_e
$$

$$
f_e = \frac{1}{T}\sum_x \mathbf{1}\big[\arg\max_{e'} p_{e'}(x)=e\big],
\qquad
P_e = \frac{1}{T}\sum_x p_e(x)
$$

奖励模型（Bradley-Terry），$r_\phi$ 是标量头：

$$
L_{\mathrm{RM}} = -\log\sigma\big(r_\phi(x,y_w) - r_\phi(x,y_l)\big)
$$

PPO 的 value loss，$\hat R$ 是 GAE 给出的回报目标：

$$
\tilde V = V_{\mathrm{old}}+\mathrm{clip}(V-V_{\mathrm{old}},-\varepsilon,\varepsilon)
$$

$$
L_V = \frac{1}{2N}\sum_{i,t} m_{i,t}\max\big((V-\hat R)^2,\ (\tilde V-\hat R)^2\big)
$$

## 表一：落在 token 上的 loss

$\mathrm{sg}$ 表示 detach。序列 logprob $\log\pi(y)=\sum_t\log\pi(y_t)$。

| loss | 输入 | 每个 token 的 $w$ | 细题 |
|---|---|---|---|
| 预训练 / SFT 的交叉熵损失（CE） | 标注序列 | 计 loss 的 token 为 1，其余为 0 | `coding-cross-entropy` |
| REINFORCE / RLOO | 采样轨迹（rollout）+ 奖励 | $\mathrm{sg}(A)$ | `coding-rloo-advantage` |
| PPO / GRPO | 同上 + $\pi_{\mathrm{old}}$ | $\mathrm{sg}(rA\cdot\mathrm{active})$ | `fireworks-grpo-sft-loss` |
| CISPO | 同上 | $\mathrm{sg}(\mathrm{clip}(r))\,A$ | `coding-cispo` |
| GSPO | 同上 | $\mathrm{sg}(s_iA_i\cdot\mathrm{active}_i)/\lvert y_i\rvert$ | `coding-gspo-seq-ratio` |
| DPO | 偏好对 + ref | chosen $+c$，rejected $-c$，$c=\beta\sigma(-z)$ | `coding-dpo-weighted` |
| SimPO | 偏好对，无 ref | chosen $+c/\lvert y_w\rvert$，rejected $-c/\lvert y_l\rvert$ | 本题 |
| IPO | 偏好对 + ref | chosen $+c$，rejected $-c$，$c=2(\frac{1}{2\tau}-h)$ | `align-ipo` |
| KTO | 单条好 / 坏 + ref | 好：$\lambda_D\beta\sigma'(u)$；坏：$-\lambda_U\beta\sigma'(u')$ | `align-kto` |
| ORPO | 偏好对，无 ref | SFT 项 + 比值项，比值项带 $\frac{1}{1-p}$ | `msft-orpo` |
| KL 惩罚（k3，放 loss） | rollout + ref | $\beta(\pi_{\mathrm{ref}}/\pi - 1)$ | `sys-kl-place` |
| on-policy 蒸馏（逐 token 反向 KL） | rollout + teacher | $-\mathrm{sg}(\log\pi_S-\log\pi_T)$ | `google-distill-llm` |

$z$、$h$、$\hat r_\theta$、$p$、$\rho$ 的定义见上一节。下面解释其中几行权重：

**DPO / SimPO / IPO。** DPO 的 $c$ 永远为正，pair 排得越对越趋于 0。IPO 的 $c$ 在间隔 $h$ 超过 $\frac{1}{2\tau}$ 之后变成负数，把间隔往回拉。SimPO 的 $z$ 用的是长度平均的 logprob，所以每个 token 的权重多除一个长度。

**KTO。** 好样本 $u=\beta(\hat r_\theta-z_0)$，坏样本 $u'=\beta(z_0-\hat r_\theta)$，$\sigma'(u)=\sigma(u)(1-\sigma(u))$。权重在 $u$ 接近 0 时最大，往两侧都会饱和；DPO 只在排对的那一侧饱和。

**ORPO。** $\nabla\log\frac{p}{1-p}=\frac{1}{1-p}\nabla\log p$，$\nabla\log p$ 是每个 token 的 $\nabla\log\pi$ 除以 $\lvert y\rvert$。chosen 已经很可能（$p\to1$）时，比值项的权重被 $\frac{1}{1-p}$ 放大。

**k3 KL。** $k_3$ 对 $\theta$ 求导得 $(1-\rho)\nabla\log\pi$，所以 $w=\beta(\rho-1)$：比参考模型更自信（$\rho<1$）的 token 被往下压。如果把 k1 直接放进 loss，$w=-\beta$ 是常数，而 $\mathbb{E}_{y\sim\pi}[\nabla\log\pi(y)]=0$，所以期望梯度为 0，只剩噪声。k1 要放进奖励、成为 advantage 的一部分才有用。

**on-policy 蒸馏。** 把 $-(\log\pi_S-\log\pi_T)$ 当作每个 token 的 advantage。表里只算当前 token 这一项；把后面 token 的回报也加进来就是完整的策略梯度，方差更大。

## 表二：不在这个形式里的 loss

这些 loss 要看整个词表或 logits 本身，有的根本不是 policy 头：

| loss | 公式 | 梯度落在哪 | 细题 |
|---|---|---|---|
| z-loss | $\lambda(\log Z)^2$ | logits：$2\lambda\log Z\cdot\mathrm{softmax}(z)$ | `coding-z-loss` |
| 全词表蒸馏（前向 KL） | $\mathrm{KL}(p_T\|p_S)$ | logits：$p_S-p_T$ | `google-distill-llm` |
| 全词表 KL 到 ref | $\sum_v\pi(\log\pi-\log\pi_{\mathrm{ref}})$ | logits，整个词表 | `coding-kl-div` |
| 熵奖励 | $-\alpha H(\pi)$ | logits，整个词表 | `openai-entropy-l1` |
| MoE aux | $\alpha E\sum_e f_eP_e$ | 只经过 router 概率 $P_e$，$f_e$ 不可导 | `openai-moe-aux-loss` |
| 奖励模型 BT | $-\log\sigma(r_w-r_l)$ | 标量头 | `anthropic-pref-bt` |
| PPO value | clipped MSE | 价值评估模型（critic）| `coding-gae` |

CE 对 logits 的梯度是 $\mathrm{softmax}(z)-\mathrm{onehot}(y)$，整个词表都有梯度。表一说的「只落在 token 上」，指的是梯度只经过 $\nabla\log\pi(y_t)$ 这一项；这一项本身会通过 softmax 压低其他词。

## 归约和 mask

权重 $w$ 相同、分母 $D$ 不同，训练行为也会不同：

- CE / SFT：有效 token 数，pad 和 prompt 不进分母。packing 时按文档切 mask，见 `coding-packed-lm`。
- DPO / IPO：先在序列内求和，再对偏好对取平均。序列内改成平均就变成了另一个目标（接近 SimPO）。
- PPO 家族：可以按 token 平均、按序列平均或除以常数，三种做法的长度偏置各不相同，见 `coding-grpo-loss-agg`。
- 多个 loss 相加时，每一项自己的分母要想清楚。policy 用 token 平均、KL 用序列平均，$\beta$ 的含义就变了。

## 常见错法

- **权重没 detach。** 梯度会再从 $w$ 走一遍，替身就不等价了。PPO、CISPO、DPO 都是这样。
- **按权重之和归一化。** SFT 的权重非负，这么做没问题；RL 和偏好优化的权重有正有负，除以权重和可能翻转符号，和接近 0 时梯度会爆掉。
- **序列 logprob 用错了归约。** DPO 要求和，SimPO 要取平均。写错了不会报错，只是悄悄换了一个目标。
- **k1 直接进 loss。** 期望梯度为 0，见上面的 k3 那一段。
- **参考模型带了梯度。** ref 的 logprob 要在 `no_grad` 下算，否则显存翻倍，梯度也错。
- **logprob 本身错了。** 没做 shift、temperature 和采样端不一致、pad 没 mask，都会让表一里所有行一起出错，见 `coding-token-logprob`、`sys-eos-mask`。

## 追问

**训练框架只支持加权 NLL，哪些能跑？** 表一全部能跑：每一步先用一次无梯度前向算出 $w$，再做一次带权重的 NLL 反传。表二不行，z-loss、全词表 KL、熵都要改 loss 代码。

**为什么 DPO 能算 offline，PPO 必须重新采样？** 在这个形式里区别看得很清楚：DPO 的 $w$ 只依赖固定的偏好对和当前模型，数据可以复用；PPO 的 $w$ 里有 $r=\pi_\theta/\pi_{\mathrm{old}}$，数据离当前策略越远，$r$ 越偏，clip 越多，所以要不断重新采样。

**SFT 和 RL 的区别在权重上是什么？** SFT 的 $w$ 恒为 1，只把「应该出现的 token」往上推。RL 的 $w$ 可以为负，能主动压低采样出来的坏 token。先做拒绝采样再做 SFT（RFT），相当于只保留 $w>0$ 的那部分。

## 相关题

- [[coding-dpo-weighted]]：只做 DPO 一种，梯度权重的推导、找 bug 片段和可执行测试都更细。
- [[fireworks-grpo-sft-loss]]：Fireworks 真题，只做 clipped GRPO 一种，要求真把它写成 SFT 式加权 NLL，并解释权重为什么不能除以 `weights.sum()`。
- [[coding-grpo-loss-agg]]：专讲 token loss 怎么聚合成一个数，seq-mean、token-mean 和常数归一的长度偏置。
- [[coding-cispo]]：表一里 CISPO 那一行的展开，讲它和 PPO clip 在出界 token 上谁丢梯度。
- [[coding-gspo-seq-ratio]]：表一里 GSPO 那一行的展开，序列级 ratio 怎么化成 token 权重。
