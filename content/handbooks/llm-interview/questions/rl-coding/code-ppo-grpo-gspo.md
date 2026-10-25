---
id: code-ppo-grpo-gspo
section: rl-coding
order: 8
level: S
title: 手写 PPO / GRPO / GSPO：TRL 和 verl 各改哪一段？
quick: "把一次更新拆成优势、ratio、clip、归约四根独立旋钮：PPO 用 GAE 再 whiten，GRPO 用组内 $(r-\\mathrm{mean})/(\\mathrm{std}+\\varepsilon)$，Dr.GRPO 去掉除 std；clip 有对称 PPO、DAPO 的不对称上界、verl 的 dual-clip（$A\\lt 0$ 时用 `clip_ratio_c` 封顶）、CISPO 的 detach 权重、GSPO 的序列几何平均；归约对照 verl 的 `agg_loss` 和 TRL 的 `loss_type`，TRL 默认已经是 `dapo`，论文原版要改成 `grpo`。"
tags:
  - PPO
  - GRPO
  - GSPO
  - TRL
  - verl
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: TRL GRPO Trainer
    url: https://huggingface.co/docs/trl/grpo_trainer
    type: primary
  - title: TRL paper index（GSPO / DAPO / Dr.GRPO 配置）
    url: https://huggingface.co/docs/trl/paper_index
    type: primary
  - title: verl GSPO example
    url: https://github.com/verl-project/verl/blob/main/examples/gspo_trainer/README.md
    type: primary
  - title: verl GRPO
    url: https://verl.readthedocs.io/en/latest/algo/grpo.html
    type: primary
  - title: GSPO
    url: https://arxiv.org/abs/2507.18071
    type: primary
  - title: verl core_algos.py
    url: https://github.com/verl-project/verl/blob/main/verl/trainer/ppo/core_algos.py
    type: primary
---

## 题目描述

实现一组小型PyTorch策略损失函数，用同一组张量比较PPO、GRPO与GSPO的计算约定。本卡的默认可运行小题是 `ppo_clip_losses`；其余函数是可逐项练习的扩展，后面的TRL/verl配置与框架路径用于代码阅读，不要求安装训练框架。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

默认接口 `ppo_clip_losses(logp,old_logp,adv,eps=0.2)`：三个同形浮点张量，logp/`old_logp`是新旧策略在相同采样token上的log概率，adv是已算好的优势；0≤eps<1。扩展使用[B,T]逐token数据和同形0/1 `response_mask`；`completion_logprobs(logits,input_ids)` 输入[B,T,V]与[B,T]，输出移位对齐的[B,T-1]。

### 输出与约束

默认返回 `(losses,rho)`，均同形。rho=exp(clamp(logp-`old_logp`,-20,20))；losses为 -adv*rho 和 -adv*clamp(rho,1-eps,1+eps) 的较大者，不做归约。扩展约定：`asymmetric_clip_losses`将上下epsilon分开；`dual_clip_losses`仅对负优势把loss封顶为-adv*c；`cispo_losses`使用截断后detach的ratio乘-adv*logp；`gspo_losses`前向ratio为有效token log-ratio均值的指数并广播，每token梯度只走自身logp；`sapo_losses`输出-adv*sigmoid(tau*(rho-1))*4/tau。`grpo_outcome_advantage`按`prompt_index`分组，把各回复有效奖励总和减组均值，可除样本标准差+eps，再广播乘mask；单样本组按mean=0,std=1。`masked_whiten`用全批mask有效位置的总体均值/方差标准化，但不额外把输出无效位置清零；`gae_advantages`返回whiten后的优势，无外部bootstrap。`rollout_is_weight`按mode结尾mask把区间外ratio置0，其他模式截断。`agg_loss`可做token均值/和，或每有效序列的token和/均值再平均；norm模式还除给定常数或T。

### 示例

```text
logp=ln([1.5,0.5]), old_logp=[0,0], adv=[1,-1], eps=0.2
ppo_clip_losses -> losses=[-1.2,0.8], rho=[1.5,0.5]
对losses使用全1 mask做token-mean -> -0.2。
```

## 解题思路与参考答案

我会把 PPO、GRPO、GSPO 写成同一次更新里的四段，每一段都能单独换：优势 $A$ 怎么算、重要性比 $\rho$ 取 token 级还是序列级、clip 用哪种写法、损失怎么归约。这样各个变体就落在同一张张量上，TRL 和 verl 各改了哪一段也一眼能看出来。下面按 verl `core_algos.py` 和 TRL `GRPOConfig` 的分支来写。

