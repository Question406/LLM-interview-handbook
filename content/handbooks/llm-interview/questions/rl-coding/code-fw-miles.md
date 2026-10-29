---
id: code-fw-miles
section: rl-coding
order: 11
level: S
title: Miles 里 GRPO / GSPO / PPO 的代码从 train.py 走到哪？
quick: >-
  Miles 在 rollout 打包阶段就用 `_normalize_rewards_by_rollout` 把 reward 改成组内
  standardization 后的标量，trainer 里 GRPO / GSPO 只是把它铺到 token 上。Clip 只有一个
  `compute_policy_loss`，GSPO 只把送进去的 `ppo_kl` 换成序列平均；每条回复等权还是每个 token 等权，看
  `--calculate-per-token-loss`。
tags:
  - Miles
  - slime
  - GRPO
  - GSPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: radixark/miles
    url: 'https://github.com/radixark/miles'
    type: primary
  - title: Miles train.py
    url: 'https://github.com/radixark/miles/blob/main/train.py'
    type: primary
  - title: Miles policy loss
    url: >-
      https://github.com/radixark/miles/blob/main/miles/backends/training_utils/loss_hub/losses.py
    type: primary
---

## 题目描述

本卡是 Miles 框架代码导航配套的小型独立张量练习：实现非对称裁剪的逐元素 policy gradient 损失，不要求安装或运行 Miles 训练系统。框架调用位置属于后文阅读部分。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

代码片段使用已提供的同形浮点张量 ratio、advantages，以及`eps_clip`、`eps_clip_high`。ratio 是正的重要性比，advantages 可正可负；两项 epsilon 为非负标量，本题默认0.2和0.28。现有片段没有函数包装，应产出变量 `clip_pg_losses1`。

### 输出与约束

逐位置比较 -advantages*ratio 与 -advantages*clamp(ratio,1-`eps_clip`,1+`eps_clip_high`)，取较大者，返回同形损失张量；不做 mask、求均值、KL 或分布式聚合。这里的公式是所需输出定义，不涉及整个框架复刻。

### 示例

```text
ratio=[1.5,0.5], advantages=[1,-1], eps_clip=0.2, eps_clip_high=0.28
clip_pg_losses1=[-1.28,0.8]。
```

## 解题思路与参考答案

Miles 的组内 standardization 做得很早：样本在 rollout 打包进训练之前，`_normalize_rewards_by_rollout` 就把 `reward` 改成了 standardization 后的标量，actor 的 backward 里看不到这一步。到了 loss 这边，GRPO、GSPO、PPO 共用一个 `compute_policy_loss` 做 clip，GSPO 只是把送进去的 `ppo_kl` 换成了序列平均。顺着 `train.py` 走一遍，就能看出每个开关落在哪个文件。

先交代背景：Miles 的包名是 `miles`，入口仍是 `train.py` / `train_async.py`，`--advantage-estimator` 的可选值是 `grpo`、`gspo`、`ppo`、`reinforce_plus_plus`、`reinforce_plus_plus_baseline`。算法公式对照见 `code-ppo-grpo-gspo`，slime 的字段和异步时间线见 `slime-async-train`、`slime-data-buffer`。

## 一步在进程之间怎么走

`train.py` 的 `train()` 是同步环，异步环在 `train_async.py`，开头就断言 `--fully-async` 不能进 `train.py`。一步的顺序是：

1. `create_rollout_components` 拉起 SGLang 引擎和 `RolloutExecutor`。
2. `create_training_models` 建 actor。`--advantage-estimator ppo` 时，`arguments.py` 把 `use_critic` 设成真，这时才会有价值评估模型（critic）。
3. 第一次 `update_weights`，把训练权重推到 SGLang，再开始 sampling。
4. 每个 `rollout_id` 走 `inference_controller.prepare_rollout` → `rollout_executor.get`，拿到这一批轨迹。colocate 时按 `--offload-rollout` / `--offload-train` 把 KV 和权重在推理、训练之间腾挪。
5. 有 critic 就先 `critic_model.train`，把它的 value 当 `external_data` 传给 `actor_model.train`；没有 critic，actor 单独 `train`。
6. 再 `update_weights`，下一轮 sampling 用新权重。

reward 的那一步改写在 `ray/rollout/train_data_conversion.py` 的 `_post_process_rewards` 里，样本打包进训练之前就完成了。

## 优势：先处理标量奖励，再分配到 token

