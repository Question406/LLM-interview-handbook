---
id: slime-dynamic-bsz
section: systems
order: 265
level: A
title: slime 的 `--use-dynamic-batch-size` 和 veRL `use_dynamic_bsz` 怎么对？开 `--balance-data` 会拆 GRPO 组吗？
quick: >-
  都是按每卡 token 预算拼 micro-batch，不再固定条数。slime 开 `--use-dynamic-batch-size
  --max-tokens-per-gpu`；logp 路径用更大的 `--log-probs-max-tokens-per-gpu`。有 CP 时预算按
  `max_response_len // cp_size` 估。`--balance-data` 会把同一 prompt 的不同 response 分到不同
  step，GRPO 组统计可能坏。
tags:
  - slime
  - VeRL
  - Batch
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime Arguments
    url: https://thudm-slime.mintlify.app/api/arguments
    type: primary
  - title: veRL dynamic bsz 对照卡
    url: https://github.com/verl-project/verl
    type: primary
---

错法：把动态 batch 说成「把 `--micro-batch-size` 改大一点」。开关打开后条数不再是常数，拼的是每卡 token 预算；只改训练帽、忘了 logp 帽，会在重算 $\log\pi$ 时 OOM。更大的坑是 `--balance-data`：它为了匀负载，可能把同一 prompt 的 $n$ 条 response 拆进不同 training step，GRPO 组内相对优势直接坏掉。

## 按 token 拼，不按条数

官方例子：长度 $100/200/300$、预算 $300$，得到两个 micro-batch $[100,200]$ 和 $[300]$。`--micro-batch-size` 此时被忽略。目标是让每卡有效 token 贴近 `--max-tokens-per-gpu`，短序列不再被最长那条拖着 padding。

有 context parallel 时，文档按 `max_response_len // cp_size` 估预算，不要按整段 $L$ 去填，否则实际激活比你想的小、卡会空。`--balance-by-flops` 用 $cL+L^2$ 估注意力，匀得更狠，但某个 micro-batch 可能超过 `--max-tokens-per-gpu`，OOM 发生在「看起来已经均衡」之后。

## 和 veRL 字段怎么对

| | slime | veRL |
| --- | --- | --- |
| 开关 | `--use-dynamic-batch-size` | `use_dynamic_bsz` |
| 训练 token 帽 | `--max-tokens-per-gpu` | `ppo_max_token_len_per_gpu` |
| logp token 帽 | `--log-probs-max-tokens-per-gpu` | `*_log_prob_max_token_len_per_gpu` |

只开训练不开 logp 帽，重算 logp 会 OOM 或变慢，和 veRL 只改 actor 是同一坑。汇报指标从「每卡 $m$ 条」改成 tokens / step，见 `sys-verl-dynamic-bsz`、`slime-batch-accounting`。

## `--balance-data` 会拆 GRPO 组

`--balance-data` 文档写明：同一 prompt 的多条 response 可能进不同 training step。GRPO / 组相对优势要求 $n$ 条同窗统计；拆开后 $\mathrm{std}(r)$ 和 advantage 对不上。要组内相对优势，先确认组还在同一统计窗口，再开均衡。flops 均衡可以开，data 均衡对 GRPO 要谨慎。

## 追问

- **固定 micro-batch 为什么在长 CoT 会炸？** 显存随最长序列走，$m$ 条里一条 $8\mathrm{k}$ 就把整步顶满。按 token 拼可以让短的先凑满预算。
- **为什么 logp 帽往往更大？** 重算 logp 没有优化器状态，但变长 packing 后单步 token 可能比训练 backward 更尖，单独设帽。
- **`--balance-by-flops` 安全吗？** 更匀，但允许某个 batch 超过 token 帽。OOM 后先关它，不要先怪动态开关。
- **和 `--balance-data` 一起开吗？** 对 GRPO 先不要。均衡负载和组统计是两件事，组散了优势为 0 或算错。