四段分别是：

1. 优势 $A$：GAE（PPO）或者组相对（GRPO 一族）。
2. 重要性比 $\rho$：token 级，或者序列几何平均（GSPO）。
3. clip：对称、不对称、dual-clip、CISPO、SAPO。clip 作用在目标里的 $\rho$ 上，网络里的 $\rho$ 不会被改写。
4. 归约：token 等权、序列等权、常数长度归一。这一段决定长回复占多少梯度。

举个例子：同样一句「我在跑 GRPO」，在 TRL 里不改配置，归约其实是 DAPO 的 token 等权；在 verl 里配 `loss_mode: gspo`，改的是 ratio 和 clip，优势还是 GRPO 那一套。把四段分开讲，这种差别就说得清楚。

先写所有变体共用的那一步，从 logits 取 completion 的 logprob：

```python
import torch
import torch.nn.functional as F

def completion_logprobs(logits, input_ids):
    # logits[b, t] 预测的是 input_ids[b, t+1]，所以丢掉最后一格 logits、丢掉第一个 input id。
    # 返回 [B, T-1]，和 response_mask 的时间维对齐。prompt 位置在 mask 里是 0。
    logp = F.log_softmax(logits[:, :-1], dim=-1)
    return logp.gather(-1, input_ids[:, 1:].unsqueeze(-1)).squeeze(-1)
```

## 优势

PPO 的 $A$ 来自价值评估模型（critic）。verl 的 `compute_gae_advantage_return` 在 response mask 为 0 的位置跳过 TD，最后对 advantage 做 masked whiten，也就是减全局均值、除全局标准差。outcome 奖励通常只加在最后一个有效 token 上，$\gamma=\lambda=1$ 时没有折扣，句末的分会沿整段传回去。

```python
def masked_whiten(x, mask, eps=1e-8):
    # verl_F.masked_whiten。只在 response token 上估均值和方差，padding 不进统计。
    denom = mask.sum().clamp(min=1)
    mean = (x * mask).sum() / denom
    var = ((x - mean).square() * mask).sum() / denom
    return (x - mean) / var.sqrt().clamp(min=eps)

def gae_advantages(rewards, values, response_mask, gamma=1.0, lam=1.0):
    # rewards, values, response_mask: [B, T]。values 与 rewards 同长，t 之后的 bootstrap 用 next value。
    # mask=0 的位置（prompt / pad）不产生新的 delta，并把上一时刻的 value / GAE 原样带过来。
    next_value = torch.zeros(rewards.size(0), device=rewards.device)
    last_gae = torch.zeros_like(next_value)
    advantages = torch.zeros_like(rewards)
    for t in reversed(range(rewards.size(1))):
        delta = rewards[:, t] + gamma * next_value - values[:, t]
        last_gae_ = delta + gamma * lam * last_gae
        # mask=0：value 和 GAE 都沿用更靠后的那一格，不把 pad 上的 V 写进递推。
        next_value = values[:, t] * response_mask[:, t] + (1 - response_mask[:, t]) * next_value
        last_gae = last_gae_ * response_mask[:, t] + (1 - response_mask[:, t]) * last_gae
        advantages[:, t] = last_gae
    return masked_whiten(advantages, response_mask)
```

GRPO 不训 $V$。verl `compute_grpo_outcome_advantage` 先把 token 奖励沿时间求和，每条回复得到一个标量，再按输入提示（prompt）id 分组。`norm_adv_by_std_in_grpo=True` 时除以组内标准差（原论文做法）；`False` 时只减均值，这就是 Dr.GRPO。标量再乘 `response_mask` 广播回每个 response token，同一条回复的 token 共享同一个 $A$。`torch.std` 默认 `unbiased=True`（除 $G-1$）。