`_normalize_rewards_by_rollout` 只在估计器是 `grpo`、`gspo`、`reinforce_plus_plus_baseline` 且 `rewards_normalization` 为真时运行，关掉用 `--disable-rewards-normalization`。分组优先用样本上的 `group_index`；没有的话，条数正好是 `rollout_batch_size * n_samples_per_prompt` 时就按 `--n-samples-per-prompt` 切块。

同一条 sampling 轨迹（rollout）的多段（多轮切出来的 sibling）必须共享一个 reward，否则直接报错。组内先减均值。要再除标准差，得同时满足三个条件：估计器是 `grpo` 或 `gspo`；`grpo_std_normalization` 为真（默认真，`--disable-grpo-std-normalization` 关掉，注释写明这是 Dr.GRPO）；组长度大于 1。标准差用 `tensor.std()`（无偏，除 $G-1$），分母是 `std + 1e-6`，并且 `std > 0` 才除。`n_samples_per_prompt == 1` 时，参数解析会把 `grpo_std_normalization` 强制改成假。

进 trainer 以后，`loss.py` 的 `compute_advantages_and_returns` 只在 pipeline 最后一阶跑。它先算 actor logprob 相对 ref 的 KL（`kl_coef == 0` 或没有 logprob 时 KL 张量是 0），再进 `advantages.py` 的 `compute_advantages`：

- `grpo` 和 `gspo` 走同一支 `get_grpo_returns`：`ones_like(kl[i]) * rewards[i]`。标量已经 standardization 过，这里只是铺到本 rank 持有的 response token 上，GSPO 不在这里改优势。
- `ppo` 把每个 token 的 KL 乘上 `-kl_coef` 当稠密奖励，终局 `rewards` 另传给 `get_advantages_and_returns_batch`。$\gamma$、$\lambda$ 是 `--gamma`、`--lambd`，默认都是 1。
- `reinforce_plus_plus` 在最后一个 `loss_mask` 非零的位置加上终局奖励，再从后往前做 $G_t = r_t + \gamma G_{t+1}$。
- `reinforce_plus_plus_baseline` 认为调用方已经减过组均值，优势是 `reward - kl_coef * kl_token`。

`--normalize-advantages` 为真时，`normalize_advantages` 会把这些 token 优势再在数据并行组上做一次 masked whiten，默认关着。GRPO 的除 std 和这次 whiten 是两层，别当成同一个开关。`--use-opd` 在任意估计器之后调用 `apply_opd_kl_to_advantages`，把 distillation KL 扣进优势，估计器的名字不会变。

## Clip：一个函数，GSPO 只换送进去的 KL

`losses.py` 的 `policy_loss_function` 是 policy 唯一的默认实现（`loss_type=policy_loss`），顺序是：

1. `advantages` 先 detach。旧 logprob 默认用训练侧已经算好的 `batch["log_probs"]`，`--use-rollout-logprobs` 改用 SGLang 记下来的 `rollout_log_probs`。
2. `get_log_probs_and_entropy` 从当前 logits 取出本 rank 的 token logprob。Megatron vocabulary 并行时走 fused cross entropy，用不上手写的全 vocabulary `log_softmax`。
3. `advantage_estimator == "gspo"` 或开了 OPSM 时，先 `all_gather_with_cp`，把 context parallel 切开的 logprob 拼回整段 response。
4. 非 GSPO 时 `ppo_kl = old_log_probs - log_probs`，逐 token。GSPO 用 `compute_gspo_kl` 对整段算 $\sum_t(\log\pi_{\mathrm{old}}-\log\pi_\theta)\cdot m_t / \sum m_t$，再 `expand_as` 到本 rank 的每个 token，后面的 clip 看到的就是「一条序列一个 KL」。
5. `loss_mask` 为 0 的位置把 KL 和 advantage 清成 0。
6. `compute_policy_loss(ppo_kl, advantages, eps_clip, eps_clip_high, eps_clip_c)`。

`math_utils.compute_policy_loss` 里 $\rho=\exp(-\mathrm{ppo\_kl})$，log-ratio 先夹到有限范围再 exp（`_safe_exp_neg_ppo_kl`），然后：

```python
pg_losses1 = -ratio * advantages
pg_losses2 = -ratio.clamp(1 - eps_clip, 1 + eps_clip_high) * advantages
clip_pg_losses1 = torch.maximum(pg_losses1, pg_losses2)
```

