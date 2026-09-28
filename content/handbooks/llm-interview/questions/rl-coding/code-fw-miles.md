---
id: code-fw-miles
section: rl-coding
order: 11
level: S
title: Miles 里 GRPO / GSPO / PPO 的代码从 train.py 走到哪？
quick: >-
  Miles 是 slime 的分支：SGLang 采样，Megatron 或 FSDP2 训练。组内减均值发生在
  `train_data_conversion._normalize_rewards_by_rollout`，进 loss 之前。GSPO 不换
  `compute_policy_loss`，只把 `ppo_kl` 改成整段 log-ratio 的平均再广播。Clip 和 dual-clip
  都在 `math_utils.compute_policy_loss`。
tags:
  - Miles
  - slime
  - GRPO
  - GSPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: radixark/miles
    url: https://github.com/radixark/miles
    type: primary
  - title: Miles train.py
    url: https://github.com/radixark/miles/blob/main/train.py
    type: primary
  - title: Miles policy loss
    url: https://github.com/radixark/miles/blob/main/miles/backends/training_utils/loss_hub/losses.py
    type: primary
---

算法公式对照见 `code-ppo-grpo-gspo`。slime 的字段和异步时间线见 `slime-async-train`、`slime-data-buffer`。Miles 的包名是 `miles`，入口仍是 `train.py` / `train_async.py`，`--advantage-estimator` 的可选取值是 `grpo`、`gspo`、`ppo`、`reinforce_plus_plus`、`reinforce_plus_plus_baseline`。

## 一步在进程之间怎么走

`train.py` 的 `train()` 是同步环。异步环在 `train_async.py`，开头就断言 `--fully-async` 不能进 `train.py`。

1. `create_rollout_components` 拉起 SGLang 引擎和 `RolloutExecutor`。
2. `create_training_models` 建 actor；`--advantage-estimator ppo` 时 `arguments.py` 把 `use_critic` 设成真，才会有 critic。
3. 第一次 `update_weights`，把训练权重推到 SGLang，再开始采样。
4. 每个 `rollout_id`：`inference_controller.prepare_rollout` → `rollout_executor.get` 拿到这一批轨迹。colocate 时按 `--offload-rollout` / `--offload-train` 把 KV、权重在推理和训练之间腾挪。
5. 有 critic：先 `critic_model.train`，把它的 value 当 `external_data` 传给 `actor_model.train`。没有 critic：actor 单独 `train`。
6. 再 `update_weights`，下一轮采样用新权重。

奖励的组内标准化不在 actor 的 backward 里。`ray/rollout/train_data_conversion.py` 的 `_post_process_rewards` 在样本打包进训练之前就改好 `reward`。

## 优势：先改标量 reward，再铺到 token

`_normalize_rewards_by_rollout` 只对 `grpo`、`gspo`、`reinforce_plus_plus_baseline` 且 `rewards_normalization` 为真时运行（关掉用 `--disable-rewards-normalization`）。分组优先用样本上的 `group_index`；没有的话，若条数正好是 `rollout_batch_size * n_samples_per_prompt`，就按 `--n-samples-per-prompt` 切块。

同一条 rollout 的多段（多轮切出来的 sibling）必须共享一个 reward，否则直接报错。组内先减均值。再除标准差要同时满足：估计器是 `grpo` 或 `gspo`、`grpo_std_normalization` 为真（默认真，`--disable-grpo-std-normalization` 关掉，注释写明这是 Dr.GRPO）、以及组长度大于 1。标准差用 `tensor.std()`（无偏，除 $G-1$），分母是 `std + 1e-6`，且 `std > 0` 才除。`n_samples_per_prompt == 1` 时参数解析会把 `grpo_std_normalization` 强制改成假。

进 trainer 之后，`loss.py` 的 `compute_advantages_and_returns` 只在 pipeline 最后一阶跑。它先算 actor logprob 相对 ref 的 KL（`kl_coef == 0` 或没有 logprob 时 KL 张量是 0），再进 `advantages.py` 的 `compute_advantages`：

- `grpo` 和 `gspo` 走同一支 `get_grpo_returns`：`ones_like(kl[i]) * rewards[i]`。标量已经标准化过了，这里只是铺到本 rank 持有的 response token 上。GSPO 不在这里改优势。
- `ppo` 把每个 token 的 KL 乘上 `-kl_coef` 当成稠密奖励，终局 `rewards` 另传给 `get_advantages_and_returns_batch`。$\gamma$、$\lambda$ 是 `--gamma`、`--lambd`，默认都是 1。
- `reinforce_plus_plus` 在最后一个 `loss_mask` 非零的位置加上终局奖励，再从后往前做 $G_t = r_t + \gamma G_{t+1}$。
- `reinforce_plus_plus_baseline` 认为调用方已经减过组均值，优势是 `reward - kl_coef * kl_token`。

`--normalize-advantages` 为真时，`normalize_advantages` 把这些 token 优势再做一次数据并行组上的 masked whiten。默认是关的。GRPO 的除 std 和这次 whiten 是两层，不要当成同一个开关。

`--use-opd` 在任意估计器之后调用 `apply_opd_kl_to_advantages`，把蒸馏 KL 扣进优势。它不替换估计器名字。

