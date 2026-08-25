---
id: sys-verl-dynamic-bsz
section: systems
order: 242
level: A
title: veRL 的 `use_dynamic_bsz` 和写死 micro-batch 有何不同？
quick: >-
  动态 batch 按**每卡 token 上限**拼序列，而不是固定条数。长 CoT 时固定 $m$ 条会 OOM 或严重 padding。打开后改
  `ppo_max_token_len_per_gpu`，并让 actor / ref / rollout 的 logp 路径同一套开关，否则账本对不齐。
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

这块容易把 `ppo_micro_batch_size_per_gpu` 当成「每卡样本数」的唯一旋钮。长 CoT 下固定 $m$ 条，显存跟最长那条走，短序列全在 pad；打开动态 batch 却只改 actor，ref / rollout 重算 logp 时会 OOM 或变慢。动态模式改的是**每卡 token 预算**，条数变成因变量。和蚂蚁「每卡样本数」连问时，我先声明：开了动态开关，样本数不再是常数，汇报改成 tokens / step。GRPO 的 completion 方差远大于 SFT，这题几乎是默认该会的工程开关。

## 固定条数 vs token 预算

写死 `ppo_micro_batch_size_per_gpu=$m$`：每步 $m$ 条，峰值 $\propto m\times T_{\max}$。一条 8k、三条 512，整步仍按 8k 配显存，短的在浪费；反过来为了不被 8k 打死把 $m$ 降到 1，短序列又吃不满 GPU。`use_dynamic_bsz=True` 后目标是每卡 token 上限，条数浮动：预算 8k 时可以是一条 8k，也可以是四条 2k。packing 提高有效 token，但「一步几条」不再可报死数。我会改口：报 `tokens / step`、峰值 token、drop-last，而不是「每卡 4 条」。固定 $m$ 适合长度齐的 SFT；GRPO 的 $n$ 条回复经常差一个数量级，动态 batch 才对得上真实负载。这和 serving 的 continuous batching 是同一直觉：按 token 形状调度，不按请求条数，见 `sys-rl-why-vllm-rollout`。差别是这里发生在训练 / 重算 logp 图上，不是 decode 引擎里。

## 三条路径必须同一套开关

必须一起改：`actor.ppo_max_token_len_per_gpu`、`ref.log_prob_max_token_len_per_gpu`、`rollout.log_prob_max_token_len_per_gpu`。只开 actor，训练图能装下，ref / 重算 logp 仍按旧 $m$ 切，长序列在 logp 路径爆，训练图却看起来很闲。美团「为什么要重算 logp」那题会和这题缠在一起，见 `meituan-verl-recompute-logprob`。三条路径的 token 帽应对齐同一量级；logp 无反向，往往可以更大，但开关不能一个 True、两个 False。slime 对应 `--use-dynamic-batch-size --max-tokens-per-gpu`，logp 另设 `--log-probs-max-tokens-per-gpu`，对照见 `slime-dynamic-bsz`。字段对不上，账本就会和蚂蚁那题的「每卡样本数」各说各话，见 `ant-verl-rollout-batch-accounting`。有上下文并行时，预算还要按 `max_response_len / cp_size` 估，否则看起来没超帽、某张卡已经炸。

## 别拆开 GRPO 组

动态拼 batch 会改变 group 边界。GRPO 的 $\hat A$ 是同一 prompt 的 $n$ 条相对优势，见 `sys-rl-group-n`。packing 若把同组拆进不同 micro-batch / step，组均值就算错，全对全错的零梯度判断也会漂，和 `byte-grpo-all-same-zero-adv` 对不上。slime 的 `--balance-data` 文档写明可能把同一 prompt 的 response 分到不同 step，先确认组还在同一统计窗口再开均衡。drop-last 会丢掉尾部不够预算的组，有效 $n$ 可能被静默改掉，日志里要同时看名义组和有效组。和蚂蚁连问时先画：prompt $\times n$ → global batch → 每卡 token；动态模式下「样本数」是结果不是输入。长度过滤、DAPO 动态采样会再改有效组，见 `slime-dynamic-partial`，不要和 `use_dynamic_bsz` 当成同一个开关。

我会把三个「动态」拆开说：动态 batch 是按 token 帽拼 micro-batch；动态采样是丢掉零方差组再补采；partial rollout 是半截轨迹跨步接着生成。三者都会改「一步看见几条」，但改的对象不同。打开之后，会计账从「每卡 $m$ 条」改成「每卡不超过 $T$ token、本步实际 $k$ 条、drop-last 丢掉 $d$ 组」，这三件事都要能从日志对上。对不上就不要先加学习率。

调试顺序也要改：先看每步实际 token 数是否贴着帽，再看有没有频繁 drop-last，再看 GRPO 组是否还在同一 micro-batch。token 数远低于帽说明拼得太碎或过滤过狠；经常顶帽并 OOM 说明帽和真实峰值（含临时张量）没对齐，要给 all-gather / logits 留余量。组被拆开时优势方差会突然变怪，不要先动温度。监控面板如果还按「每卡样本数」画图，会看起来像 batch 在随机跳。把横轴改成 tokens / step，跳变才是真异常。

## 追问

- **打开后还报每卡 $m$ 条？** 错。改报 tokens / step 和峰值长度。$m$ 已不是约束，再报会和配置对不上。
- **只改 actor 会怎样？** 重算 logp 或 ref 前向按旧切分，长 CoT 在那条路径 OOM，训练图却很闲。三条路径同一套开关。
- **和固定 micro-batch 怎么选？** 长度齐用固定 $m$ 更好调、更好对账；completion 方差大、易 OOM 就开动态。
- **会不会拆 GRPO 组？** 会。组相对优势必须同一统计窗口；`--balance-data` 尤其危险。拆组等于换了估计器。
- **drop-last 的代价？** 尾部不够预算的组被丢，有效样本和名义 $n$ 对不上，要在日志里对账。
- **slime 字段怎么对？** `--max-tokens-per-gpu` ↔ `ppo_max_token_len_per_gpu`；logp 帽单独设，见 `slime-dynamic-bsz`。
- **和蚂蚁「每卡样本数」怎么收束？** 先声明动态模式下样本数不是常数，再画 prompt $\times n$ → token 帽，见 `ant-verl-rollout-batch-accounting`。报 tokens / step、有效组和 drop-last，不要报一个死 $m$。
- **三个「动态」怎么分？** 动态 batch 管显存形状；动态采样管零方差组；partial rollout 管半截轨迹。不要用一个开关回答三个问题。
- **CP 开启后预算怎么估？** 按本地切开的序列长度估，不能仍用全长 $T$ 当每卡 token 帽，否则某 rank 先炸。
- **监控为什么不能再用每卡样本数？** 条数已是因变量，图上会随机跳。横轴改成 tokens / step，再叠有效组和 drop-last，才能看出是拼得太碎、顶帽还是拆组。
- **帽要不要留余量？** 要。token 帽只管序列本体，all-gather、logits、碎片会把峰值抬上去。顶帽就 OOM 说明余量不够，不是动态 batch 没用。
- **拼得太碎是什么样子？** token 数远低于帽、micro-batch 很多、GPU 吃不满。过滤过狠或长度分布极偏时出现，先查过滤和组是否被拆，再加帽。
- **开了还炸先查什么？** 是不是只开了 actor、logp 路径仍按旧 $m$ 切。三条路径同一套开关。
