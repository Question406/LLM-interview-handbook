---
id: code-fw-trl
section: rl-coding
order: 9
level: S
title: TRL 的 GRPOTrainer 把变体都收进 loss_type，代码怎么分支？
quick: "优势在 `_generate_and_score_completions` 里算完；`_compute_loss` 先选 token 级或序列级 $\\rho$，再按 `loss_type` 分支 clip 和归约。默认是 `dapo`，不是 `grpo`。"
tags:
  - TRL
  - GRPO
  - GSPO
  - DAPO
  - CISPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: TRL GRPO Trainer
    url: https://huggingface.co/docs/trl/grpo_trainer
    type: primary
  - title: trl/trainer/grpo_trainer.py
    url: https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
    type: primary
---

开关和公式见 `code-ppo-grpo-gspo`。TRL 没有 verl 那种 driver / worker 分界，也没有 Miles 那种先把 奖励分数（reward） 标准化再送进 Megatron。一条 `GRPOTrainer` 自己生成、自己算优势、自己反传。没有 GAE、没有 value head。PPO+价值评估模型（critic） 不在这个类里。

## 生成缓存：为什么 old logprob 有时就是当前 logprob 的 detach

`training_step` 仍走 Hugging Face `Trainer`。真正换 batch 的是 `_prepare_inputs`。训练时每隔 `steps_per_generation * num_iterations` 步才调用一次 `_generate_and_score_completions`，把生成 batch 切成 `steps_per_generation` 份放进 `_buffered_inputs`，中间的累积步只取下一片。评测不缓冲，每个 batch 现生成。

因此 `num_iterations=1` 且 `steps_per_generation <= gradient_accumulation_steps` 时，同一次生成上的策略还没被更新第二次，`old_per_token_logps` 可以不存。`_compute_loss` 里如果输入没有这份张量，就用 `per_token_logps.detach()`。开了 vLLM 则总是另算 old，因为采样分布和训练前向可能不一致。

## 优势在生成结束时就算完

`_generate_and_score_completions` 后半：

1. 多个 `reward_funcs` 的输出拼成 `rewards_per_func`，并且跨进程聚合。组内标准化必须看见同一输入提示 的全部 $G$ 条，而 $G$ 可能被切到不同 GPU。
2. 某个样本上所有奖励函数都返回 `None`，记进 `unscorable_mask`。不把它们 `nansum` 成 0，否则会把「没打分」当成奖励 0，拉偏组均值。
3. `multi_objective_aggregation="sum_then_normalize"`（默认）：先按 `reward_weights` 求和。`rewards.view(-1, num_generations)` 上 `nanmean` 得到组均值，再 `repeat_interleave` 铺回每一条。`scale_rewards`：
   - `"group"`（默认）：组内 `nanstd`。
   - `"batch"`：整个 batch 一个标准差。
   - `"none"`：不除。组内 std 仍会算，只用于打日志里的零方差比例。
   - 优势是 `rewards - mean`，需要缩放时再除 `std + 1e-4`。
4. `"normalize_then_sum"`：每个奖励函数先在组内做 $(r-\mathrm{mean})/(\mathrm{std}+10^{-4})$，加权求和，再对这个和做一次 batch 减均值除 std。这是 GDPO 的顺序。
5. `nan_to_num` 把 unscorable 行的优势变成 0。
6. 按 `process_index` 把优势切回本进程。本进程只训练自己那几条，但均值用的是聚合后的全组。

`num_generations` 就是 $G$。训练默认 8。评测可以用 `num_generations_eval`，设成 1 时组内 std 被写成 0，优势变成 `reward - mean` 再除 $10^{-4}$，数值会很大。这是评测分支，不是训练默认。

## _compute_loss：先造 ρ，再按 loss_type 分叉

输入是 输入提示（prompt） ids 和 completion ids 拼起来的序列。`logits_to_keep` 等于 completion 长度，只对回复位置取 logprob。`mask` 是 `completion_mask`；有工具返回时再乘 `tool_mask`，工具文本不进损失。

`log_ratio = per_token_logps - old_per_token_logps`。

- `importance_sampling_level="token"`（默认）：权重就是逐 token 的 log-ratio，形状 `[B, T]`。
- `"sequence"`：`(log_ratio * mask).sum(-1) / mask.sum(-1).clamp(min=1)`，再 `unsqueeze(-1)`，形状 `[B, 1]`。这是 GSPO 的长度平均。梯度穿过这个均值，所以每个 token 的 $\partial s/\partial\log\pi_t$ 带 $1/|y|$。和 verl `compute_policy_loss_gspo` 里把序列均值 detach 掉不同。

`coef_1 = exp(log_importance_weights)`。

然后：

