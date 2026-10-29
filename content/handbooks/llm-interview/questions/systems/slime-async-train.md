---
id: slime-async-train
section: systems
order: 259
level: S
title: slime 的异步训练怎么开？挪 `ray.get` 和 `train_async.py` 是一回事吗？
quick: >-
  挪 `ray.get` 可以让下一轮 generate 与本轮 train 重叠，但仍按 rollout boundaries
  等齐；`train_async.py` 配 fully-async generate 则用后台队列跨步交组，不等最慢请求。后者要管理 trajectory
  age、TIS 和丢弃策略，且分卡部署才有充分的训推重叠空间。
tags:
  - slime
  - Async RL
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: slime fully-async 示例
    url: 'https://thudm.github.io/slime/_examples_synced/fully_async/README.html'
    type: primary
  - title: LMSYS slime 介绍
    url: 'https://www.lmsys.org/blog/2025-07-09-slime/'
    type: primary
---

两者的区别在于是否仍按 rollout boundaries 等齐。挪 `ray.get` 只是后移等待点，让下一轮生成与本轮训练重叠；换 `train_async.py` 后，后台队列可以跨步保留请求，完成足够的组就交给训练，这才是 fully-async。

比如一个 Agent 请求还在等工具，其他组已经完成，fully-async 可以先训练已完成的组。代价是轨迹可能来自旧策略，要管理 policy stale；若 throughput 升了、正确率却掉了，我会先检查 trajectory age 和 KL。引擎内部的 continuous batching 又是另一层，见 `sys-cont-batch`。`--colocate` 配 offload 时训推很难同时运行，先分卡才有充分的重叠空间。

## 轻量：挪 `ray.get`

默认 `train.py` 里，generate 的 `ray.get` 是硬同步点：本轮轨迹没齐，train 不开始；train 没结束，下一轮 generate 不发。把 `ray.get` 往后挪，可以让下一轮 generate 和本轮 train 重叠。语义仍是：按 sampling 轨迹（rollout） boundary 对齐，最慢那条 completion 仍决定这一步何时「齐」。

这适合中等长度、想先叠 throughput、还不想引入跨步 stale 的场景。轨迹相对 $\pi_{\mathrm{now}}$ 最多差半步到一步，ratio 还比较接近 1。colocate + offload 时 overlap 空间很小：训练要把 SGLang 挤出显存，物理上叠不动。分卡才吃得开这一档异步。别说「一体部署就是异步」。挪 `ray.get` 的正确位置是：本轮 train 启动之后、下轮 generate 的结果在用之前再 wait。挪得太早，仍是串行；挪过了「用结果」的点，会读到未完成的 future。我会读 `train.py`，不背 flag，因为官方就是让你看见这条时间线。

## Fully-async：换入口和 generate 函数

真正的 fully-async 要换 `train_async.py`，并设

`--rollout-function-path slime.rollout.fully_async_rollout.generate_rollout_fully_async`。

后台 `AsyncRolloutWorker` 维持 in-flight 池，凑满 `rollout_batch_size` 组就交，不等「这一 rollout_id 的所有请求结束」。默认 generate 仍是 `sglang_rollout.generate_rollout`，两条路径不要混。Agent / 工具长尾时，最慢样本不再拖死一步，这才是换入口的理由。

自定义 generate / reward model（RM） 在 fully-async 下仍走 `--custom-generate-function-path` / `--custom-rm-path`，不要为了异步重写整个 loop。水位常见于 `sglang_server_concurrency`：队列太浅叠不上，太深则轨迹相对当前 $\theta$ 过旧。

换来的是 stale：交上来的组可能生于 $k$ 步之前的权。要配 TIS（`--use-tis`）或 freshness / mask，盯 KL、$\rho$ 分位数、trajectory age。throughput 涨而 holdout 掉，就是异步把 off-policy 买过头了。veRL 用 staleness 阈值丢轨迹；slime 用队列水位和 IS / mask，见 `sys-rl-infra`。in-flight 池太深时，最旧的样本可能落后数十步，clip 也救不了 $\rho$ 偏离。可以设最大 age：超了就丢、重采，或只 mask 旧 token。Agent 长尾是 fully-async 的主场：工具调用 10 秒的那条不应堵住已经写完的 32 组。但环境失败、重试、session 状态要和队列语义对齐，否则会把半截 tool 轨迹当完整 episode。



