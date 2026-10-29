---
id: sys-rl-grpo-loop-roles
section: systems
order: 28
level: S
title: 讲一遍 GRPO 一步：Actor、Ref、Reward、Rollout 各干什么？
quick: >-
  先让 Rollout 用当前 Actor 权重每题采 $n$ 条回答，Reward 打分，再按组内均值和标准差计算优势，Actor 据此做 clip
  更新。Ref 冻结，只提供 KL 所需的 logp；GRPO 没有 Critic，整步只有 Actor 更新权重。
tags:
  - GRPO
  - VeRL
  - LLM RL
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
  - title: veRL GRPO docs
    url: 'https://verl.readthedocs.io/en/latest/algo/grpo.html'
    type: primary
---

## 可以这样回答

GRPO 一步可以按「sampling、打分、算组内优势、计算参考 logprob、更新 Actor」来讲，只有 Actor 的权重会更新，GRPO 没有 Critic。比如数学题先用同一道题采出多条回答，Reward 判断对错，再把高于组平均的回答概率往上推。Rollout 是 Actor 的推理视图，Ref 是冻结的参考，Reward 提供分数；它们的职责和显存放置要分别说清楚。veRL 虽然把 Actor / Rollout / Ref 配在同一组 Hydra 下，也不代表它们融合成同一个模块。

其中 $\rho=\pi_\theta/\pi_{\mathrm{old}}$。我会先讲清谁产生 $\rho$、谁产生 $\hat A$、谁产生 KL，再写这一行。三个 $\pi$ 最容易混：$\pi_{\mathrm{old}}$ 是 sampling 那一版，进 ratio；$\pi_\theta$ 是正在更新的 Actor，训练图重算；$\pi_{\mathrm{ref}}$ 是冻结 SFT，只进 KL。把 ref 当成 old，clip 的对象就错了。Rollout 引擎里的 logp 既不是 $\pi_\theta$ 也不可靠当 $\pi_{\mathrm{old}}$ 的数值来源，所以要重算。Reward 发生在优势之前：没有标量分就没有组内均值，后面的 clip 也无法提供更新方向。$n\gt 1$ 是优势可定义的前提，见 `sys-rl-group-n`。

## 技术备查

GRPO 一步可以按「sampling、打分、算组内优势、计算参考 logprob、更新 Actor」来讲，只有 Actor 的权重会更新，GRPO 没有 Critic。比如数学题先用同一道题采出多条回答，Reward 判断对错，再把高于组平均的回答概率往上推。Rollout 是 Actor 的推理视图，Ref 是冻结的参考，Reward 提供分数；它们的职责和显存放置要分别说清楚。veRL 虽然把 Actor / Rollout / Ref 配在同一组 Hydra 下，也不代表它们融合成同一个模块。

## 一步按时间轴

1. **Rollout。** 推理引擎（vLLM / SGLang）加载 Actor **当前**权重，每个 prompt 采 $n$ 条 completion（veRL 里 `actor_rollout_ref.rollout.n`，$n\gt 1$，见 `sys-rl-group-n`）。这一步是 逐 token 生成（decode），常占实际耗时大头，见 `sys-rl-why-vllm-rollout`。
2. **Reward。** 规则 验证器（verifier） 或 reward model（RM） 给每条一个标量。数学 / 代码常看答案对不对、格式合不合法。RLVR 里 Reward 常常不是网络，不要默认「还有一个要训的 RM」。
3. **Advantage。** 同一输入的 $n$ 条回答得分减去组均值（再除标准差）。高于组平均的往上推，低于的往下压。不另训 value。整组全对 / 全错则 $\hat A=0$。
4. **Ref logprob。** 冻结的 reference model（通常是 RL 起点的 SFT）再 forward 一次，得到 $\log\pi_{\mathrm{ref}}$，用来加 KL，防止漂太远。Ref **不更新**。
5. **Actor update。** 用训练图重算 $\log\pi_\theta$，和 sampling 时的 $\pi_{\mathrm{old}}$ 做 ratio，clip 后按优势更新。**只有这一步改权重。** sampling logp 不能直接进 ratio，见 `meituan-verl-recompute-logprob`。

可以写成：

$$
\mathcal{L}(\theta) = \mathbb{E}\Big[\min\big(\rho\hat A,\;\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\hat A\big) - \beta\,\mathrm{KL}(\pi_\theta\Vert\pi_{\mathrm{ref}})\Big],
$$

其中 $\rho=\pi_\theta/\pi_{\mathrm{old}}$。我会先讲清谁产生 $\rho$、谁产生 $\hat A$、谁产生 KL，再写这一行。三个 $\pi$ 最容易混：$\pi_{\mathrm{old}}$ 是 sampling 那一版，进 ratio；$\pi_\theta$ 是正在更新的 Actor，训练图重算；$\pi_{\mathrm{ref}}$ 是冻结 SFT，只进 KL。把 ref 当成 old，clip 的对象就错了。Rollout 引擎里的 logp 既不是 $\pi_\theta$ 也不可靠当 $\pi_{\mathrm{old}}$ 的数值来源，所以要重算。Reward 发生在优势之前：没有标量分就没有组内均值，后面的 clip 也无法提供更新方向。$n\gt 1$ 是优势可定义的前提，见 `sys-rl-group-n`。