```python
def grpo_outcome_advantage(token_rewards, response_mask, prompt_index, eps=1e-6, norm_by_std=True):
    # token_rewards, response_mask: [B, T]
    # prompt_index: 长度 B 的 prompt id。同一道题的 G 条必须同一个 id，不能按 batch 下标猜。
    scores = (token_rewards * response_mask).sum(dim=-1)  # [B]，outcome 标量
    adv = torch.empty_like(scores)
    for pid in set(prompt_index.tolist()):
        members = [i for i, p in enumerate(prompt_index.tolist()) if p == pid]
        group = scores[members]
        if group.numel() == 1:
            # verl 的单样本分支：不当成「减掉自己所以是 0」。
            mean, std = group.new_zeros(()), group.new_ones(())
        else:
            mean = group.mean()
            std = group.std(unbiased=True)  # 与 compute_grpo_outcome_advantage 里的 torch.std 一致
        if norm_by_std:
            adv[members] = (group - mean) / (std + eps)
        else:
            adv[members] = group - mean  # Dr.GRPO：algorithm.norm_adv_by_std_in_grpo=False
    # 广播。padding 乘 0。返回的第二项在 verl 里也是这份张量，他们管它叫 returns。
    return adv[:, None] * response_mask
```

TRL 的 `scale_rewards` 只管这一步的除标准差，不动归约：`"group"`（默认）用组内 std；`"batch"` 整批一个 std（Lite PPO）；`False` / `"none"` 不除 std。多奖励时，`multi_objective_aggregation="sum_then_normalize"` 先加权求和再标准化；`"normalize_then_sum"` 是 GDPO，每个奖励维先在组内标准化再相加，免得大尺度奖励把其余项淹掉。verl 里对应的是 `compute_gdpo_outcome_advantage`。

## Clip

下面的 `pg_loss` 都是要最小化的量，所以比论文里的 $\min(\rho A,\mathrm{clip}(\rho)A)$ 多一个负号。`maximum(-ρA, -clip(ρ)A)` 和 $-\mathrm{minimum}(ρA, \mathrm{clip}(ρ)A)$ 是同一个量。

先写对称 PPO（verl 的 `clip_ratio`，TRL 的 `epsilon`，两边默认都是 0.2）：

```python
def ppo_clip_losses(logp, old_logp, adv, eps=0.2):
    # 先把 log ρ 夹到 [-20, 20] 再 exp，避免 ρ 变成 inf。这是数值夹，不是信任域。
    log_ratio = (logp - old_logp).clamp(-20.0, 20.0)
    rho = log_ratio.exp()
    unclipped = -adv * rho
    clipped = -adv * rho.clamp(1.0 - eps, 1.0 + eps)
    # A>0 且 ρ>1+ε，或 A<0 且 ρ<1-ε：clipped 更大，maximum 选它，该项对 θ 的梯度为 0。
    # 反方向（好 token 被压低、坏 token 被抬高）不 clip，梯度还在。
    return torch.maximum(unclipped, clipped), rho
```

DAPO 的 clip-higher 是把上下界拆开：下界仍是 `epsilon`（0.2），上界换成更大的 `epsilon_high`（论文 0.28）。正优势能走得更远，负优势仍被较紧的下界挡住。TRL 不设 `epsilon_high` 时上下界相同；verl 的字段是 `clip_ratio_low` / `clip_ratio_high`，缺省都回落到 `clip_ratio`。

```python
def asymmetric_clip_losses(logp, old_logp, adv, eps_low=0.2, eps_high=0.28):
    log_ratio = (logp - old_logp).clamp(-20.0, 20.0)
    rho = log_ratio.exp()
    unclipped = -adv * rho
    clipped = -adv * rho.clamp(1.0 - eps_low, 1.0 + eps_high)
    return torch.maximum(unclipped, clipped), rho
```

verl 在对称或不对称 clip 之后还有一道 dual-clip（`clip_ratio_c`，默认 3.0，必须大于 1；GSPO 例子里设成 10），只在 $A\lt 0$ 时生效。负优势而 $\rho$ 很大时，$-A\rho$ 会变成一个巨大的正损失，这一步的梯度就被极端样本主导了。dual-clip 把这份损失封在 $-A\cdot c$，$A\ge 0$ 的样本照常走 PPO clip。

```python
def dual_clip_losses(logp, old_logp, adv, eps_low=0.2, eps_high=0.2, clip_ratio_c=3.0):
    # clip_ratio_c > 1。它不是 1±ε 那个窗口，是负优势样本上 ratio 的另一道上限。
    assert clip_ratio_c > 1.0
    ppo, rho = asymmetric_clip_losses(logp, old_logp, adv, eps_low, eps_high)
    capped = -adv * clip_ratio_c
    # A<0：在普通 PPO 损失和 -A*c 里取更小的那个，防止坏动作的 ρ 爆炸。
    # A>=0：capped 更小会误伤正优势，所以丢掉。
    return torch.where(adv < 0, torch.minimum(ppo, capped), ppo), rho
```

