---
id: code-fw-verl
section: rl-coding
order: 10
level: S
title: verl 里优势在 driver、clip 在 worker，代码怎么接？
quick: "优势在 driver 的 `RayPPOTrainer.fit` 里算，GRPO 按 `uid` 分组；clip 在 actor worker 的 policy loss 里，`vanilla` 模式含 dual-clip。"
tags:
  - verl
  - GRPO
  - PPO
  - GSPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: verl RayPPOTrainer
    url: https://github.com/verl-project/verl/blob/main/verl/trainer/ppo/ray_trainer.py
    type: primary
  - title: verl core_algos.py
    url: https://github.com/verl-project/verl/blob/main/verl/trainer/ppo/core_algos.py
    type: primary
  - title: verl GRPO
    url: https://verl.readthedocs.io/en/latest/algo/grpo.html
    type: primary
---

公式和开关对照见 `code-ppo-grpo-gspo`。重算 logprob 的原因见 `meituan-verl-recompute-logprob`。当前仓库里 `RayPPOTrainer` 标了 deprecated，注释写着 v0.9.0 会拆掉，要换 `trainer.use_v1=True`。下面这条数据流仍是 `fit()` 里能对上的实现。

## fit() 里一步的顺序

Driver 不跑模型前向。它通过 Ray 调 worker，优势在 driver 上算，注释写明 advantage 很轻。

1. DataLoader 取出 prompt batch。给每条 prompt 一个 `uid`（`uuid4`）。这个 id 是后面 GRPO 分组的键，不是 sample 下标。
2. `batch.repeat(repeat_times=rollout.n, interleave=True)`，同一输入提示 的 $n$ 条在 batch 里交错排开。`n` 就是组大小。
3. `async_rollout_manager.generate_sequences`。REMAX 会在同一次请求里再拼一条 greedy baseline（`__do_sample__=False`），避免引擎 sleep 之后再发第二次。
4. 奖励分数（reward）：可选 colocated 奖励模型（RM），然后 `extract_reward` 得到 `reward_tensor`。
5. 旧 logprob 有两条路。默认重算：`_compute_old_log_prob`，训练图上再跑一遍 actor，得到 `old_log_probs`。`algorithm.rollout_correction.bypass_mode` 为真时不重算，直接把 采样轨迹（rollout） 引擎的 logprob 当成 old。注释把前者叫三策略（$\pi_{\mathrm{rollout}}$、$\pi_{\mathrm{old}}$、$\pi_\theta$），后者叫两策略。
6. 有 reference 就 `_compute_ref_log_prob`。`use_critic` 时 `_compute_values`。
7. `token_level_scores = reward_tensor`。`algorithm.use_kl_in_reward` 为真则 `apply_kl_penalty`，把 KL 扣进 token reward，再用自适应 $\beta$；否则 `token_level_rewards = token_level_scores`。
8. 非 bypass 且 batch 里有 `rollout_log_probs` 时，`compute_rollout_correction_and_add_to_batch` 写出 IS 权重。这层乘在后面的 policy loss 上，不替代 PPO clip。
9. `compute_advantage(...)`。
10. 有 Critic 时先 `_update_critic`。`trainer.critic_warmup` 还没过完就只更新 rollout 权重、不更新 actor。过了才 `_update_actor`。

`adv_estimator=gae` 才会走 critic。GRPO 配置把估计器设成 `grpo`，这条 fit 里 values / critic update 都不进。

## compute_advantage 怎么分发

`ray_trainer.compute_advantage` 先补 `response_mask`。然后：

- `AdvantageEstimator.GAE`：`core_algos.compute_gae_advantage_return`。从 response 末尾往前，`mask=0` 的位置把 next value 和 GAE 原样留住，不把 pad 上的 $V$ 写进 delta。返回 `advantages + values`。advantage 再 `masked_whiten`。`use_pf_ppo` 时还有一次 `compute_pf_ppo_reweight_data`。
- `AdvantageEstimator.GRPO`：`compute_grpo_outcome_advantage`。分组键是 `non_tensor_batch["uid"]`，不是「每 n 条一切」。`norm_adv_by_std_in_grpo` 从 `algorithm.norm_adv_by_std_in_grpo` 读，默认真。
- 其他名字（`rloo`、`reinforce_plus_plus`、`gpg`、`gdpo`、`optimal_token_baseline` 等）走 `get_adv_estimator_fn` 注册表。GDPO 会把 `non_tensor_batch` 和整个 batch 传进去，按奖励维度分别做组内标准化。optimal token baseline 还要求 actor 事先写出 `sum_pi_squared`。

GRPO 函数内部：`scores = token_level_rewards.sum(-1)`，同一 `uid` 的标量放进一个 list。组长度大于 1：减 `mean`，`norm_adv_by_std_in_grpo` 为真再除 `torch.std + 1e-6`（`torch.std` 默认无偏，除 $G-1$）。组长度等于 1：代码把 mean 写成 0、std 写成 1，优势等于原始分数，不是 0。组长度 0 才抛错。最后 `scores.unsqueeze(-1) * response_mask`，同一条回复的每个有效 token 共享这个标量。返回的 advantages 和 returns 是同一张量。

