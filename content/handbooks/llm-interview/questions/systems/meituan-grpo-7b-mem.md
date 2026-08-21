---
id: meituan-grpo-7b-mem
section: systems
order: 140
level: A
title: 美团：7B 做 GRPO 时显存开销从哪来，怎么降？
quick: >-
  显存主要在 actor 权重 / 梯度 / 优化器、reference 前向、以及 $n$ 条 rollout 的 KV 与 logits。先减
  $n$、序列长和 micro-batch，再用 ZeRO、梯度检查点、LoRA 和 vLLM 卸载采样，而不是只报一个「大概 40G」。
tags:
  - Meituan
  - GRPO
  - Memory
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“7B规模模型使用GRPO训练时的显存占用开销及优化方式”**

陷阱是报一个脱离配置的「大概 40G」。7B bf16 权重大约 14GB 只是起点；面试要拆账：参数、梯度、优化器、reference、rollout KV、logits / 激活。GRPO 虽无 critic，仍常驻 ref 做 KL，且同 prompt 生成 $n$ 条长 completion——KV 峰值往往压过参数本身。先问清：全参还是 LoRA、是否挂 ref、最大长度、`rollout.n` / `--n-samples-per-prompt`、rollout 是否与 trainer 同卡。同场阶段瓶颈卡讲墙钟，本题讲显存。

## 先拆账再优化

7B bf16 权重 $\approx 14\,\mathrm{GB}$。全参 Adam 再加两倍状态（m/v），梯度一份，轻松到 $14\times(1+1+2)$ 量级，还没算激活。FSDP/ZeRO-2 切优化器，ZeRO-3 再切参数，换来 all-gather。GRPO 的 $n$ 条 rollout：每条 KV $\propto$ layers $\times$ kv_heads $\times$ dim $\times$ seq。$n=8$、4k 长度时，采样侧 KV 经常大于 14GB 权重。vLLM/SGLang 的 PagedAttention 减少碎片，但 **总 token 数** 仍在。logits 若物化 vocab 维，峰值再加一截。packing / 动态 batch 提高有效 token，但会改变每卡样本数，需和会计账一起核对，见 `sys-verl-dynamic-bsz`、`slime-dynamic-bsz`。

ref 前向：KL 要冻住的 $\pi_{\mathrm{ref}}$。同卡就再驻一份或 offload 轮转；分卡就多一份副本。阶段性减弱 KL 能省前向，但要监控崩坏。不要说「GRPO 没 critic 所以显存只有一份 7B」。

## 按收益关旋钮

采样侧（通常最划算）：更短 `max_response_len`、更小 $n$、vLLM/SGLang 卸载采样、KV 量化只动 rollout 副本。训练仍 bf16。更新侧：ZeRO-2/3 或 FSDP、梯度累计换小 micro-batch、activation checkpoint、只训 LoRA（优化器状态从全参降到 adapter）。HybridEngine / slime `--colocate` + `--offload-train` / `--offload-rollout` 让训推互斥占显存，峰值少一份整模或少一套常驻，但一步串行。动态 batch 用 `--max-tokens-per-gpu` / `ppo_max_token_len_per_gpu` 卡住每卡 token，避免最长那条撑爆。

不要先上 ZeRO-3 幻想加速生成——生成是 decode，和参数分片不是同一瓶颈。阶段墙钟见 `meituan-grpo-stage-bottleneck`。

## 面试怎么报数字

开口先报配置：7B 全参 vs LoRA、$n$、max len、是否 ref、是否同卡。再报峰值发生在哪一段（采样 KV vs 反向激活 vs 优化器）。优化顺序：减 $n$ 和长度 → 采样卸载 / 量化 KV → checkpoint / ZeRO / LoRA。给固定 GB 而不问配置，会被追问拆穿。slime 对账：`--n-samples-per-prompt`、`--max-tokens-per-gpu`、`--colocate`。veRL 对账：`actor_rollout_ref.rollout.n`、`ppo_micro_batch_size_per_gpu`、`use_dynamic_bsz`。

开口不要给固定 GB。先写五项：权重、梯度、Adam、ref、rollout KV。7B 全参 bf16 权重约 14GB，Adam 再乘二，KV 随 $n\times L$ 走，峰值常常在采样而不在参数。LoRA 只缩小优化器那一项，底模和 KV 还在。同卡 HybridEngine 省的是第二份整模，不是 KV；slime `--colocate` 靠 `--offload-train` / `--offload-rollout` 互斥，切换有 PCIe 税。优化按收益：先减 `--n-samples-per-prompt` / `rollout.n` 和 `max_response_len`，再把采样卸载到 vLLM/SGLang 并考虑 KV 量化，然后才是 activation checkpoint、ZeRO、LoRA。反向优化（先 ZeRO-3 再减 $n$）会把通信税加在已经 generation-bound 的一步上。动态 batch 用 `--max-tokens-per-gpu` 卡住每卡 token，但可能拆 GRPO 组，要和 `--balance-data` 一起说。面试被追问「你当时多少 G」时，把配置和峰值发生在哪一段一起报，才像跑过。

## 怎么报峰值

不要给脱离配置的 GB。先报全参还是 LoRA、是否挂 ref、$n$、最大长度、是否同卡，再报峰值发生在采样 KV、反向激活还是优化器。7B 权重约 14GB 只是起点。减 $n$ 和长度通常比先开 ZeRO-3 更划算。动态 batch 卡住每卡 token，但可能拆组。同卡省的是第二份整模或靠 offload 互斥，KV 仍在。

## 追问

- **为什么不能只报 14GB？** 那只是 7B bf16 权重。全参 Adam 再加两倍状态，梯度一份，ref 前向，再加上 $n$ 条长 completion 的 KV 和 logits。峰值经常在采样侧而不是参数。不问配置就报「大概 40G」会被拆穿。
- **GRPO 没 critic 是不是很省？** 省了 value 头和一份优化器，但 `--n-samples-per-prompt` / `rollout.n` 条长 KV 往往更贵。不要说「没 critic 所以显存只有一份 7B」。KL 还常驻 ref。
- **LoRA 省在哪？** 优化器状态和梯度按 adapter 计。底模仍要一份给前向和采样，KV 仍随 $n$ 和长度走。LoRA 不是把 7B GRPO 变成「一张消费卡就能跑很大 $n$」。
- **同卡怎么放得下？** veRL HybridEngine 原地 reshard，少一份整模；slime `--colocate` 靠 `--offload-train` / `--offload-rollout` 轮转，进程仍是两套。都是时分，不是边 backward 边 decode。
- **动态 batch 能省显存吗？** `--max-tokens-per-gpu` / `use_dynamic_bsz` 按 token 预算切 micro，避免最长序列定峰值。可能把 GRPO 组拆开，要和 `--balance-data` 一起谨慎。账本见 `slime-batch-accounting`。