分卡 + fully-async 才能让 SGLang 一直 CUDA graph 着、trainer 一直 backward。`--colocate` 下 offload 把重叠窗口削掉，fully-async 收益很小。partial rollout 又引入另一类旧 token（半截 prefix），见 `slime-dynamic-partial`。两条 stale 来源要一起管，不要只开一个开关就报「已经异步了」。



引擎内 continuous batching、`train.py` 里挪 `ray.get`、`train_async.py` 的 fully-async，是三层。第一层解决短请求空等，没有 policy stale。第二层让下一轮 generate 和本轮 train 重叠，仍按 `rollout_id` 切步，stale 最多约一步。第三层后台队列交组，stale 由水位和 age 决定，必须 TIS / 丢弃 / mask。`--colocate` 会把二、三层的重叠窗口削掉，因为 offload 让两边无法同时占 GPU。分卡才是异步的物理前提。自定义 generate / RM 继续走 `--custom-generate-function-path` / `--custom-rm-path`，不要为异步重写 loop。被问「你们异步了吗」时，先说是哪一层、stale 怎么管、放置是不是分卡。只说打开了 async，还不足以说明轨迹的新鲜度。throughput 涨、holdout 掉，优先查 trajectory age，而不是加学习率。

## 追问

**挪 `ray.get` 和 `train_async.py` 是一回事吗？**
不是。前者仍按 `rollout_id` 切步，只是把 wait 点后移，让下一轮 generate 和本轮 train 重叠；后者换入口和 `generate_rollout_fully_async`，后台 `AsyncRolloutWorker` 维持 in-flight 池，凑满 batch 就交。
**Continuous batching 算异步 RL 吗？**
不算。那是引擎一步之内的请求交错，没有策略版本差，见 `sys-cont-batch`。异步 RL 是 trainer 与 rollout 之间的流水线，带 $\pi$ 的 stale。回答时要说明自己讨论的是哪一层。
**必须上 TIS 吗？**
步间 gap 大就必须有 IS / 丢弃 / mask 之一。gap 只有半步、KL 仍稳，可以先监控再加。fully-async 队列一深，通常就必须上。throughput 涨而 holdout 掉，优先查 trajectory age。
**为什么官方把 loop 摊开？**
让你看见同步点在哪。包成 `Trainer.fit()` 之后，「异步」会变成一个布尔，stale 从哪来就讲不清。我会读 `train.py`，不背 flag。
**`--colocate` 下 fully-async 有用吗？**
收益很小。offload 让训推无法同时占 GPU，重叠窗口被物理削掉。要吃异步，先分卡。
**自定义 generate 要不要为异步重写？**
不要。fully-async 下仍走 `--custom-generate-function-path` / `--custom-rm-path`。重写 loop 容易把 Buffer 和 freshness 搞丢。
**队列多深合适？**
浅了叠不上 throughput，深了 age 过大 $\rho$ 偏离。用 `sglang_server_concurrency` 当水位，盯 KL 分位数，超了就丢或 TIS，不要只把池开到满。
**Agent 工具长尾为什么必须 fully-async？**
最慢那条可能卡在 sandbox 十几秒，同步一步会被它拖死。队列交组让已完成的 32 组先训，但 session 状态和重试要和队列语义对齐，半截 tool 轨迹不能当完整 episode。
**怎么证明你真的异步了？**
画出 wait 点：`train.py` 里 `ray.get` 的位置，或 `train_async.py` + `generate_rollout_fully_async`。再报 stale 怎么管（TIS / age / 丢弃）和是否分卡。说「开了 colocate」不算异步。挪 `ray.get` 仍按 rollout 切步；真正 fully-async 才后台保活、跨步交组。两档不要说成一回事，colocate 下 overlap 空间更小。