CISPO 换掉的是 clip 的对象，优势没动。TRL `loss_type="cispo"` 时，clip 的是 IS 权重本身，然后 detach，再乘上 $A$ 和 $\log\pi_\theta$，所以越界的 token 仍有 $\nabla\log\pi$。ScaleRL 把上界放在 `epsilon_high`，推荐 5.0，别当成 $1+0.2$。指标 `cispo_clip_ratio` 统计的是正优势且 $\rho>\varepsilon_{\mathrm{high}}$ 的比例。论文里的双侧形式见 `pt-cispo`。

```python
def cispo_losses(logp, old_logp, adv, eps_max=5.0):
    rho = (logp - old_logp).exp()
    # detach：上界是常数系数。反传只走 logp，不走被截断的 ρ。
    weight = rho.clamp(max=eps_max).detach()
    return -(weight * adv * logp), rho
```

GSPO 把 clip 的对象换成序列几何平均，优势仍是组相对的。verl `compute_policy_loss_gspo` 的前向值，等于把 $s_i=\exp(\mathrm{mean}_t\log\rho_t)$ 广播到每个 token，但序列均值被 detach，梯度只从当前 token 的 $\log\pi$ 走：

$$
\log s_{i,t}=\mathrm{sg}[\log s_i]+\log\pi_\theta(y_t)-\mathrm{sg}[\log\pi_\theta(y_t)].
$$

数值上 $s_{i,t}=s_i$。如果直接对 $\exp(\mathrm{mean}\log\rho)$ 反传，$1/|y|$ 会进到 ratio 的梯度里；verl 把这一项停掉了，长度权重交给后面的 `agg_loss`。log 在 exp 之前再夹到不超过 10。窗口用 $3\times 10^{-4}$ / $4\times 10^{-4}$，因为几何平均离 1 很近，套 0.2 几乎永远不会触发。GSPO 这条函数自己不再做 dual-clip。

```python
def gspo_losses(logp, old_logp, adv, response_mask, eps_low=3e-4, eps_high=4e-4):
    log_ratio = logp - old_logp
    lengths = response_mask.sum(dim=-1).clamp(min=1)          # [B]
    # (1/|y|) * Σ_t log ρ_t ，只在 response token 上平均。
    seq_log_ratio = (log_ratio * response_mask).sum(dim=-1) / lengths
    # 前向 = 广播后的序列比；序列均值不参与反传。
    log_s = logp - logp.detach() + seq_log_ratio.detach()[:, None]
    log_s = log_s.clamp(max=10.0)
    rho = log_s.exp()
    unclipped = -adv * rho
    clipped = -adv * rho.clamp(1.0 - eps_low, 1.0 + eps_high)
    return torch.maximum(unclipped, clipped), rho
```

$\pi_\theta=\pi_{\mathrm{old}}$ 时，token 比和序列比都是 1，GSPO 的 clip 和 GRPO 没有区别。TRL 文档写明，`importance_sampling_level="sequence"` 要在 `steps_per_generation > gradient_accumulation_steps` 或 `num_iterations > 1` 时才看得出差别。

SAPO 拿掉了硬 clip，改成一个温度门。verl `compute_policy_loss_sapo` 和 TRL `loss_type="sapo"` 用的是同一个门：$f(x)=\sigma(\tau(x-1))\cdot 4/\tau$。$A>0$ 用 $\tau_{\mathrm{pos}}$（TRL 默认 1.0，verl 字段 `tau_pos`），否则用更大的 $\tau_{\mathrm{neg}}$（TRL 默认 1.05），负优势衰减得更快。损失是 $-f(\rho)A$，归约被 verl 写死成 `seq-mean-token-mean`。

```python
def sapo_losses(logp, old_logp, adv, tau_pos=1.0, tau_neg=1.05):
    rho = (logp - old_logp).clamp(-20.0, 20.0).exp()
    tau = torch.where(adv > 0, torch.full_like(adv, tau_pos), torch.full_like(adv, tau_neg))
    gate = torch.sigmoid(tau * (rho - 1.0)) * (4.0 / tau)
    return -(gate * adv), rho
```

