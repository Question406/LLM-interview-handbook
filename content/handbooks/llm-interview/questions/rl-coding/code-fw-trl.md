---
id: code-fw-trl
section: rl-coding
order: 9
level: S
title: TRL 的 GRPOTrainer 把变体都收进 loss_type，代码怎么分支？
quick: >-
  TRL 一个 `GRPOTrainer` 自己生成、自己算优势、自己 backpropagation：优势在
  `_generate_and_score_completions` 末尾就算完，`_compute_loss` 先按
  `importance_sampling_level` 造 token 级或序列级 $\rho$，再按 `loss_type` 分两次分支，一次决定怎么
  clip，一次决定除以什么。默认 `loss_type` 是 `dapo`，要对齐 DeepSeekMath 得改成 `grpo`。
tags:
  - TRL
  - GRPO
  - GSPO
  - DAPO
  - CISPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: TRL GRPO Trainer
    url: 'https://huggingface.co/docs/trl/grpo_trainer'
    type: primary
  - title: trl/trainer/grpo_trainer.py
    url: 'https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py'
    type: primary
---

TRL 把 GRPO 的各种变体都收进一个 `GRPOTrainer`：优势在生成结束时就算完，`_compute_loss` 先造 $\rho$，再按 `loss_type` 分两次叉，第一次选 clip 的写法，第二次选归约的分母。读代码时抓住这两个 `if` 就不会乱。它没有 verl 那种 driver / worker 分界，也没有 Miles 那种先把奖励分数（reward）standardization 再送进 Megatron；没有 GAE，没有 value head，PPO+价值评估模型（critic）不在这个类里。开关和公式见 `code-ppo-grpo-gspo`。

举个最容易踩的例子：照着 DeepSeekMath 写配置，什么都不改，以为跑的是原版 GRPO。可 `loss_type` 的默认值是 `dapo`，归约是全局 token 等权，和「每条回复先平均」的原版不是一回事，长短回复的权重都变了。

## 生成缓存：old logprob 为什么有时就是当前 logprob 的 detach

`training_step` 仍走 Hugging Face `Trainer`，真正换 batch 的是 `_prepare_inputs`。训练时每隔 `steps_per_generation * num_iterations` 步才调用一次 `_generate_and_score_completions`，把生成的 batch 切成 `steps_per_generation` 份放进 `_buffered_inputs`，中间的累积步只取下一片。评测不缓冲，每个 batch 现生成。

所以 `num_iterations=1` 且 `steps_per_generation <= gradient_accumulation_steps` 时，同一次生成上的策略还没被更新第二次，`old_per_token_logps` 可以不存。`_compute_loss` 里如果输入没有这份张量，就用 `per_token_logps.detach()`。开了 vLLM 则总是另算 old，因为 sampling 分布和训练前向可能不一致。

## 优势在生成结束时就算完

`_generate_and_score_completions` 的后半段按这个顺序走：

1. 多个 `reward_funcs` 的输出拼成 `rewards_per_func`，并跨进程聚合。组内 standardization 必须看见同一 prompt 的全部 $G$ 条，而这 $G$ 条可能被切到了不同 GPU 上。
2. 某个样本上所有 reward function 都返回 `None`，就记进 `unscorable_mask`。这些不会被 `nansum` 成 0，否则「没打分」会被当成奖励 0，把组均值拉偏。
3. 默认的 `multi_objective_aggregation="sum_then_normalize"` 先按 `reward_weights` 求和，在 `rewards.view(-1, num_generations)` 上 `nanmean` 得到组均值，再 `repeat_interleave` 铺回每一条。`scale_rewards` 有三档：
   - `"group"`（默认）：组内 `nanstd`。
   - `"batch"`：整个 batch 一个标准差。
   - `"none"`：不除。组内 std 仍会算，只用来打日志里的零方差比例。
   - 优势是 `rewards - mean`，需要缩放时再除 `std + 1e-4`。
4. 换成 `"normalize_then_sum"` 时，每个 reward function 先在组内做 $(r-\mathrm{mean})/(\mathrm{std}+10^{-4})$，加权求和，再对这个和做一次 batch 减均值除 std。这是 GDPO 的顺序。
5. `nan_to_num` 把 unscorable 行的优势变成 0。
6. 按 `process_index` 把优势切回本进程。本进程只训练自己那几条，但均值用的是聚合后的全组。

`num_generations` 就是 $G$，训练默认 8。

## _compute_loss：先造 ρ，再按 loss_type 分叉

输入是 promptids 和 completion ids 拼起来的序列。`logits_to_keep` 等于 completion 长度，只对回复位置取 logprob。`mask` 是 `completion_mask`，有工具返回时再乘 `tool_mask`，工具文本不进损失。

先算 `log_ratio = per_token_logps - old_per_token_logps`，然后看 `importance_sampling_level`。默认 `"token"` 时，权重就是逐 token 的 log-ratio，形状 `[B, T]`。设成 `"sequence"` 时，算 `(log_ratio * mask).sum(-1) / mask.sum(-1).clamp(min=1)` 再 `unsqueeze(-1)`，形状 `[B, 1]`，这是 GSPO 的长度平均。梯度会穿过这个均值，所以每个 token 的 $\partial s/\partial\log\pi_t$ 带一个 $1/|y|$，这点和 verl `compute_policy_loss_gspo` 里把序列均值 detach 掉不同。接着 `coef_1 = exp(log_importance_weights)`。

第一次分叉决定 clip 怎么写：

