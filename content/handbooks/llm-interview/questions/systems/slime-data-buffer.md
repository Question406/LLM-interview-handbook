---
id: slime-data-buffer
section: systems
order: 252
level: A
title: slime 的 Data Buffer 是干什么的？Agent 多轮要改哪一层？
quick: >-
  Buffer 是训练和 rollout 之间的唯一数据面：灌 prompt、收轨迹 / reward / verifier，再给 Megatron
  读。默认 `sglang_rollout.generate_rollout` 已带异步、dynamic sampling、partial
  rollout。多轮工具不要改 Megatron kernel，换 `--rollout-function-path` 包一层
  thought-action-obs。veRL 对等物是自定义 reward manager + env，不是同一个模块名。
tags:
  - slime
  - Agent RL
  - Data Buffer
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 文档
    url: https://thudm.github.io/slime/zh/index.html
    type: primary
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

这块容易把 Data Buffer 说成「一个 replay 队列」，或去 Megatron 里手写工具循环。官方说法：training / rollout / Data Buffer 是一条路，Agent 就是数据生成，不 fork 训练核。Buffer 是两边的 **唯一数据面**：灌 prompt、收轨迹 / reward / verifier / mask，再给 Megatron 读 packed/varlen batch。默认 `sglang_rollout.generate_rollout` 已带异步、dynamic sampling、partial rollout。多轮工具应换 `--custom-generate-function-path` 或 `--rollout-function-path` 包一层 thought-action-obs，见 `slime-custom-generate`。veRL 对等物是自定义 Reward Manager + Env，不是同一个模块名。别在训练核里调工具，那会把 serving 的连续 batch、前缀缓存全丢掉。

## 三框：Rollout / Buffer / Train

1. **Rollout（SGLang + router）**：生产 token 和工具结果，写入 Buffer。请求打 `--sglang-router-ip/port`。权重靠 `update_weights` 与 trainer 对齐，见 `slime-weight-sync`。
2. **Buffer**：保存可训练字段（prompt、response、`loss_mask`、reward、group id、`status`、`policy_version`）。partial 半成品也在这里，默认 `--buffer-filter-path` FIFO（`pop_first`）。
3. **Train（Megatron）**：从 Buffer 取 batch，更新后再把新权推回引擎。

面试画三框比背类名有用。Buffer 不是算法：`--advantage-estimator` 在 train 侧读完 Buffer 之后算。dynamic sampling 的 abort / 回收也通过 Buffer 把未完成 `Sample` 塞回去。FIFO 会把没写完的长题优先弹出，下一步可能被同一批长尾拖住，要用 filter 或长度惩罚对冲，见 `slime-dynamic-partial`。

## Agent 改哪一层

魔改顺序：`--custom-rm-path` → 单条 `--custom-generate-function-path` → 整段 `--rollout-function-path` → `--advantage-estimator` → Megatron 并行。和 veRL「先改 Reward Manager」同一精神，只是 slime 把生成函数当成一等接口。多轮必须在 Sample 上填对 `tokens`、`response_length`、observation 的 mask=0。不要为了 Agent 换 `--colocate` 或 TP，放置和数据面正交。fully-async 的 in-flight 池仍然写入同一 Buffer，只是交组不再等整个 `rollout_id`；stale 靠 version / TIS / mask，Buffer 必须留下版本字段。

## 和 veRL 怎么对、什么别做

veRL 没有叫 Data Buffer 的同名模块，数据面散在 rollout worker 输出和 trainer 输入。slime 把它收成显式队列，partial / abort / 自定义 generate 才好接。不要：在 Megatron forward 里调 HTTP 工具；绕过 Buffer 把 tensor 直接塞进 optimizer；评测轨迹和 train 轨迹混写同一条无 `evaluation` 标记的路径。`--eval-function-path` 分流。验收：Buffer 里一条样本能否反推出 group、$n$、mask、版本；缺字段下一步 GRPO 统计会 silently 错。

我会把 Data Buffer 画成唯一交接面：左边 SGLang+router 写入 token、mask、reward、status、`policy_version`；右边 Megatron 读 packed batch，更新后再 `update_weights`。Agent 多轮是左边怎么生成，不是右边怎么改 kernel。默认 `sglang_rollout.generate_rollout` 已经把异步、dynamic sampling、partial 接到这条面；你要做的是更浅的 `--custom-rm-path` / `--custom-generate-function-path`，或整段 `--rollout-function-path`。半截轨迹也住在 Buffer 里，FIFO `pop_first` 会把最长最难的题优先送回，长尾可能更尖，旧 token 必须 mask 或 `--use-tis`。fully-async 仍然写同一 Buffer，只是交组不等整个 `rollout_id`，版本字段更重要。veRL 没有同名模块，对等的是 rollout 输出到 actor 输入，魔改精神仍是 Reward Manager + Env。不要绕过 Buffer 把激活直接塞进 optimizer，也不要在 Megatron forward 里打工具 HTTP。面试能画出三框和字段契约，这题就过了；只说「有个队列」过不了追问。

## 字段契约

Buffer 里一条样本要能反推 group、$n$、mask、`status`、`policy_version`。缺字段则 GRPO 统计 silently 错。partial 半截也在这里，FIFO 会把长尾优先送回。fully-async 仍写同一面，版本更重要。不要绕过 Buffer 塞 tensor，不要在 Megatron 里打工具。veRL 对等的是 rollout 输出到 actor 输入，不是同名模块。

## 追问

- **Buffer 是 replay 吗？** 默认不是 off-policy experience replay。它是本步（以及 partial 跨步）的交接面。若当 replay 用，必须自己管 freshness 和 `policy_version`，否则旧轨迹会当 on-policy 进 loss。
- **为什么不要改 Megatron 做工具？** 会丢掉 SGLang 的连续 batch、前缀缓存和页式 KV，训练核还会被环境 RTT 堵住。Agent 是数据生成，换 generate / RM 函数，不 fork 训练核。
- **partial 的半截存在哪？** Buffer。`--partial-rollout` 写入，`--buffer-filter-path` 默认 FIFO 弹出。前半段是旧权，必须 `--mask-offpolicy-in-partial-rollout` 或 `--use-tis`。两边都关是数学错误。
- **和 veRL 一句话对？** Buffer ≈ rollout worker 输出到 actor 输入的显式队列。魔改精神仍是 Reward Manager + Env，不是改 HybridEngine 或 Megatron kernel。模块名不同，分层相同。
- **FIFO 有什么坑？** 没写完的往往是最长最难的题，`pop_first` 把它们优先送回，下一步长尾更尖。可换 `--buffer-filter-path`，但要声明 freshness 变了。这和动态采样提高有效组是相反的压力。
