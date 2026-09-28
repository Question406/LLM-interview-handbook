---
id: code-ppo-grpo-gspo
section: rl-coding
order: 8
level: S
title: 手写 PPO / GRPO / GSPO：TRL 和 verl 各改哪一段？
quick: >-
  优势、ratio、clip、归约是四根独立旋钮。PPO 用 GAE 再 whiten；GRPO 用组内
  $(r-\mathrm{mean})/(\mathrm{std}+\varepsilon)$，Dr.GRPO 去掉除 std。Clip 有对称 PPO、DAPO 的不对称上界、verl
  的 dual-clip（$A\lt 0$ 时用 `clip_ratio_c` 封顶）、CISPO 的 detach 权重、GSPO 的序列几何平均。归约对照
  verl 的 `agg_loss` 和 TRL 的 `loss_type`（默认已是 `dapo`，不是论文里的 `grpo`）。
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

组优势片段见 `code-grpo`，对称 clip 的符号见 `code-ppo-clip`，GAE 的 terminal / truncation 见 `code-gae`。CISPO 的动机见 `pt-cispo`，DAPO 的四个旋钮见 `pt-dapo`，归约口试见 `baidu-grpo-loss-agg`。下面按 verl `core_algos.py` 和 TRL `GRPOConfig` 的分支写，方便把变体对齐到同一张张量上。

一次更新拆成四段，互相可以换：

1. 优势 $A$：GAE（PPO）或组相对（GRPO 一族）。
2. 重要性比 $\rho$：token 级，或序列几何平均（GSPO）。
3. clip：对称、不对称、dual-clip、CISPO、SAPO。clip 的是目标里的 $\rho$，网络里的 $\rho$ 不会被改写。
4. 归约：token 等权、序列等权、常数长度归一。这一段决定长回复占多少梯度。

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

PPO 的 $A$ 来自 critic。verl 的 `compute_gae_advantage_return` 在 response mask 为 0 的位置跳过 TD，最后对 advantage 做 masked whiten（减全局均值、除全局标准差）。outcome 奖励通常只加在最后一个有效 token 上。$\gamma=\lambda=1$ 时没有折扣，句末分会沿整段传回去。

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

GRPO 不训 $V$。verl `compute_grpo_outcome_advantage` 先把 token 奖励沿时间求和，得到每条回复一个标量，再按 prompt id 分组。`norm_adv_by_std_in_grpo=True` 时除组内标准差（原论文）；`False` 时只减均值，这是 Dr.GRPO。标量再乘 `response_mask` 广播回每个 response token，同一条回复上的 token 共享同一个 $A$。

组里只有 1 条时，这份源码把 mean 设成 0、std 设成 1，优势等于原始分数，不会变成 0。数学上 $n=1$ 减掉自己的均值才是 0。文档仍要求 `rollout.n>1`。`torch.std` 默认 `unbiased=True`（除 $G-1$）。

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

TRL 的 `scale_rewards` 管的是这一步的除标准差，不改归约：`"group"`（默认）组内 std；`"batch"` 整批一个 std（Lite PPO）；`False` / `"none"` 不除 std。多奖励时 `multi_objective_aggregation="sum_then_normalize"` 先加权求和再标准化；`"normalize_then_sum"` 是 GDPO，每个奖励维先在组内标准化再相加，避免大尺度奖励淹没其余项。verl 对应 `compute_gdpo_outcome_advantage`。

## Clip

下面的 `pg_loss` 都是要最小化的数，所以相对论文里的 $\min(\rho A,\mathrm{clip}(\rho)A)$ 多了一个负号。`maximum(-ρA, -clip(ρ)A)` 和 $-\mathrm{minimum}(ρA, \mathrm{clip}(ρ)A)$ 是同一个量。

对称 PPO（verl `clip_ratio`，TRL `epsilon`，两边默认 0.2）：

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

DAPO clip-higher：下界仍是 `epsilon`（0.2），上界换成更大的 `epsilon_high`（论文 0.28）。正优势可以走得更远，负优势仍被较紧的下界挡住。TRL 不设 `epsilon_high` 时上下界相同。verl 的字段是 `clip_ratio_low` / `clip_ratio_high`，缺省都回落到 `clip_ratio`。