| 角色 | 权重动吗 | 典型实现 |
| --- | --- | --- |
| Actor | 是 | FSDP / Megatron 训练图 |
| Rollout | 否（共用 Actor 权的推理副本） | vLLM / SGLang |
| Ref | 否 | 再一次 forward，或与 Actor 同卡轮流占显存 |
| Reward | 常否 | 规则 / 外部 RM |
| Critic | GRPO 没有 | PPO 才有 |

Rollout 持有 Actor 权重的推理副本，负责生成；权重同步后还要 flush KV 并记录 version，见 `infra-rl-weight-sync`。

## 这些角色放在哪些卡上

veRL 的 `actor_rollout_ref` 配置组对应常见的同卡部署：先推理 sampling，卸 KV，再做训练更新。HybridEngine 管这些角色的放置和切换，见 `sys-verl-hybridengine`。OpenRLHF 常给 vLLM 单独一套卡；slime 默认 Megatron + SGLang，使用 `--colocate` 时让两个进程 offload 轮转，见 `slime-colocate-vs-split`。

追问「哪些要训练」时按表回答：Actor 要；Ref 冻；Reward 在 RLVR 里常常是规则；PPO 才多一个要训的 Critic。同卡方案下五段是抢显存的：KV 最大的是 Rollout，优化器状态最大的是 Actor，Ref 再 forward 一次也不便宜。所以会看到「先 sampling、卸 KV、再 ref、再 backward」的调度，而不是五个进程同时占着。分卡则 Rollout 常驻，Actor/Ref 在训练池，同步走 `update_weights`。Agent 任务再多一个环境角色：sandbox 的延迟往往超过 decode，一步实际耗时不再能用 MFU 解释，见 `sys-rl-infra`。按时间轴说明角色、是否训练和显存放置，就能解释整步的调度。Rollout 的速度来自专用推理引擎，logprob 的数值对齐则靠训练图重算，验收时也要分别检查。

计算耗时时也按角色拆：Rollout 通常最长，Ref 需要一次前向，Actor backward 较短但占优化器显存。对应到三个策略，sampling 引擎使用 $\pi_{\mathrm{old}}$ 的推理视图，训练图计算当前 $\pi_\theta$，KL 使用冻结的 $\pi_{\mathrm{ref}}$；$\rho$ 的分子分母都由训练图提供。Reward 给标量分数，不属于策略 $\pi$；GRPO 没有 Critic，也只有 Actor 会改动 $\theta$。

## 追问

**$\pi_{\mathrm{old}}$ 是谁？**
sampling 那一版 Actor，用来算 ratio。不是 Ref。Ref 只进 KL。引擎里的 logp 也不能直接当 old 的数值，所以要训练图重算。
**为什么 Ref 还要占卡？**
KL 要 $\log\pi_{\mathrm{ref}}$，大模型再 forward 一次不便宜。同卡方案会把 Ref 和 Actor 错开跑；分卡则多一份驻留。省掉 Ref 等于关掉 KL，漂远是另一类事故。
**Reward 打在 token 上还是序列上？**
GRPO 常用序列标量再广播到生成 token（配合 response mask）。过程奖要另说，不要默认逐步 价值评估模型（critic）。RLVR 里 Reward 常常是规则，不是要训的网络。
**少了重算 logp 会怎样？**
ratio 进的是引擎数值，clip 区间可能被噪声打穿，见美团那题。PagedAttention、量化、不同 TP 都会造出能进 $\rho$ 的误差。
**哪些权重在动？**
只有 Actor。Rollout 是 Actor 的推理视图，Ref 冻，GRPO 没有 Critic。把 RM 和 Critic 说成同一个东西，下一问 PPO 会穿。
**veRL 为什么配在 `actor_rollout_ref` 一组？**
它们常共享 GPU、轮流占显存：先采、卸 KV、再 ref、再 backward。这是放置，不是三个模块融合成一个算子。
**没有 Ref 能不能训 GRPO？**
能，等于关掉 KL，策略容易漂。短实验可以，长训或高学习率时 holdout 会垮。要说清你关的是正则，不是「GRPO 不需要 ref」。
**Reward 是网络时谁在更新？**
RLHF 的 RM 通常冻结当打分器；要训 RM 是另一阶段。不要把「有 RM」说成这一步有两个可训网络。Critic 仍是 PPO 才有。
**一步里谁产生 $\rho$、$\hat A$、KL？**
$\rho$ 来自训练图上的 $\pi_\theta$ 对 $\pi_{\mathrm{old}}$；$\hat A$ 来自组内奖励减均值；KL 来自冻结 ref。引擎 logp 不进这三项的可靠数值。
