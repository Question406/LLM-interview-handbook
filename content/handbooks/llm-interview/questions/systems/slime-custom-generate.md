---
id: slime-custom-generate
section: systems
order: 257
level: A
title: slime 做多轮工具 / 自定义 reward，该换哪一层函数？
quick: "我会按改动范围选接口：只换分数用 `--custom-rm-path`，多轮工具循环用 `--custom-generate-function-path`，改整组采样策略才用 `--rollout-function-path`。多轮样本要填对 `tokens`、`response_length`、`loss_mask` 和 `status`，对应 veRL 的 Reward Manager + Env 分层。"
tags:
  - slime
  - Agent RL
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

多轮工具和 reward 应优先改数据生成接口：只改分数，用 `--custom-rm-path`；改一条样本的工具循环，用 `--custom-generate-function-path`；要接管整组 `generate_rollout` 采样，再换 `--rollout-function-path`。这样能继续利用默认的 continuous batching、dynamic sampling 和 partial 采样轨迹（rollout）。

比如数学验证器只需换打分函数，thought-action-obs 则需要改单条生成过程，通常没必要改 Megatron kernel 或 trainer step。对应 veRL，可以理解成 Reward Manager、Env / tool loop 和 rollout worker 三层。请求仍走 router（`--sglang-router-ip/port`），`rollout_id` 保证续训顺序，评测另挂 `--eval-function-path`。

## 三档分别换什么

| 你要改的 | slime | veRL 近似 |
| --- | --- | --- |
| 对错 / 验证器（verifier） | `--custom-rm-path` | Reward Manager |
| 单条采样 + 工具循环 | `--custom-generate-function-path` | Env / tool loop |
| 组采样、partial、eval 分流 | `--rollout-function-path` | 自定义 rollout worker |
| 算法 | `--advantage-estimator` | `algorithm.adv_estimator` |

只换打分：数学题、编译器、规则奖励，走 `--custom-rm-path`，默认 `sglang_rollout.generate_rollout` 仍管异步、dynamic sampling、abort。多轮 thought-action-obs：换 `--custom-generate-function-path` 的单条 `async generate`，仍享受外层调度。只有要改组策略、自己做 partial / eval 分流，才整段换 `--rollout-function-path`。`generate_rollout(args, rollout_id, data_source, evaluation)` 必须带回 `RolloutFnTrainOutput`。fully-async 下自定义 generate / 奖励模型（RM） 仍走这两条 path，不要为异步重写 loop，见 `slime-async-train`。

## Sample 字段是训练契约

- `tokens` = 输入提示（prompt） + response；多轮 `response_length` = 去掉首轮 prompt 后的长度。
- `loss_mask` 和 `response_length` 同长，工具 observation 对应位置置 0，只训练模型生成的 token。
- `status`：`COMPLETED` / `TRUNCATED` / `ABORTED` / `FAILED`。partial rollout 靠 `data_source` 把半成品塞回去；`ABORTED` 与 `--partial-rollout` 回收语义要对齐。
- 失败环境不要假装 `COMPLETED` 再给 0 分，否则 GRPO 组统计被脏样本污染。

漏 mask 会把工具返回当策略梯度；漏 `response_length` 会让旧 prefix 在 partial 下算进 on-policy。Buffer 只信这些字段，不信你在 generate 里 print 的调试信息。



多引擎时走 router，session 亲和见 `slime-router-session`。绑死 ip 会让 continuous batching 和 PD 分离失效。Megatron 里手写工具循环会丢掉 serving 的前缀缓存和页式 KV，实际耗时和正确性一起崩。改动可以从奖励分数（reward）开始，再依次考虑单条 generate、整段 rollout、advantage 和并行。和 veRL「先改 Reward Manager」同一精神。`--eval-function-path` 独立，避免 train 的 tool 超时污染评测。

## 追问

**只改分数换哪一层？**
`--custom-rm-path`。默认 `sglang_rollout.generate_rollout` 仍管异步、dynamic sampling、abort。不要为了改 verifier 重写 generate。
**多轮工具呢？**
`--custom-generate-function-path` 换单条 `async generate`。`tokens` 含 prompt+response，`response_length` 去掉首轮 prompt，`loss_mask` 同长且工具观测为 0，`status` 用四种枚举。失败不要标 `COMPLETED` 再给 0 分。
**什么时候换 `--rollout-function-path`？**
要改组采样、partial、eval 分流，或必须返回 `RolloutFnTrainOutput`。签名是 `generate_rollout(args, rollout_id, data_source, evaluation)`。能浅则浅，整段换容易丢掉官方 abort/回收。
**为什么必须打 router？**
引擎池、PD 分离、session 哈希都在 `--sglang-router-ip/port`。绑单个 engine 会失去 continuous batching，也让多副本同步失效。
**fully-async 要重写 loop 吗？**
不要。仍走 `--custom-generate-function-path` / `--custom-rm-path`。重写 loop 容易把 Data Buffer 和 freshness 搞丢，见 `slime-async-train`。`rollout_id` 保证续训顺序。