`--eps-clip` 默认 0.2。`--eps-clip-high` 缺省时被设成和 `eps_clip` 一样，设得更大就是 DAPO 的 clip-higher。`--eps-clip-c` 缺省是 `None`，不进 dual-clip；设了且大于 1 时，只在 `advantages < 0` 上再取 `min(clip_pg_losses1, -eps_clip_c * advantages)`，和 verl 的 `clip_ratio_c` 是同一个式子。

OPSM（`--use-opsm`）在 clip 之后再乘一层 mask：负优势且序列 KL 大于 `--opsm-delta` 的 token 被乘 0。这是整段丢掉，$\rho$ 并没有被夹回区间。

TIS 在更后面。开了 `--use-tis` 或 `--get-mismatch-metrics` 时默认用 `vanilla_tis_function`，它比较的是训练侧 logprob 和 `rollout_log_probs`，跟 $\pi_\theta/\pi_{\mathrm{old}}$ 那一对无关。它可能会改 response mask（rejection），所以 `get_sum_of_sample_mean` 用新 mask 做分子、用预先算好的 `rollout_mask_sums` 做分母，免得被丢掉的 token 把分母也缩小。自定义函数走 `--custom-tis-function-path`。

`--entropy-coef != 0` 时，`loss = pg_loss - entropy_coef * entropy`。KL 正则在 `--use-kl-loss` 时用 `compute_approx_kl`，类型由 `--kl-loss-type` 选，可选 `k1`（默认）、`k2`、`k3`、`low_var_kl`；`--use-unbiased-kl` 再乘 $\exp(\log\pi_\theta-\log\pi_{\mathrm{old}})$。这一项加在 loss 上，不进已经 standardization 过的 reward。

## 归约：`--calculate-per-token-loss`

`get_sum_of_sample_mean` 把一维 token 损失收成标量，权重是 `loss_masks`。`--calculate-per-token-loss` 为真时按 token 加权，为假时每条样本先自己平均再相加。`loss.py` 的 `loss_function` 之后还要适配 Megatron 的 gradient accumulation：

- 非 per-token：再除以 `global_batch_size`（或这一步的 `num_rollouts` / `dynamic_global_batch_size`），并乘 microbatch 数和并行度。
- per-token：不再除 batch，Megatron 路径乘 context-parallel size，抵消框架里多乘的那一次。

所以「每条回复等权」还是「每个 token 等权」，看的是 `--calculate-per-token-loss`，跟 `--advantage-estimator` 无关。GSPO 改的是送进 clip 的那个 KL 的粒度，归约开关仍然独立。

## 追问

**PPO 的 value loss 在哪？**
在另一条 `value_loss_function`：$\max((V_{\mathrm{clip}}-R)^2,(V-R)^2)$，clip 半径是 `--value-clip`，只有 PPO 会训它。

**`--kl-coef` 和 `--kl-loss-coef` 是一回事吗？**
不是同一个数。PPO 那条把 KL 乘进 token reward 的路径用 `--kl-coef`，`--use-kl-loss` 那一项用 `--kl-loss-coef`。

**和 verl、TRL 比，组 standardization 放在哪一步？**
Miles 放在 rollout 打包阶段，loss 里看到的 reward 已经是优势标量。verl 把同一件事留在 driver 的 `compute_grpo_outcome_advantage`，TRL 留在 `_generate_and_score_completions`。

**Miles 和 verl 的 GSPO 梯度一样吗？**
不一样。Miles 不 detach 序列比，也不换 loss 函数，只把 `ppo_kl` 换成序列平均；verl 的 `compute_policy_loss_gspo` 会 detach 序列均值，让梯度从 token logprob 走。

## 简单测试怎么写

下面代码是可以直接执行的小测试，保存为 solution.py，运行 python3 solution.py；通过后输出 simple tests passed。数值代码需要 PyTorch。

先给片段里的 ratio、advantages 和上下界赋小值，再原样执行公式。正优势的 ratio=1.5 被上界 1.28 截断；负优势的 ratio=0.5 按下界 0.8 计算，loss 分别为 -1.28 和 0.8。

```python
import torch

ratio = torch.tensor([1.5, 0.5])
advantages = torch.tensor([1.0, -1.0])
eps_clip, eps_clip_high = 0.2, 0.28
pg_losses1 = -ratio * advantages
pg_losses2 = -ratio.clamp(1 - eps_clip, 1 + eps_clip_high) * advantages
clip_pg_losses1 = torch.maximum(pg_losses1, pg_losses2)
torch.testing.assert_close(clip_pg_losses1, torch.tensor([-1.28, 0.8]))
print("simple tests passed")
```