```python
def asymmetric_clip_losses(logp, old_logp, adv, eps_low=0.2, eps_high=0.28):
    log_ratio = (logp - old_logp).clamp(-20.0, 20.0)
    rho = log_ratio.exp()
    unclipped = -adv * rho
    clipped = -adv * rho.clamp(1.0 - eps_low, 1.0 + eps_high)
    return torch.maximum(unclipped, clipped), rho
```

verl 在对称 / 不对称 clip 之后还有 dual-clip（`clip_ratio_c`，默认 3.0，必须大于 1；GSPO 例子里设成 10）。只在 $A\lt 0$ 时生效：负优势且 $\rho$ 很大时，$-A\rho$ 会变成巨大的正损失，把这一步梯度吃掉。dual-clip 把这份损失封在 $-A\cdot c$。$A\ge 0$ 的样本保持普通 PPO clip。

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

CISPO 换的是 clip 对象，不是优势。TRL `loss_type="cispo"`：clip 的是 IS 权重本身，再 detach，乘上 $A$ 和 $\log\pi_\theta$。越界 token 仍有 $\nabla\log\pi$。ScaleRL 把上界放在 `epsilon_high`，推荐 5.0，不是 $1+0.2$。指标 `cispo_clip_ratio` 统计的是正优势且 $\rho>\varepsilon_{\mathrm{high}}$ 的比例。论文里的双侧形式见 `pt-cispo`。

```python
def cispo_losses(logp, old_logp, adv, eps_max=5.0):
    rho = (logp - old_logp).exp()
    # detach：上界是常数系数。反传只走 logp，不走被截断的 ρ。
    weight = rho.clamp(max=eps_max).detach()
    return -(weight * adv * logp), rho
```

GSPO 把 clip 的对象换成序列几何平均，优势仍是组相对。verl `compute_policy_loss_gspo` 的前向值等于把 $s_i=\exp(\mathrm{mean}_t\log\rho_t)$ 广播到每个 token，但序列均值被 detach，梯度只从当前 token 的 $\log\pi$ 走：

$$
\log s_{i,t}=\mathrm{sg}[\log s_i]+\log\pi_\theta(y_t)-\mathrm{sg}[\log\pi_\theta(y_t)].
$$

数值上 $s_{i,t}=s_i$。若直接对 $\exp(\mathrm{mean}\log\rho)$ 反传，$1/|y|$ 会进 ratio 的梯度；verl 把这一项停掉，长度权重交给后面的 `agg_loss`。log 在 exp 之前再夹到不超过 10。窗口用 $3\times 10^{-4}$ / $4\times 10^{-4}$，因为几何平均离 1 很近，套 0.2 几乎永不触发。GSPO 这条函数本身不再做 dual-clip。

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

$\pi_\theta=\pi_{\mathrm{old}}$ 时 token 比和序列比都是 1，GSPO 的 clip 不会和 GRPO 分开。TRL 写明 `importance_sampling_level="sequence"` 要在 `steps_per_generation > gradient_accumulation_steps` 或 `num_iterations > 1` 时才看得到差别。

SAPO 拿掉硬 clip，改成温度门。verl `compute_policy_loss_sapo` 和 TRL `loss_type="sapo"` 是同一个门：$f(x)=\sigma(\tau(x-1))\cdot 4/\tau$。$A>0$ 用 $\tau_{\mathrm{pos}}$（TRL 默认 1.0，verl 字段 `tau_pos`），否则用更大的 $\tau_{\mathrm{neg}}$（TRL 默认 1.05），负优势衰减更快。损失是 $-f(\rho)A$，归约被 verl 写成死的 `seq-mean-token-mean`。

```python
def sapo_losses(logp, old_logp, adv, tau_pos=1.0, tau_neg=1.05):
    rho = (logp - old_logp).clamp(-20.0, 20.0).exp()
    tau = torch.where(adv > 0, torch.full_like(adv, tau_pos), torch.full_like(adv, tau_neg))
    gate = torch.sigmoid(tau * (rho - 1.0)) * (4.0 / tau)
    return -(gate * adv), rho
```

