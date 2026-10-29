---
id: slime-dynamic-bsz
section: systems
order: 265
level: A
title: slime 的 `--use-dynamic-batch-size` 和 veRL `use_dynamic_bsz` 怎么对？开 `--balance-data` 会拆 GRPO 组吗？
quick: "两者都用每卡 token 预算拼 micro-batch，训练和 logp 重算要分别设上限。GRPO 开 `--balance-data` 前还要检查组的统计窗口，因为同一 prompt 的 response 可能被拆进不同 training step。"
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

slime 和 veRL 的动态 batch 都按每卡 token 预算拼 micro-batch，训练和 logp 重算分别设上限，重算 $\log\pi$ 也有自己的显存需求。GRPO 还要额外检查组有没有被拆开：`--balance-data` 可能把同一 prompt 的 $n$ 条 response 分到不同 training step，导致组内优势统计出错。

比如官方例子里，三条序列长度是 $100/200/300$，预算是 $300$，就会拼成 $[100,200]$ 和 $[300]$ 两个 micro-batch。这时 `--micro-batch-size` 被忽略，每卡有效 token 尽量贴近 `--max-tokens-per-gpu`，短序列也就少为最长序列做 padding。

有 context parallel 时，文档按 `max_response_len // cp_size` 估预算，不要按整段 $L$ 去填，否则实际激活比你想的小、卡会空。`--balance-by-flops` 用 $cL+L^2$ 估 attention，匀得更狠，但某个 micro-batch 可能超过 `--max-tokens-per-gpu`，OOM 发生在「看起来已经均衡」之后。

| | slime | veRL |
| --- | --- | --- |
| 开关 | `--use-dynamic-batch-size` | `use_dynamic_bsz` |
| 训练 token 帽 | `--max-tokens-per-gpu` | `ppo_max_token_len_per_gpu` |
| logp token 帽 | `--log-probs-max-tokens-per-gpu` | `*_log_prob_max_token_len_per_gpu` |

只开训练不开 logp 帽，重算 logp 会 OOM 或变慢，和 veRL 只改 actor 是同一坑。汇报指标从「每卡 $m$ 条」改成 tokens / step，见 `sys-verl-dynamic-bsz`、`slime-batch-accounting`。

`--balance-data` 文档写明：同一 prompt 的多条 response 可能进不同 training step。GRPO 要把 $n$ 条 response 放在同一个窗口里统计组相对优势；拆开后 $\mathrm{std}(r)$ 和 advantage 对不上。要组内相对优势，先确认组还在同一统计窗口，再开均衡。flops 均衡可以开，data 均衡对 GRPO 要谨慎。

## 追问

**固定 micro-batch 为什么在长 chain of thought（CoT，即分步推理过程） 会出现数值异常？**
固定条数时，显存开销受最长序列影响，$m$ 条里一条 $8\mathrm{k}$ 就把整步顶满。按 token 拼可以让短的先凑满预算。
**为什么 logp 帽往往更大？**
重算 logp 没有优化器状态，但变长 packing 后单步 token 可能比训练 backward 更尖，单独设帽。
**`--balance-by-flops` 安全吗？**
更匀，但允许某个 batch 超过 token 帽。OOM 后先关它，不要先怪动态开关。
**和 `--balance-data` 一起开吗？**
对 GRPO 先不要。均衡负载和组统计是两件事，组散了优势为 0 或算错。