还有一层：采样引擎和训练前向的 logprob 可能对不上。这是另外乘在算好的 token loss 上的权重，上面的 PPO clip 照样要做。TRL 默认 `vllm_importance_sampling_correction=True`、`vllm_importance_sampling_mode="sequence_mask"`、上界 `vllm_importance_sampling_clip_max=3.0`。`*_truncate` 把比值夹进 $[C_{\min},C_{\max}]$；`*_mask` 把区间外的比值改成 0，这个样本这一步就没有梯度。verl 把同样的系数放进 `rollout_is_weights`，在 `pg_losses` 上再乘一次。

```python
def rollout_is_weight(rho, mode="sequence_mask", c_max=3.0, c_min=None):
    # rho 已经是 token 比或序列比。mask：越界变 0。truncate：夹到区间里，梯度仍在（除非你再 detach）。
    if mode.endswith("mask"):
        keep = rho <= c_max if c_min is None else (rho >= c_min) & (rho <= c_max)
        return rho * keep.float()
    lo = rho.new_zeros(()) if c_min is None else rho.new_full((), c_min)
    return rho.clamp(min=lo, max=c_max)
```

## 归约

clip 之后，每个 token 有一个损失 $\ell_{b,t}$，verl 的 `agg_loss` 把它收成标量。数据并行时还要乘 `dp_size`、除全局 token 数，这样切多少张卡都不改变损失尺度。下面按单卡写（`dp_size=1`）。

```python
def agg_loss(loss_mat, response_mask, mode, loss_scale_factor=None):
    # loss_mat, response_mask: [B, T]
    # token-mean：verl 默认，也是 TRL loss_type="dapo"（再除的是全局累积 batch 的有效 token，不只是这张 micro-batch）。
    if mode == "token-mean":
        return (loss_mat * response_mask).sum() / response_mask.sum().clamp(min=1)
    # token-sum：不除 token 数。长 batch 的梯度按 token 总数线性变大。
    if mode == "token-sum":
        return (loss_mat * response_mask).sum()
    seq_sum = (loss_mat * response_mask).sum(dim=-1)          # [B]
    seq_len = response_mask.sum(dim=-1)                        # [B]
    valid = (seq_len > 0).float()
    # seq-mean-token-sum：每条先求和，再对有效序列平均。长回复更响。
    # 这是 TRL loss_type="grpo" 去掉「再除 |o_i|」之前的近亲；TRL 的 "grpo" 还要再除 |o_i|，见下。
    if mode == "seq-mean-token-sum":
        return (seq_sum * valid).sum() / valid.sum().clamp(min=1)
    # seq-mean-token-sum-norm：上面再除一个常数。verl 默认常数是 mask 的时间维（padding 后的长度）。
    # 设成 max_completion_length 就对齐 TRL loss_type="dr_grpo" 的 1/(L·G) 里的 L。
    # 分母不随这条回复的真实长度变，短回复不会因为除以更小的 |o_i| 而被放大。
    if mode == "seq-mean-token-sum-norm":
        horizon = response_mask.size(-1) if loss_scale_factor is None else loss_scale_factor
        return (seq_sum * valid).sum() / valid.sum().clamp(min=1) / horizon
    # seq-mean-token-mean：每条内部先平均，再对序列平均。每条回复权重相同。
    # TRL loss_type="grpo" 是这一式。GSPO 例子显式要求它。verl 的 SAPO 把它写死。
    if mode == "seq-mean-token-mean":
        seq_mean = seq_sum / (seq_len + 1e-8)
        return (seq_mean * valid).sum() / valid.sum().clamp(min=1)
    raise ValueError(mode)
```

下面是 TRL `loss_type` 和 verl 模式的对应。TRL 当前默认是 `"dapo"`，DeepSeekMath 的原版对应 `"grpo"`；文档把 `"grpo"` 标成会偏好「正优势的短回复、负优势的长回复」。

| 你要的归约 | verl `loss_agg_mode` | TRL `loss_type` |
| --- | --- | --- |
| 全局有效 token 等权 | `token-mean` | `dapo`（默认；分母是累积后的全局 token） |
| 只在本卡 micro-batch 里按 token 平均 | 单卡时同 `token-mean` | `bnpo`（`per_device_train_batch_size==1` 时退回 `grpo`） |
| 每条回复等权，内部再对 token 平均 | `seq-mean-token-mean` | `grpo` |
| 每条先求和再平均，再除常数长度 | `seq-mean-token-sum-norm` | `dr_grpo`（常数是 `max_completion_length`） |

