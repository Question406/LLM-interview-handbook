---
id: slime-data-buffer
section: systems
order: 252
level: A
title: slime 的 Data Buffer 是干什么的？Agent 多轮要改哪一层？
quick: "Data Buffer 是 rollout 与训练之间的数据交接面，保存 prompt、轨迹、reward、mask、状态和策略版本，再供 Megatron 读取。多轮 Agent 优先改生成或打分函数；半截轨迹和异步数据尤其要保留 group、版本及 mask，避免把旧 token 当成当前策略样本训练。"
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

Data Buffer 负责把生成端的数据交给训练端：提供 prompt，保存轨迹、reward、验证结果和 mask，再让 Megatron 读 packed/varlen batch。它保存的不只是完整回答，partial rollout 的半成品和策略版本也要经过这里。

比如 Agent 调过工具后，工具 observation 要留在上下文里，但对应的 loss mask 应是 0，不能当成模型自己的动作训练。多轮工具可以改 `--custom-generate-function-path` 或 `--rollout-function-path`，见 `slime-custom-generate`，默认 `sglang_rollout.generate_rollout` 的调度能力则尽量保留。veRL 大致对应 Reward Manager + Env；在 Megatron 里手写工具循环会丢掉 serving 的连续 batch 和前缀缓存。

## 三框：Rollout / Buffer / Train

1. Rollout（SGLang + router）：生成 token 和工具结果，写入 Buffer。请求打 `--sglang-router-ip/port`。权重靠 `update_weights` 与 trainer 对齐，见 `slime-weight-sync`。
2. Buffer：保存可训练字段（prompt、response、`loss_mask`、reward、group id、`status`、`policy_version`）。partial 半成品也在这里，默认 `--buffer-filter-path` FIFO（`pop_first`）。
3. Train（Megatron）：从 Buffer 取 batch，更新后再把新权推回引擎。

可以把生成、交接和训练画成三个框，检查字段怎样传递。Buffer 不是算法：`--advantage-estimator` 在 train 侧读完 Buffer 之后算。dynamic sampling 的 abort / 回收也通过 Buffer 把未完成 `Sample` 塞回去。FIFO 会把没写完的长题优先弹出，下一步可能被同一批长尾拖住，要用 filter 或长度惩罚对冲，见 `slime-dynamic-partial`。

## Agent 改哪一层

按改动范围从小到大，可以依次考虑：`--custom-rm-path` → 单条 `--custom-generate-function-path` → 整段 `--rollout-function-path` → `--advantage-estimator` → Megatron 并行。和 veRL「先改 Reward Manager」同一精神，只是 slime 把生成函数当成一等接口。多轮必须在 Sample 上填对 `tokens`、`response_length`、观测结果（observation） 的 mask=0。不要为了 Agent 换 `--colocate` 或 TP，放置和数据面正交。fully-async 的 in-flight 池仍然写入同一 Buffer，只是交组不再等整个 `rollout_id`；stale 靠 version / TIS / mask，Buffer 必须留下版本字段。



veRL 没有叫 Data Buffer 的同名模块，数据面散在 rollout worker 输出和 trainer 输入。slime 把它收成显式队列，partial / abort / 自定义 generate 才好接。Megatron forward 里调 HTTP 工具会阻塞训练，绕过 Buffer 直接把 tensor 塞给 optimizer 则会跳过数据交接检查；评测轨迹和 train 轨迹也要用 `evaluation` 标记分开。`--eval-function-path` 分流。验收：Buffer 里一条样本能否反推出 group、$n$、mask、版本；缺字段下一步 GRPO 统计会 silently 错。

## 追问

**Buffer 是 replay 吗？**
默认不是 off-policy experience replay。它是本步（以及 partial 跨步）的交接面。若当 replay 用，必须自己管 freshness 和 `policy_version`，否则旧轨迹会当 on-policy 进 损失（loss）。
**为什么不要改 Megatron 做工具？**
会丢掉 SGLang 的连续 batch、前缀缓存和页式 KV，训练核还会被环境 RTT 堵住。Agent 是数据生成，换 generate / 奖励模型（RM） 函数，不 fork 训练核。
**partial 的半截存在哪？**
Buffer。`--partial-rollout` 写入，`--buffer-filter-path` 默认 FIFO 弹出。前半段是旧权，必须 `--mask-offpolicy-in-partial-rollout` 或 `--use-tis`。两边都关是数学错误。
**和 veRL 一句话对？**
Buffer ≈ rollout worker 输出到 actor 输入的显式队列。魔改精神仍是 Reward Manager + Env，不是改 HybridEngine 或 Megatron kernel。模块名不同，分层相同。
**FIFO 有什么坑？**
没写完的往往是最长最难的题，`pop_first` 把它们优先送回，下一步长尾更尖。可换 `--buffer-filter-path`，但要声明 freshness 变了。这和动态采样提高有效组是相反的压力。