采样引擎和训练前向的 logprob 还可能不一致。这是另一层权重，乘在已经算好的 token loss 上，不替代上面的 PPO clip。TRL 默认 `vllm_importance_sampling_correction=True`、`vllm_importance_sampling_mode="sequence_mask"`、上界 `vllm_importance_sampling_clip_max=3.0`。`*_truncate` 把比值夹进 $[C_{\min},C_{\max}]$；`*_mask` 把区间外的比值改成 0，该样本这一步没有梯度。verl 把同样的系数放进 `rollout_is_weights`，在 `pg_losses` 上再乘一次。

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

clip 之后每个 token 有一个损失 $\ell_{b,t}$。verl `agg_loss` 把它收成标量。数据并行时还要乘 `dp_size`、除全局 token 数，这样切多少卡不改变损失尺度。下面按单卡写（`dp_size=1`）。

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

TRL `loss_type` 和 verl 模式的对应。TRL 当前默认是 `"dapo"`，不是 DeepSeekMath 的 `"grpo"`。文档把 `"grpo"` 标成会偏好「正优势的短回复、负优势的长回复」。

| 你要的归约 | verl `loss_agg_mode` | TRL `loss_type` |
| --- | --- | --- |
| 全局有效 token 等权 | `token-mean` | `dapo`（默认；分母是累积后的全局 token） |
| 只在本卡 micro-batch 里按 token 平均 | 单卡时同 `token-mean` | `bnpo`（`per_device_train_batch_size==1` 时退回 `grpo`） |
| 每条回复等权，内部再对 token 平均 | `seq-mean-token-mean` | `grpo` |
| 每条先求和再平均，再除常数长度 | `seq-mean-token-sum-norm` | `dr_grpo`（常数是 `max_completion_length`） |

Dr.GRPO 在 verl 里要三处一起改，只改归约不够：`norm_adv_by_std_in_grpo=False`、`loss_agg_mode=seq-mean-token-sum-norm`、`use_kl_loss=False`。TRL 侧是 `scale_rewards=False` 加上 `loss_type="dr_grpo"`。

KL 不进这张归约表。TRL `beta`（默认 0）大于 0 时，可导的 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 加在每个 token 的 $l_{i,t}$ 里，和 ratio 一起反传。`use_bias_correction_kl=True`（默认）还会再乘重要性比。verl 的 `use_kl_loss` 是 surrogate 旁边另加的一项，`kl_loss_type=low_var_kl` 即 Schulman $k_3$。PPO 也可以先把 KL 扣进 reward 再送 GAE，那会改优势的符号，见 `ant-grpo-kl-vs-ppo`。

## 对照着开

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

`policy_loss.loss_mode=vanilla` 进 `compute_policy_loss_vanilla`（旧名 `compute_policy_loss`）。它先做不对称 clip，再对负优势做 dual-clip，最后调用 `agg_loss`。`gspo` 走 `compute_policy_loss_gspo`，不做 dual-clip。

## 上面这些函数各自对应哪段源码

上面的 Python 是按源码收过的白板版。三个框架的调用顺序、张量在哪一步从标量变成 token、以及 GSPO 到底改优势还是改 KL，按仓库拆开：

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

## 追问

- **改 `loss_agg_mode` 会改优势吗？** 不会。优势在 clip 之前就算完了。归约只决定这些 token 损失怎么加总。
- **`n=1` 在 verl 里是不是零梯度？** 源码的单样本分支不是。mean 被设成 0、std 设成 1，优势等于原始分数。要组内对照，仍得 `rollout.n>1`，见 `sys-rl-group-n`。
- **GSPO 的 $1/|y|$ 在梯度的哪一段？** verl 把序列均值 detach 了，ratio 的梯度不含 $1/|y|$。长度出现在 `seq-mean-token-mean` 的分母里。直接对 $\exp(\mathrm{mean}\log\rho)$ 反传，才会在 ratio 里再除一次长度。
- **dual-clip 和 DAPO 的上界是一回事吗？** 不是。`clip_ratio_high` 移动的是 $1+\varepsilon$，正负优势都看这个窗口。`clip_ratio_c` 只封 $A\lt 0$ 且 $\rho$ 很大时的损失，默认 3，不在 1 附近。
- **CISPO 越界还有梯度吗？** 有。权重是 detach 常数，反传走 $\log\pi$。PPO / GRPO / GSPO 的 `maximum` 在有利一侧越界时梯度是 0。见 `pt-cispo`。