Dr.GRPO 在 verl 里要三处一起改，光改归约不够：`norm_adv_by_std_in_grpo=False`、`loss_agg_mode=seq-mean-token-sum-norm`、`use_kl_loss=False`。TRL 这边是 `scale_rewards=False` 加 `loss_type="dr_grpo"`。

KL 不在这张归约表里。TRL 的 `beta`（默认 0）大于 0 时，可导的 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 加在每个 token 的 $l_{i,t}$ 里，和 ratio 一起反传；`use_bias_correction_kl=True`（默认）还会再乘重要性比。verl 的 `use_kl_loss` 是 surrogate 旁边另加的一项，`kl_loss_type=low_var_kl` 就是 Schulman $k_3$。PPO 也可以先把 KL 扣进奖励分数（reward）再送进 GAE，那会改变优势的符号，见 `ant-grpo-kl-vs-ppo`。

## 对照着开

TRL 和 verl 的配置并排写出来是这样：

```python
from trl import GRPOConfig

# 默认已经是 token 等权（dapo）+ 组内除 std + token 级 ρ + 对称 0.2。
# 论文 GRPO 要显式改回 loss_type="grpo"。
paper_grpo = GRPOConfig(
    loss_type="grpo",
    importance_sampling_level="token",
    scale_rewards="group",
    num_generations=8,
    beta=0.0,
    epsilon=0.2,
)
dapo = GRPOConfig(
    loss_type="dapo",
    epsilon=0.2,
    epsilon_high=0.28,          # clip-higher
    mask_truncated_completions=True,
    beta=0.0,
)
gspo = GRPOConfig(
    loss_type="grpo",            # 序列等权。换成 "dapo" 就改成 token 等权
    importance_sampling_level="sequence",
    beta=0.0,
    epsilon=3e-4,
    epsilon_high=4e-4,
    gradient_accumulation_steps=1,
    steps_per_generation=4,      # 必须大于 gradient_accumulation_steps，序列比才不等于 1
)
cispo = GRPOConfig(loss_type="cispo", epsilon_high=5.0)
sapo = GRPOConfig(loss_type="sapo", sapo_temperature_pos=1.0, sapo_temperature_neg=1.05)
```

```yaml
# verl：同一条 PPO trainer。PPO 把 adv_estimator 改成 gae，并训 critic。
# GRPO
algorithm:
  adv_estimator: grpo
  norm_adv_by_std_in_grpo: true
actor_rollout_ref:
  rollout:
    n: 8
  actor:
    policy_loss:
      loss_mode: vanilla          # gspo / sapo / gpg
    loss_agg_mode: token-mean
    clip_ratio: 0.2
    clip_ratio_low: 0.2           # DAPO 保持 0.2
    clip_ratio_high: 0.2          # DAPO 改成 0.28
    clip_ratio_c: 3.0             # dual-clip，只作用于 A<0
    use_kl_loss: true
    kl_loss_coef: 0.001
    kl_loss_type: low_var_kl

# GSPO：优势仍走 grpo，loss_mode 换成 gspo。例子里的窗口和 dual-clip 上界如下。
#   policy_loss.loss_mode: gspo
#   loss_agg_mode: seq-mean-token-mean
#   clip_ratio_low: 3.0e-4
#   clip_ratio_high: 4.0e-4
#   clip_ratio_c: 10.0
#   use_kl_loss: false
```

`policy_loss.loss_mode=vanilla` 进的是 `compute_policy_loss_vanilla`（旧名 `compute_policy_loss`），先做不对称 clip，再对负优势做 dual-clip，最后调 `agg_loss`。`gspo` 走 `compute_policy_loss_gspo`，不做 dual-clip。

## 上面这些函数各自对应哪段源码

上面的 Python 是照着源码收过的白板版。三个框架的调用顺序、张量在哪一步从标量变成 token、GSPO 到底改优势还是改 KL，按仓库拆开讲：

- Miles（slime 的企业向分支，SGLang + Megatron / FSDP2）：`code-fw-miles`
- verl（Ray driver 上算优势，worker 上算 loss）：`code-fw-verl`
- TRL（单进程 `GRPOTrainer._compute_loss`）：`code-fw-trl`