- `cispo`：`clamped_ratios = coef_1.clamp(max=epsilon_high).detach()`，`per_token_loss = -clamped_ratios * advantages * per_token_logps`。上界就是 `epsilon_high` 本身，ScaleRL 推荐 5.0，别当成 $1+0.2$。backpropagation 只走 `per_token_logps`。
- `grpo`、`bnpo`、`dr_grpo`、`dapo`、`luspo`：`coef_2 = clamp(coef_1, 1-epsilon_low, 1+epsilon_high)`。`delta` 不是 `None` 时，再把 `coef_1` 夹到 `max=delta`（INTELLECT-2 的双侧上界，文档建议大于 $1+\varepsilon$）。损失是 `-min(coef_1 * A, coef_2 * A)`。
- `sapo`：`sigmoid(τ(coef_1-1)) * 4/τ`，$A>0$ 用 `sapo_temperature_pos`（默认 1.0），否则用 `sapo_temperature_neg`（默认 1.05）。
- `vespo`：`get_gamma_weights` 给出序列级权重 $\varphi$，损失是 `-φ * A * per_token_logps`。它要求 `importance_sampling_level="token"`，和 GSPO 的 sequence 设置正好相反。

归约之前还有几个可选乘数：`off_policy_mask_threshold`（OPSM，负优势且序列漂移超过阈值就乘 0）、`top_entropy_quantile`（只留高熵 token，论文建议 0.2，默认 1.0 表示全留）、vLLM 的 `importance_sampling_ratio`（`vespo` 不加这一层）。

`beta != 0` 时 KL 用 $k_3$：$\exp(\log\pi_{\mathrm{ref}}-\log\pi_\theta)-(\log\pi_{\mathrm{ref}}-\log\pi_\theta)-1$。`use_bias_correction_kl` 默认为真，再乘 `coef_1`。KL 加进 `per_token_loss`，和 clip 用同一个 mask、同一次归约。`beta=0` 时不加载 reference。

## 归约：loss_type 的后半段

clip 已经写进 `per_token_loss`，第二个 `if` 决定除以什么：

- `grpo`、`sapo`：每条算 `((loss * mask).sum(-1) / mask.sum(-1)).mean()`，再除以当前 gradient accumulation 步数，每条回复等权。文档认为这会偏向「正优势的短回复、负优势的长回复」，所以不推荐当默认。
- `bnpo`：用本卡 micro-batch 的有效 token 之和做分母，再除累积步数。`per_device_train_batch_size==1` 时和 `grpo` 数值相同。
- `dr_grpo`：分母是 `batch_size * max_completion_length`，不随真实回复长度变，再除累积步数。
- `cispo`、`dapo`、`vespo`：分母是 `num_items_in_batch`，也就是这一整个生成 batch 的有效 token，再按进程数、累积步、`steps_per_generation` 缩放到「这一步优化器该看见的那一份」。这是全局 token 等权，`loss_type` 的默认值就是 `dapo`。
- `luspo`：`(loss * mask).sum(-1).mean()`，序列损失再乘一次长度，用来抵消 sequence-level 权重被加总 $|y|$ 次。

entropy bonus 单独算，永远是有效 token 上的平均熵，不跟着 `loss_type` 的分母走。`entropy_coef` 默认 0。开了 `use_adaptive_entropy` 会按窗口内的全局熵去加减系数，目标默认 0.2 nats；注释写明普通语言模型的熵在 2 到 10，这个默认几乎不会触发，要改成训练早期日志里的 `entropy`。MoE 的 `aux_loss` 再乘 `router_aux_loss_coef`，同样按累积步数缩放。

clip 指标只对硬 clip 那一组 loss 记录：`coef_1 < 1-epsilon_low` 且 $A<0$ 算下界，`coef_1 > 1+epsilon_high` 且 $A>0$ 算上界，CISPO 另记 `coef_1 > epsilon_high` 且 $A>0$。序列级 $\rho$ 的形状是 `[B, 1]`，`masked_seq_mean` 看到时间维为 1 就直接 squeeze，不再按 token 平均。

## 追问

**sequence 级 $\rho$ 配 `dapo` 为什么直接报错？**
初始化时，`importance_sampling_level="sequence"` 配上 `bnpo` / `dr_grpo` / `dapo` / `cispo` 都会报错。这些 loss 按 token 求和，序列比广播之后，同一条序列的权重会被加 $|y|$ 次。复现 GSPO 论文要用 `loss_type="grpo"`，`luspo` 则强制 sequence。

**评测时 `num_generations_eval` 设成 1 会怎样？**
组内 std 被写成 0，优势变成 `reward - mean` 再除 $10^{-4}$，数值会很大。这是评测分支，训练默认不会这样。

**和 Miles、verl 比，TRL 的优势在哪一步算？**
TRL 的组 standardization 和 clip 在同一个类里，优势是 `[B]` 的标量，到 `_compute_loss` 才 `unsqueeze`。Miles 在 sampling 轨迹（rollout）转换时就把组均值减掉了；verl 在 Ray driver 上按 `uid` 分组，loss 在 worker 上算。

**GSPO 在 TRL 和 verl 里梯度一样吗？**
不一样。TRL 的 GSPO 梯度穿过长度平均，verl 把那段 detach 了。

**要对齐 DeepSeekMath 的原版 GRPO，要改什么？**
把 `loss_type` 改成 `grpo`。TRL 的默认归约已经是 DAPO 的 token 等权，原版是每条回复先平均。
