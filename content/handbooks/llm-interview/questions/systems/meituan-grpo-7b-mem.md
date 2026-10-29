---
id: meituan-grpo-7b-mem
section: systems
order: 140
level: A
title: 美团：7B 做 GRPO 时显存开销从哪来，怎么降？
quick: >-
  7B 做 GRPO 的显存要分开算：actor 权重、梯度、优化器和激活，reference 前向，以及每题 $n$ 条 rollout 的 KV 与
  logits。7B bf16 权重约 14GB 只是其中一项；先确定峰值在哪，再调整
  $n$、序列长度、micro-batch，或使用分片、checkpoint 和 LoRA。
tags:
  - Meituan
  - GRPO
  - Memory
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: 'https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981'
    type: candidate-first-hand
  - title: verl
    url: 'https://github.com/verl-project/verl'
    type: primary
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“7B 规模模型使用 GRPO 训练时的显存占用开销及优化方式”**

7B 做 GRPO 没有一个固定的显存数字，要把训练、reference 前向和 rollout 分开算。bf16 权重约 14GB 只是起点，全参训练还要梯度和优化器状态，生成时还会产生 KV 和 logits。

比如同一道题要生成 $n$ 条长回答，KV 峰值就可能超过模型权重。GRPO 虽然没有价值评估模型（critic），为了算 KL 仍可能保留 reference。所以我会先确认全参还是 LoRA、是否有 ref、最大长度、`rollout.n` / `--n-samples-per-prompt`，以及 rollout 和 trainer 是否同卡。

## 先拆账再优化

7B bf16 权重 $\approx 14\,\mathrm{GB}$。全参 Adam 再加两倍状态（m/v），梯度一份，轻松到 $14\times(1+1+2)$ 量级，还没算激活。FSDP/ZeRO-2 切优化器，ZeRO-3 再切参数，换来 all-gather。GRPO 的 $n$ 条 rollout：每条 KV $\propto$ layers $\times$ kv_heads $\times$ dim $\times$ seq。$n=8$、4k 长度时，sampling 侧 KV 经常大于 14GB 权重。vLLM/SGLang 的 PagedAttention 减少碎片，但 总 token 数 仍在。logits 若物化 vocab 维，峰值再加一截。packing / 动态 batch 提高有效 token，但会改变每卡样本数，需和会计账一起核对，见 `sys-verl-dynamic-bsz`、`slime-dynamic-bsz`。

ref 前向：KL 要冻住的 $\pi_{\mathrm{ref}}$。同卡就再驻一份或 offload 轮转；分卡就多一份副本。阶段性减弱 KL 能省前向，但要监控崩坏。不要说「GRPO 没 critic 所以显存只有一份 7B」。

## 根据峰值所在阶段调整

sampling 侧（通常最划算）：更短 `max_response_len`、更小 $n$、vLLM/SGLang 卸载 sampling、KV 量化只动 rollout 副本。训练仍 bf16。更新侧：ZeRO-2/3 或 FSDP、梯度累计换小 micro-batch、activation checkpoint、只训 LoRA（优化器状态从全参降到 adapter）。HybridEngine / slime `--colocate` + `--offload-train` / `--offload-rollout` 让训推互斥占显存，峰值少一份整模或少一套常驻，但一步串行。动态 batch 用 `--max-tokens-per-gpu` / `ppo_max_token_len_per_gpu` 卡住每卡 token，避免最长那条撑爆。

ZeRO-3 主要解决训练参数的分片；生成是逐 token 的 decode，需要另外看 sampling 引擎和 KV 开销。阶段实际耗时见 `meituan-grpo-stage-bottleneck`。



开口先报配置：7B 全参 vs LoRA、$n$、max len、是否 ref、是否同卡。再报峰值发生在哪一段（sampling KV vs 反向激活 vs 优化器）。优化顺序：减 $n$ 和长度 → sampling 卸载 / 量化 KV → checkpoint / ZeRO / LoRA。显存数字要和这些配置一起给出，才有可比性。slime 对账：`--n-samples-per-prompt`、`--max-tokens-per-gpu`、`--colocate`。veRL 对账：`actor_rollout_ref.rollout.n`、`ppo_micro_batch_size_per_gpu`、`use_dynamic_bsz`。

## 追问

**为什么不能只报 14GB？**
那只是 7B bf16 权重。全参 Adam 再加两倍状态，梯度一份，ref 前向，再加上 $n$ 条长 completion 的 KV 和 logits。峰值经常在 sampling 侧而不是参数。因此要先确认配置，再给显存估算。
**GRPO 没 critic 是不是很省？**
省了 value 头和一份优化器，但 `--n-samples-per-prompt` / `rollout.n` 条长 KV 往往更贵。不要说「没 critic 所以显存只有一份 7B」。KL 还常驻 ref。
**LoRA 省在哪？**
优化器状态和梯度按 adapter 计。基础模型仍要一份给前向和 sampling，KV 仍随 $n$ 和长度走。LoRA 不是把 7B GRPO 变成「一张消费卡就能跑很大 $n$」。
**同卡怎么放得下？**
veRL HybridEngine 原地 reshard，少一份整模；slime `--colocate` 靠 `--offload-train` / `--offload-rollout` 轮转，进程仍是两套。都是时分，不是边 backward 边 decode。
**动态 batch 能省显存吗？**
`--max-tokens-per-gpu` / `use_dynamic_bsz` 按 token 预算切 micro，避免最长序列定峰值。可能把 GRPO 组拆开，要和 `--balance-data` 一起谨慎。账本见 `slime-batch-accounting`。