## Clip：一个函数，GSPO 只换送进去的 KL

`losses.py` 的 `policy_loss_function` 是 policy 的唯一默认实现（`loss_type=policy_loss`）。顺序是：

1. `advantages` 先 detach。旧 logprob 默认用训练侧已经算好的 `batch["log_probs"]`；`--use-rollout-logprobs` 改用 SGLang 记下来的 `rollout_log_probs`。
2. `get_log_probs_and_entropy` 从当前 logits 取出本 rank 的 token logprob。Megatron 词表并行时走 fused cross entropy，不是手写的全词表 `log_softmax`。
3. `advantage_estimator == "gspo"` 或开了 OPSM 时，先 `all_gather_with_cp` 把 context parallel 切开的 logprob 拼回整段 response。
4. 非 GSPO：`ppo_kl = old_log_probs - log_probs`，逐 token。GSPO：`compute_gspo_kl` 对整段算 $\sum_t(\log\pi_{\mathrm{old}}-\log\pi_\theta)\cdot m_t / \sum m_t$，再 `expand_as` 到本 rank 的每个 token。后面的 clip 看到的是「一条序列一个 KL」。
5. `loss_mask` 为 0 的位置把 KL 和 advantage 清成 0。
6. `compute_policy_loss(ppo_kl, advantages, eps_clip, eps_clip_high, eps_clip_c)`。

`math_utils.compute_policy_loss` 里 $\rho=\exp(-\mathrm{ppo\_kl})$，log-ratio 先夹到有限范围再 exp（`_safe_exp_neg_ppo_kl`）。然后：

```python
pg_losses1 = -ratio * advantages
pg_losses2 = -ratio.clamp(1 - eps_clip, 1 + eps_clip_high) * advantages
clip_pg_losses1 = torch.maximum(pg_losses1, pg_losses2)
```

`--eps-clip` 默认 0.2。`--eps-clip-high` 缺省时被设成和 `eps_clip` 相同；设得更大就是 DAPO 的 clip-higher。`--eps-clip-c` 缺省是 `None`，不进 dual-clip。设了且大于 1 时，只在 `advantages < 0` 上再取 `min(clip_pg_losses1, -eps_clip_c * advantages)`，和 verl 的 `clip_ratio_c` 是同一式。

OPSM（`--use-opsm`）在 clip 之后乘一层 mask：负优势且序列 KL 大于 `--opsm-delta` 的 token 被乘 0。这是整段丢掉，不是把 $\rho$ 夹回区间。

TIS 在更后面。`--use-tis` 或 `--get-mismatch-metrics` 时，默认 `vanilla_tis_function`，比较的是训练侧 logprob 和 `rollout_log_probs`，不是 $\pi_\theta/\pi_{\mathrm{old}}$ 那一对。它可能改 response mask（rejection），于是 `get_sum_of_sample_mean` 用新 mask 做分子、用预先算好的 `rollout_mask_sums` 做分母，避免被丢掉的 token 把分母也缩小。自定义函数走 `--custom-tis-function-path`。

熵：`--entropy-coef != 0` 时 `loss = pg_loss - entropy_coef * entropy`。KL 正则：`--use-kl-loss` 时用 `compute_approx_kl`，类型 `--kl-loss-type`，可选 `k1`（默认）、`k2`、`k3`、`low_var_kl`。`--use-unbiased-kl` 再乘 $\exp(\log\pi_\theta-\log\pi_{\mathrm{old}})$。这项是加到 loss 上的，不进已经标准化过的 reward。PPO 那条把 KL 乘进 token reward 的路径，用的是 `--kl-coef`，和 `--kl-loss-coef` 不是同一个数。

## 归约：`--calculate-per-token-loss`

`get_sum_of_sample_mean` 把一维 token 损失收成标量，权重是 `loss_masks`。`--calculate-per-token-loss` 为真时按 token 加权，为假时每条样本先自己平均再相加。`loss.py` 的 `loss_function` 在这之后还要适配 Megatron 的梯度累积：

- 非 per-token：再除以 `global_batch_size`（或这一步的 `num_rollouts` / `dynamic_global_batch_size`），并乘 microbatch 数和并行度。
- per-token：不再除 batch，Megatron 路径乘 context-parallel size，用来抵消框架里多乘的那一次。

所以「每条回复等权」还是「每个 token 等权」看的是 `--calculate-per-token-loss`，不是 `--advantage-estimator`。GSPO 改的是送进 clip 的那个 KL 的粒度；归约开关仍然独立。

value loss 是另一条 `value_loss_function`：$\max((V_{\mathrm{clip}}-R)^2,(V-R)^2)$，clip 半径 `--value-clip`。只有 PPO 会训它。

## 和 verl、TRL 对一下

Miles 把组标准化放在 rollout 打包阶段，loss 里看到的 reward 已经是优势标量。verl 把同一件事留在 driver 的 `compute_grpo_outcome_advantage`。TRL 留在 `_generate_and_score_completions`。Miles 的 GSPO 不 detach 序列比、也不换 loss 函数，只把 `ppo_kl` 换成序列平均；verl 的 `compute_policy_loss_gspo` 会 detach 序列均值，让梯度从 token logprob 走。