Dr.GRPO 在这里只关除 std。长度归约和 KL 要另外改 `loss_agg_mode` 和 `use_kl_loss`，见 `code-ppo-grpo-gspo`。

## worker 上的 policy loss

`core_algos.py` 用 `@register_policy_loss` 注册 loss。actor 配置 `policy_loss.loss_mode` 选函数。

`vanilla`（以及仍可用、但标了 deprecated 的 `compute_policy_loss`）步骤：

1. `log_ratio = log_prob - old_log_prob`，夹到 $[-20, 20]$，再 exp 得到 $\rho$。
2. `pg_losses1 = -A * ρ`，`pg_losses2 = -A * clamp(ρ, 1-clip_low, 1+clip_high)`。`clip_ratio_low` / `clip_ratio_high` 缺省回落到 `clip_ratio`（论文里的 $\varepsilon$，常见 0.2）。DAPO 把 high 设成 0.28。
3. `clip_pg_losses1 = max(pg_losses1, pg_losses2)`。这就是最小化 $-\min(\rho A, \mathrm{clip}(\rho)A)$。`pg_losses2 > pg_losses1` 的位置记进 `pg_clipfrac`。
4. dual-clip：`clip_ratio_c` 默认 3，必须大于 1。`pg_losses3 = -A * clip_ratio_c`。只在 `advantages < 0` 时用 `min(pg_losses3, clip_pg_losses1)` 换掉上一步的损失。负优势且 $\rho$ 很大时，$-A\rho$ 会非常大；这一支把它封在 $-A\cdot c$。正优势不走这支。触发比例记在 `pg_clipfrac_lower`。
5. 若 batch 里有 `rollout_is_weights`，乘到 `pg_losses` 上。
6. `agg_loss(...)`。

`gspo` 注册的是 `compute_policy_loss_gspo`，推荐 `loss_agg_mode="seq-mean-token-mean"`，但函数允许传入别的模式，注释写明这和论文「死在序列平均」不同。序列比：

```python
seq_lengths = response_mask.sum(-1).clamp(min=1)
negative_approx_kl_seq = (negative_approx_kl * response_mask).sum(-1) / seq_lengths
log_seq_importance_ratio = log_prob - log_prob.detach() + negative_approx_kl_seq.detach().unsqueeze(-1)
log_seq_importance_ratio = log_seq_importance_ratio.clamp(max=10.0)
seq_importance_ratio = log_seq_importance_ratio.exp()
```

前向每个 token 的比值等于 $\exp(\mathrm{mean}_t \log\rho_t)$。序列均值被 detach，梯度只从 `log_prob - log_prob.detach()` 走，也就是当前 token 的 $\log\pi$。长度 $1/|y|$ 不在 ratio 的梯度里，只在后面的 `seq-mean-token-mean` 分母里。然后同样是 `maximum(-A*ρ, -A*clamp(ρ))`，窗口来自 `clip_ratio_low/high`。GSPO 例子把它们设成 $3\times 10^{-4}$ 和 $4\times 10^{-4}$。这条函数没有 dual-clip，`pg_clipfrac_lower` 固定返回 0。例子里的 `clip_ratio_c: 10` 因此不会进 GSPO 这条 loss。

`sapo` 不用 clamp。门是 $\sigma(\tau(\rho-1))\cdot 4/\tau$，$A>0$ 用 `tau_pos`，否则 `tau_neg`。`agg_loss` 被写成死的 `seq-mean-token-mean`。

`dppo_tv` / `dppo_kl` 用截断重要性采样代替 dual-clip：`ratio.clamp(max=clip_ratio_c)`，默认上界 20，注释指向 DPPO 的 total variation / KL 约束。

## agg_loss 的四种分母

`loss_mat` 是 `[micro_batch, response_length]`。数据并行大于 1 时必须传入全局 token 数或全局 batch 大小，再乘 `dp_size`，这样卡数变化不改变损失尺度。单卡时：

- `token-mean`：有效 token 之和 / 有效 token 数。actor 默认。
- `token-sum`：只求和，再乘 `dp_size`。梯度随 token 总数变。
- `seq-mean-token-sum`：每条先对 token 求和，再对有效序列数平均。长回复更响。
- `seq-mean-token-sum-norm`：上式再除 `loss_scale_factor`。缺省是 `loss_mask.shape[-1]`，也就是 padding 后的长度。设成常数最大长度，就对齐 Dr.GRPO 的 $1/(LG)$。
- `seq-mean-token-mean`：每条内部先除自己的 token 数，再对序列平均。全 mask 的序列被丢掉。

KL 若走 `use_kl_loss`，是 actor loss 旁边加的一项，类型常见 `low_var_kl`（Schulman $k_3$，log-ratio 再夹）。若走 `use_kl_in_reward`，KL 在 `compute_advantage` 之前就进了 `token_level_rewards`，GAE 或 GRPO 都会看见它。两处不要同时当成同一个 $\beta$。