- `cispo`：`clamped_ratios = coef_1.clamp(max=epsilon_high).detach()`，`per_token_loss = -clamped_ratios * advantages * per_token_logps`。上界是 `epsilon_high` 本身。ScaleRL 推荐 5.0，不是 $1+0.2$。反传只走 `per_token_logps`。
- `grpo`、`bnpo`、`dr_grpo`、`dapo`、`luspo`：`coef_2 = clamp(coef_1, 1-epsilon_low, 1+epsilon_high)`。`delta` 不是 `None` 时再把 `coef_1` 夹到 `max=delta`（INTELLECT-2 的双侧上界，文档建议大于 $1+\varepsilon$）。损失是 `-min(coef_1 * A, coef_2 * A)`。
- `sapo`：`sigmoid(τ(coef_1-1)) * 4/τ`，$A>0$ 用 `sapo_temperature_pos`（默认 1.0），否则 `sapo_temperature_neg`（默认 1.05）。
- `vespo`：`get_gamma_weights` 给序列级权重 $\varphi$，损失是 `-φ * A * per_token_logps`。要求 `importance_sampling_level="token"`，和 GSPO 的 sequence 设置相反。

初始化时如果 `importance_sampling_level="sequence"` 却配了 `bnpo` / `dr_grpo` / `dapo` / `cispo`，会直接报错：这些 loss 按 token 求和，序列比广播之后会把同一条序列的权重加 $|y|$ 次。复现 GSPO 论文要 `loss_type="grpo"`。`luspo` 则强制 sequence。

可选乘数，都发生在归约之前：`off_policy_mask_threshold`（OPSM，负优势且序列漂移超过阈值则乘 0）、`top_entropy_quantile`（只留高熵 token，论文建议 0.2，默认 1.0 表示全留）、vLLM 的 `importance_sampling_ratio`（`vespo` 不加这一层）。

`beta != 0` 时 KL 是 $k_3$：$\exp(\log\pi_{\mathrm{ref}}-\log\pi_\theta)-(\log\pi_{\mathrm{ref}}-\log\pi_\theta)-1$。`use_bias_correction_kl` 默认真，再乘 `coef_1`。KL 加进 `per_token_loss`，和 clip 用同一个 mask、同一次归约。`beta=0` 时不加载 reference。

## 归约：loss_type 的后半段

clip 已经写进 `per_token_loss`。除以什么是第二个 `if`：

- `grpo`、`sapo`：每条 `((loss * mask).sum(-1) / mask.sum(-1)).mean()`，再除以当前梯度累积步数。每条回复等权。文档认为这会偏向「正优势的短回复、负优势的长回复」，所以不推荐当默认。
- `bnpo`：本卡 micro-batch 的有效 token 之和做分母，再除累积步数。`per_device_train_batch_size==1` 时和 `grpo` 数值相同。
- `dr_grpo`：分母是 `batch_size * max_completion_length`，不随真实回复长度变。再除累积步数。
- `cispo`、`dapo`、`vespo`：分母是 `num_items_in_batch`，也就是这一整个生成 batch 的有效 token，再按进程数、累积步、`steps_per_generation` 缩放到「这一步优化器该看见的那一份」。这是全局 token 等权。`loss_type` 的默认值就是 `dapo`。
- `luspo`：`(loss * mask).sum(-1).mean()`，序列损失再乘过长度，用来抵消 sequence-level 权重被加总 $|y|$ 次。

熵奖励另算，永远是有效 token 上的平均熵，不跟着 `loss_type` 的分母走。`entropy_coef` 默认 0。`use_adaptive_entropy` 时按窗口内的全局熵去加减系数，目标默认 0.2 nats，注释写明普通语言模型的熵在 2 到 10，这个默认几乎不会触发，要改成训练早期日志里的 `entropy`。

MoE 的 `aux_loss` 再乘 `router_aux_loss_coef`，同样按累积步数缩放。

clip 指标只对硬 clip 那一组 loss 记录：`coef_1 < 1-epsilon_low` 且 $A<0$ 算下界，`coef_1 > 1+epsilon_high` 且 $A>0$ 算上界。CISPO 另记 `coef_1 > epsilon_high` 且 $A>0$。序列级 $\rho$ 的形状是 `[B, 1]`，`masked_seq_mean` 看到时间维为 1 就直接 squeeze，不再按 token 平均。

## 和另外两个框架

TRL 的组标准化和 clip 在同一个类里，优势是 `[B]` 的标量，到 `_compute_loss` 才 `unsqueeze`。Miles 在 采样轨迹（rollout） 转换时就把组均值减掉。verl 在 Ray driver 上按 `uid` 分组，loss 在 worker。TRL 的 GSPO 梯度穿过长度平均；verl 把那段 detach。TRL 的默认归约已经是 DAPO 的 token 等权，要对齐 DeepSeekMath 的「每条回复先平均」必须把 `loss_type` 改成 `grpo`。