| 白板函数 | Miles | verl | TRL |
| --- | --- | --- | --- |
| 组内减均值 / 除 std | `train_data_conversion._normalize_rewards_by_rollout`，在进 trainer 之前改 reward | `core_algos.compute_grpo_outcome_advantage`，按 `uid` 分组 | `_generate_and_score_completions` 里 `rewards.view(-1, num_generations)` |
| 把标量铺到 token | `math_utils.get_grpo_returns` | 同一函数末尾 `scores.unsqueeze(-1) * response_mask` | `_compute_loss` 里 `advantages.unsqueeze(1)` |
| GAE | `get_advantages_and_returns_batch` | `compute_gae_advantage_return`，之后 `masked_whiten` | 没有这条路径 |
| 对称 / 不对称 clip | `math_utils.compute_policy_loss` | `compute_policy_loss_vanilla` | `_compute_loss` 里 `loss_type in {grpo,bnpo,dr_grpo,dapo,luspo}` |
| dual-clip | 同一函数，`eps_clip_c is not None` | 同一函数，`clip_ratio_c` | 没有。另有 `delta` 把 $\rho$ 再夹一次上界 |
| GSPO 的序列比 | `compute_gspo_kl`：序列均值广播成每个 token 的 `ppo_kl`，clip 函数不换 | `compute_policy_loss_gspo`：序列均值 detach，梯度走 token $\log\pi$ | `importance_sampling_level="sequence"`：`log_ratio` 先在长度上平均，梯度穿过这个均值 |
| CISPO | 不在默认 `policy_loss` 里 | 不在 `core_algos` 的 vanilla / gspo 里 | `loss_type=="cispo"`：`clamp(coef_1, max=epsilon_high).detach()` |
| token / 序列归约 | `get_sum_of_sample_mean` + `--calculate-per-token-loss` | `agg_loss` | `_compute_loss` 后半按 `loss_type` 分支 |

## 简单测试怎么写

把参考实现与以下测试按顺序放进 solution.py，运行 python3 solution.py。数值测试使用同一 PyTorch 环境，浮点数用带容差的比较；通过后输出 simple tests passed。

只复制前面的 PyTorch 函数定义，不需要“对照着开”中的 TRL 配置。用正负优势各一个位置，手算 PPO 裁剪后的逐 token loss 为 -1.2 与 0.8；这是结果测试，函数内部的参数合法性断言不能代替它。

```python
losses, ratio = ppo_clip_losses(torch.tensor([1.5, 0.5]).log(), torch.zeros(2), torch.tensor([1., -1.]))
torch.testing.assert_close(losses, torch.tensor([-1.2, 0.8]))
torch.testing.assert_close(ratio, torch.tensor([1.5, 0.5]))
print("simple tests passed")
```

## 追问

**改 `loss_agg_mode` 会改优势吗？**
不会。优势在 clip 之前就算完了，归约只决定这些 token 损失怎么加总。

**`n=1` 在 verl 里是不是零梯度？**
源码的单样本分支不是零。组里只有 1 条时，mean 被设成 0、std 设成 1，优势等于原始分数；数学上 $n=1$ 减掉自己的均值才是 0。要做组内对照，仍然得 `rollout.n>1`，文档也这样要求，见 `sys-rl-group-n`。

**GSPO 的 $1/|y|$ 在梯度的哪一段？**
verl 把序列均值 detach 了，ratio 的梯度里没有 $1/|y|$，长度出现在 `seq-mean-token-mean` 的分母里。直接对 $\exp(\mathrm{mean}\log\rho)$ 反传，才会在 ratio 里再除一次长度。

**dual-clip 和 DAPO 的上界是一回事吗？**
两回事。`clip_ratio_high` 移动的是 $1+\varepsilon$，正负优势都看这个窗口；`clip_ratio_c` 只封 $A\lt 0$ 且 $\rho$ 很大时的损失，默认 3，离 1 很远。

**CISPO 越界还有梯度吗？**
有。权重是 detach 后的常数，反传走 $\log\pi$；PPO / GRPO / GSPO 的 `maximum` 在有利一侧越界时梯度是 0，见 `pt-cispo`。

相关：`code-grpo`（组优势片段）、`code-ppo-clip`（对称 clip 的符号）、`code-gae`（GAE 的 terminal / truncation）、`pt-cispo`（CISPO 的动机）、`pt-dapo`（DAPO 的四个旋钮）、`baidu-grpo-loss-agg`（归约口试）
