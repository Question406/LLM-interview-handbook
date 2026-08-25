---
id: slime-advantage-estimator
section: systems
order: 256
level: A
title: slime 里 GRPO / GSPO / CISPO / PPO 怎么切？和 veRL 的 config 怎么对？
quick: >-
  `--advantage-estimator` 选 `grpo` / `gspo` / `cispo` / `reinforce_plus_plus` /
  `reinforce_plus_plus_baseline` / `ppo`。OPD 正交，叠加 `--use-opd`。默认 per-sample
  loss，对齐百度题要开 `--calculate-per-token-loss`。和 veRL 的 `algorithm.adv_estimator`
  是同一层开关，只是 slime 用 CLI 而不是 Hydra YAML。
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

这块容易背论文摘要，却说不出 slime 里动过的开关。`--advantage-estimator` 和 veRL 的 `algorithm.adv_estimator` 是同一层：换的是优势怎么估、clip 对象是谁，不是换一套 rollout 栈。OPD 正交，叠加 `--use-opd`，不要说「OPD 是一种 advantage」。默认 per-sample loss，对齐百度「序列 loss 怎么落到 token」要开 `--calculate-per-token-loss`。面试我先报当时用的估计器和聚合方式，再讲长尾样本会被哪种平均淹没。组大小走 `--n-samples-per-prompt`，对 veRL `actor_rollout_ref.rollout.n`。

## 估计器怎么切

- **GRPO**：`--n-samples-per-prompt` 做组内相对 advantage，无 critic。$n=1$ 时相对优势没有定义，见 `sys-rl-group-n`。同一套 SGLang rollout，只换 estimator。
- **GSPO / CISPO**：同一套 rollout，换 clip 对象。GSPO 用序列 likelihood ratio，减轻超长回复把 token-level $\rho$ 拉爆。CISPO 把 IS 权重截断后 detach，梯度仍走 $\log\pi$（见 `pt-cispo`）。追问「为啥换」答长度偏差和「越界 token 还要不要梯度」，不要只报名字。
- **PPO**：同一组 train GPU 上 actor / critic 轮流 offload，并行拓扑必须一致；角色差异走 `--megatron-config-path`，没有单独 `critic_num_gpus`。别按 OpenRLHF 的 critic 独立卡去套 slime。
- **REINFORCE++ / baseline**：`--advantage-estimator reinforce_plus_plus` 或 `reinforce_plus_plus_baseline`，仍无 critic，baseline 形式不同，组统计约束比 GRPO 弱。

OPD：`--use-opd --opd-kl-coef`，和 estimator 正交。TIS：`--use-tis`，修 SGLang 采样策略和训练图不一致（量化、partial rollout、旧权），也正交。不要把 TIS / OPD / estimator 拧成一个枚举。

## 损失聚合和 veRL 对表

默认 `mean(sum_i / \mathrm{len}_i)`（per sample）。长样本的每个 token 权重被长度摊薄；短样本更响。`--calculate-per-token-loss` 变成全局 token 平均，长尾 CoT 会主导梯度。和 veRL `loss_agg_mode`、百度题是同一题。先说你当时用的是哪一种，再讲哪种会淹没哪类样本。一步样本数仍走 `--rollout-batch-size` × `--n-samples-per-prompt` 对 `--global-batch-size`，见 `slime-batch-accounting`。换 estimator 不自动改账本；GSPO 仍要组在一起，`--balance-data` 拆组同样危险。

## 放置不要跟着算法改

GRPO/GSPO/CISPO 都是无 critic 的组算法，放置仍是 Megatron + SGLang，`--colocate` 或分卡。切到 PPO 才多一个 value 角色，但卡还是同一组 train GPU 轮流 offload，不是突然加一套 critic 池。Serving 侧 generate 函数、router、`--partial-rollout` 保持不变。算法开关在 estimator 和 loss 聚合；Infra 开关在放置和引擎。面试把两层分开，才不会把「我们上了 GSPO」说成换了框架。

我会按「同一套 rollout，换估计器」来讲。SGLang + Buffer + Megatron 不动，动的是 `--advantage-estimator`。GRPO 用组内均值当 baseline，必须 `--n-samples-per-prompt` $\gt 1$。GSPO 把 clip 放到序列 likelihood ratio，缓解超长 CoT 把 token 级 $\rho$ 拉爆。CISPO 截断 IS 权重后 detach，梯度仍走 $\log\pi$，回答「越界 token 还要不要梯度」。PPO 才引入 critic，但 slime 没有独立 `critic_num_gpus`，同一组 train GPU 轮流 offload，角色差在 `--megatron-config-path`。OPD 与 TIS 都是叠加开关：`--use-opd --opd-kl-coef` 不是一种 advantage；`--use-tis` 修量化 / partial / 旧权的采样隙。损失默认 per-sample 平均，长样本被摊薄；`--calculate-per-token-loss` 改全局 token 平均，长尾会主导，和 veRL `loss_agg_mode` 对表。换估计器不改 `--global-batch-size` 账本，也不自动允许 `--balance-data` 拆组。先报用过的估计器和聚合方式，再讲为什么换，比背论文公式稳。veRL 侧同一层是 `algorithm.adv_estimator` 和 `actor_rollout_ref.rollout.n`，只是 Hydra 而不是 CLI。

## 先报开关再讲论文

面试顺序：估计器名字 → `--n-samples-per-prompt` → 损失是 per-sample 还是 `--calculate-per-token-loss` → OPD/TIS 有没有叠。GSPO/CISPO 讲长度偏差和越界梯度，不要只报字母。PPO 讲同一组 GPU 轮流 offload。换估计器不改账本、不改 colocate。和 veRL 对 Hydra 字段。长尾会被哪种平均淹没要主动说。

## 追问

- **和 veRL 怎么对？** slime `--advantage-estimator` ↔ `algorithm.adv_estimator`；`--n-samples-per-prompt` ↔ `actor_rollout_ref.rollout.n`；`--calculate-per-token-loss` ↔ `loss_agg_mode`。一个 CLI，一个 Hydra。对表时当场问 mini-batch 含不含 $n$。
- **OPD 是 advantage 吗？** 不是。`--use-opd --opd-kl-coef` 叠在估计器上，管外部教师 KL。不要写进 estimator 枚举，也不要说「我们用 OPD 代替 GRPO」。OPSD / Self-OPD 是同权重特权教师，更不是这个开关，见 `pt-opsd`。
- **为什么 GSPO 换序列 ratio？** token-level $\rho$ 在长序列上方差大，容易整段被 clip 吃掉。序列 likelihood ratio 减轻长度偏差。CISPO 则把 IS 截断后 detach，梯度仍走 $\log\pi$，回答越界 token 还要不要学。
- **PPO 要单独 critic GPU 吗？** slime 没有 `critic_num_gpus`。同一组 train GPU 轮流 offload，并行拓扑必须一致，角色差异走 `--megatron-config-path`。按 OpenRLHF 独立 critic 池去套会配错。
- **TIS 和换 estimator 的关系？** 正交。量化、partial、异步造成的分布隙用 `--use-tis`；优势定义用 `--advantage-estimator`。换 GSPO 不能代替训练图重算 logp，也不能代替 TIS。TIS 和 CISPO 也不是同一个 clip，见 `pt-tis-async`。
