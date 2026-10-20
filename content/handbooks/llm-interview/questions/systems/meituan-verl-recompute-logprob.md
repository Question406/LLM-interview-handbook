---
id: meituan-verl-recompute-logprob
section: systems
order: 231
level: S
title: 美团二面：veRL 为什么要重新 forward 算 logprob，生成时记下的不够吗？
quick: >-
  不够。vLLM / SGLang 的采样 logp 和 FSDP/Megatron 训练图不是同一套算子、分块和精度，ratio /
  KL 必须用训练图上的 $\log\pi_\theta$。old logp 也常在训练后端重算一遍并 detach，避免引擎数值把
  clip 搞假。
tags:
  - Meituan
  - VeRL
  - Importance Sampling
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型研发二面-日常实习
    url: https://www.nowcoder.com/feed/main/detail/23e19d8300c54f2eb9ed9933aeaa5129
    type: candidate-first-hand
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

## 真题记录

- 公司：美团
- 岗位：大模型研发；日常实习二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“使用过 verl 框架吗”**；**“verl 框架为什么需要重新 forward 计算 log probs”**

常见误区是：答成「重算是为了省显存」或「生成时记下的 logp 已经一样」。vLLM / SGLang 为吞吐牺牲了和训练完全对齐的数值：paged attention、chunked prefill、不同 TP、bf16 累加顺序、量化，都会让 token logp 差几个千分位。差会进 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，clip 和 KL 就漂。HybridEngine 换的是权重布局；重算换的是 计算图。两件事不要并成一个开关。slime 同样：SGLang（尤其 BF16 训 + FP8 采）的 logp 不能当 $\pi_{\mathrm{old}}$，还是要 Megatron 上再 forward。同场 GRPO 哪段最慢见配套卡。重算是一次前向，通常不是实际耗时第一名，但是数学必要。

## 采样 logp 和训练图差在哪

生成引擎的目标是 tokens/s：PagedAttention、kernel fusion、FP8、TP 切法和训练 FSDP/Megatron 不同。online softmax 的实现、是否 chunked prefill、累加顺序，都会让 $\log p(a_t\mid s_t)$ 对不齐。差几个千分位看起来小，ratio 是相除，clip 区间 $[1-\epsilon,1+\epsilon]$ 会被噪声填满或永远不触发。于是出现「clip 全是 0」或「KL 对不上 ref」。根因是图，不是学习率。FlashAttention 训练侧和推理侧版本不同也会贡献偏差。所以：采样只要 token；logp 可丢或只做监控，不要计入 loss。

## 正确拆法：old / new / ref

- 采样：vLLM/SGLang 出 token，权重版本要已 `update_weights` / reshard 完成，KV 已按版本 flush。
- old：用生成时那一版 $\theta$ 在训练后端 no-grad forward 一次，当作 $\pi_{\mathrm{old}}$，detach。这才是 ratio 的分母。
- new：每个 mini-batch 再 forward $\pi_\theta$，算 $\rho=\pi_\theta/\pi_{\mathrm{old}}$。
- ref：KL 用冻结 $\pi_{\mathrm{ref}}$，同样走训练图，不要用引擎 logp 减。

不要说重算是为了省显存。省显存的是 HybridEngine 少一份整模、或 slime `--offload-train` / `--offload-rollout`。重算是为了 on-policy 数学和训练图一致。`--use-tis` 修的是采样策略与训练策略的分布隙（量化、partial、旧权），代替不了训练图 logp。把 TIS 说成「可以不重算」，是标准错答。

## 和放置、量化怎么叠

同卡 HybridEngine：换完布局引擎里的 $\theta$ 已是新的，但数值图仍是 vLLM 的，仍要重算。分卡 OpenRLHF / slime 分离：同步协议保证版本，重算保证图。量化采样时两层隙同时在：精度 + 图，TIS 和 recompute 都要。partial 采样轨迹（rollout） 的前半段还是旧权 token，mask 或 TIS 之外，新后缀的 logp 照样回训练图。面试把 HybridEngine、weight sync、recompute 画成三步：布局、版本、图。缺一都会在 $\rho$ 上无声地偏。

## 追问

- **记下生成 logp 为什么不够？** paged attention、chunked prefill、TP 切分、bf16 累加顺序、量化，都会让 token logp 差千分位。差进 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，窄 clip 区间会被噪声填满或永不触发。所以采样只要 token。
- **重算是为了省显存吗？** 不是。省显存的是 HybridEngine 少一份整模，或 slime `--offload-train` / `--offload-rollout`。重算还多一次训练图前向，目的是 on-policy 数学和训练图一致。
- **`--use-tis` 能否代替重算？** 不能。TIS 修采样分布（FP8、partial 旧 prefix、异步 stale）；重算修计算图数值。对象不同，生产上常叠加。说「开了 TIS 就可以不重算」是标准错答。
- **old 和 new 都能在引擎上算吗？** 不要。两边都用引擎，偏差可能暂时同向抵消，换引擎版本就炸。分母分子和 KL 的 ref 都回 FSDP/Megatron。
- **这段会不会变成瓶颈？** 可能，尤其 micro-batch 很小的时候，但仍通常短于长 思维链（CoT，即分步推理过程） rollout。用动态 token 帽优化，不要删。实际耗时归因见配套阶段卡。
