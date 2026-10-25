---
id: slime-advantage-estimator
section: systems
order: 256
level: A
title: slime 里 GRPO / GSPO / CISPO / PPO 怎么切？和 veRL 的 config 怎么对？
quick: "slime 用 `--advantage-estimator` 选择优势估计器，对应 veRL 的 `algorithm.adv_estimator`；采样系统可以保持不变。还要独立说明 loss 怎样聚合：OPD 的 `--use-opd`、TIS 和 per-token loss 分别解决其他问题，不能混成同一个算法开关。"
tags:
  - slime
  - GRPO
  - GSPO
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

在 slime 里切 GRPO / GSPO / CISPO / PPO，先看 `--advantage-estimator`，它对应 veRL 的 `algorithm.adv_estimator`。改变的是优势估计和 clip 对象，SGLang 采样系统可以继续使用原来那套。

比如长短回答混在一批里，除了换估计器，还要看损失怎样按长度平均。默认 per-sample loss 会摊薄长回答里每个 token 的权重，`--calculate-per-token-loss` 则按全局 token 平均。OPD 另用 `--use-opd` 叠加，组大小由 `--n-samples-per-prompt` 控制，对应 veRL 的 `actor_rollout_ref.rollout.n`。

## 估计器怎么切

- GRPO：`--n-samples-per-prompt` 做组内相对 advantage，不需要价值评估模型（critic）。$n=1$ 时相对优势没有定义，见 `sys-rl-group-n`。同一套 SGLang rollout，只换 estimator。
- GSPO / CISPO：同一套 rollout，换 clip 对象。GSPO 用序列 likelihood ratio，减轻超长回复把 token-level $\rho$ 拉爆。CISPO 把 IS 权重截断后 detach，梯度仍走 $\log\pi$（见 `pt-cispo`）。选择时要解释它如何处理长度偏差，以及越界 token 是否继续提供梯度。
- PPO：同一组 train GPU 上 actor / critic 轮流 offload，并行拓扑必须一致；角色差异走 `--megatron-config-path`，没有单独 `critic_num_gpus`。别按 OpenRLHF 的 critic 独立卡去套 slime。
- REINFORCE++ / baseline：`--advantage-estimator reinforce_plus_plus` 或 `reinforce_plus_plus_baseline`，仍无 critic，baseline 形式不同，组统计约束比 GRPO 弱。

OPD：`--use-opd --opd-kl-coef`，和 estimator 正交。TIS：`--use-tis`，修 SGLang 采样策略和训练图不一致（量化、partial rollout、旧权），也正交。不要把 TIS、OPD 和优势估计器当成同一组选项。

## 损失聚合和 veRL 对表

默认 `mean(sum_i / \mathrm{len}_i)`（per sample）。长样本的每个 token 的权重被长度摊薄；短样本的每个 token 权重更大。`--calculate-per-token-loss` 变成全局 token 平均，少数很长的 CoT 会主导梯度。和 veRL `loss_agg_mode`、百度题是同一题。先说你当时用的是哪一种，再讲哪种会淹没哪类样本。一步样本数仍走 `--rollout-batch-size` × `--n-samples-per-prompt` 对 `--global-batch-size`，见 `slime-batch-accounting`。换 estimator 不自动改账本；GSPO 仍要组在一起，`--balance-data` 拆组同样危险。



GRPO/GSPO/CISPO 都是无 critic 的组算法，放置仍是 Megatron + SGLang，`--colocate` 或分卡。切到 PPO 才多一个 value 角色，但卡还是同一组 train GPU 轮流 offload，不是突然加一套 critic 池。Serving 侧 generate 函数、router、`--partial-rollout` 保持不变。算法开关在 estimator 和 loss 聚合；Infra 开关在放置和引擎。回答时分清算法和 Infra 两层，就能说明换 GSPO 后哪些部分实际发生了变化。

## 追问

**和 veRL 怎么对？**
slime `--advantage-estimator` ↔ `algorithm.adv_estimator`；`--n-samples-per-prompt` ↔ `actor_rollout_ref.rollout.n`；`--calculate-per-token-loss` ↔ `loss_agg_mode`。一个 CLI，一个 Hydra。对表时当场问 mini-batch 含不含 $n$。
**OPD 是 advantage 吗？**
不是。`--use-opd --opd-kl-coef` 叠在估计器上，管外部教师 KL。不要写进 estimator 枚举，也不要说「我们用 OPD 代替 GRPO」。OPSD / Self-OPD 是同权重特权教师，更不是这个开关，见 `pt-opsd`。
**为什么 GSPO 换序列 ratio？**
token-level $\rho$ 在长序列上方差大，容易整段被 clip 吃掉。序列 likelihood ratio 减轻长度偏差。CISPO 则把 IS 截断后 detach，梯度仍走 $\log\pi$，回答越界 token 还要不要学。
**PPO 要单独 critic GPU 吗？**
slime 没有 `critic_num_gpus`。同一组 train GPU 轮流 offload，并行拓扑必须一致，角色差异走 `--megatron-config-path`。按 OpenRLHF 独立 critic 池去套会配错。
**TIS 和换 estimator 的关系？**
正交。量化、partial、异步造成的分布隙用 `--use-tis`；优势定义用 `--advantage-estimator`。换 GSPO 不能代替训练图重算 logp，也不能代替 TIS。TIS 和 CISPO 也不是同一个 clip，见 `pt-tis-async`。
