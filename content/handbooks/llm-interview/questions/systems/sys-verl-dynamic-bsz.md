---
id: sys-verl-dynamic-bsz
section: systems
order: 242
level: A
title: veRL 的 `use_dynamic_bsz` 和写死 micro-batch 有何不同？
quick: "固定 micro-batch 限制每卡样本条数，动态 batch 则按每卡 token 预算拼序列。长 CoT 的长度差异大，按 token 切分能减少 padding 和 OOM；actor、ref 和 rollout 重算 logp 的路径要一起配置，并保留 GRPO 的组统计边界。"
tags:
  - VeRL
  - Batch
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁 26 秋招 VeRL batch 面经
    url: https://www.nowcoder.com/feed/main/detail/e2585943c7874b3081b0878b646b6f01
    type: candidate-first-hand
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

设置 `use_dynamic_bsz=True` 后，`ppo_micro_batch_size_per_gpu` 不再单独决定实际条数。`use_dynamic_bsz` 把每卡固定样本数改成每卡 token 预算，实际放几条由序列长度决定。比如一条 8k、三条 512 的回复，固定 $m$ 条时整步按最长的 8k 配显存；把 $m$ 降到 1 虽然能避开长序列 OOM，短序列又吃不满 GPU。预算设为 8k 时，动态模式可以放一条 8k，也可以放四条 2k。

固定 `ppo_micro_batch_size_per_gpu=$m$` 的峰值 $\propto m\times T_{\max}$，适合长度接近的监督微调（SFT）。GRPO 同一组的 $n$ 条回复经常差一个数量级，按 token 拼更接近真实负载。Packing 能提高有效 token 的比例，但样本条数随长度变化，汇报时应给 `tokens / step`、峰值 token 和 drop-last，不能再固定报每卡 4 条。这和 serving continuous batching 都按 token 形状调度，不过这里作用于训练 / 重算 logp 图，并非逐 token 生成（decode）引擎。

## 配置与组统计怎么对齐

Actor、ref 和 rollout 重算 logp 要一起配置，对应 `actor.ppo_max_token_len_per_gpu`、`ref.log_prob_max_token_len_per_gpu`、`rollout.log_prob_max_token_len_per_gpu`。只改 actor，训练能装下，其他路径仍按旧 $m$ 切，长 CoT 就可能在 ref 或 logp 前向 OOM，训练图却很闲。三条路径的预算应在同一量级；logp 没有反向，可以适当更大，但开关不能一个 True、两个 False。slime 对应 `--use-dynamic-batch-size --max-tokens-per-gpu`，logp 另设 `--log-probs-max-tokens-per-gpu`。对应时，`--max-tokens-per-gpu` 对应 `ppo_max_token_len_per_gpu`。

有上下文并行时，要按本地切开的长度估预算，例如 `max_response_len / cp_size`，继续按全长 $T$ 算会让某个 rank 先 OOM。预算还需给 all-gather、logits、临时张量和碎片留空间，序列 token 刚到上限就 OOM，通常说明这个余量不足。

GRPO 的 $\hat A$ 来自同一输入提示的 $n$ 条回复，动态拼 batch 时必须让组均值和优势仍在同一统计窗口计算。把组拆到不同 micro-batch / step 后各算各的，会改变估计器，全对全错的零梯度判断也会漂。slime 的 `--balance-data` 文档说明，同一 prompt 的 response 可能被分到不同 step，开启前要确认统计窗口。drop-last 会丢掉尾部不够预算的组，长度过滤、DAPO 动态采样也会改变有效组数；日志要同时记录名义组和有效组，防止有效 $n$ 被悄悄改掉。

理解配置时，可以先画输入提示（prompt）$\times n$ → global batch → 每卡 token。动态 batch 按 token 上限拼 micro-batch；动态采样丢掉零方差组再补采；partial rollout 让半截轨迹跨步继续生成。三者都影响一步看见几条，但分别改变显存形状、采样组和生成进度。

调试时先对日志：每卡不超过 $T$ token、本步实际 $k$ 条、drop-last 丢掉 $d$ 组。token 数远低于预算且 micro-batch 很多，说明拼得太碎，可能是过滤过狠或长度分布极偏；经常贴着上限 OOM，就查临时张量余量。再看 GRPO 组是否被拆开，优势方差突然异常时先查统计窗口，再调温度或学习率。监控横轴改成 tokens / step，叠加有效组和 drop-last，条数随长度浮动才不会被误读成异常。

## 追问

**长度比较整齐时也要开动态 batch 吗？**
不一定。固定 $m$ 更容易调试和核对；completion 长度方差大、容易 OOM 时，动态方式更合适。

**只开 actor 后仍然 OOM，先看哪里？**
先看 ref 和重算 logp 是否仍按旧 $m$ 切分。三条路径都要启用动态切分，并分别设置预算。

**怎样回答蚂蚁面经里的“每卡样本数”？**
先说明动态模式下条数是长度与预算共同决定的结果，再报 tokens / step、有效组和 drop-last。字段核对见 `ant-verl-rollout-batch-accounting`。

相关：`sys-rl-why-vllm-rollout`、`meituan-verl-recompute-logprob`、`slime-dynamic-bsz`、`sys-rl-group-n`、`byte-grpo-all-same-zero-adv`、`slime-dynamic-partial`
