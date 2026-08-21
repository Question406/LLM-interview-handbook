---
id: infra-rl-rollout-optimize
section: systems
order: 238
level: A
title: AI Infra 实习：RL rollout 有哪些优化？量化、异步分别换什么？
quick: >-
  吞吐：vLLM/SGLang、连续 batch、前缀缓存、动态过滤废组。显存：rollout 权重量化或 KV 量化，训练仍 bf16。时间线：异步
  rollout 让生成和更新重叠，换来策略 stale。先画瓶颈再选，不要三件一起开。
tags:
  - RL Infra
  - Rollout
  - Async RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: AI infra实习面经（小厂）
    url: https://www.nowcoder.com/feed/main/detail/166e576d5afa4a298cf9492ed51bed04
    type: candidate-first-hand
  - title: verl fully async
    url: https://github.com/verl-project/verl/blob/main/docs/advance/fully_async.md
    type: primary
---

## 真题记录

- 岗位：AI Infra 实习
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“rl里rollout有哪些优化点（rollout量化 异步rollout等）”**

陷阱是把量化、异步、动态过滤当成「三个都开就更快」。面试先画瓶颈：tokens/s 不够、显存爆、还是墙钟被最长样本拖死，再换对应的东西。三件一起开会把分布偏移、policy stale、半截轨迹缠在一起，出了问题没法归因。Continuous batching 是引擎内交错请求，没有策略版本差，不要和异步 RL 用同一个词。

## 引擎：换吞吐，不换算法

HF `generate` 是逐步同步、静态 batch，最长序列拖死整组。换成 vLLM / SGLang：continuous batching、PagedAttention、prefix cache。公共 system prompt 的 KV 能复用，但 key 必须带 `policy_version`，否则旧激活会续进新权。Agent 任务再开工具超时和 session 亲和，请求打 router 而不是绑死某一个 engine。验收看有效 tokens/s 和 KV 占用，不要报 MFU——decode 本就是 memory-bound。veRL 走 `actor_rollout_ref.rollout` 接 vLLM/SGLang；slime 默认 SGLang + `--sglang-router-ip/port`。引擎优化解决的是「同样 $n$ 条、同样长度，生成更快」，不解决全对/全错组没有梯度。

## 量化：只动采样副本

量化换的是 **采样侧显存 / 带宽**，不是训练精度。常见：BF16 训 + FP8/INT8 权或 KV 量化采。actor backward、Adam、reference 仍用训练精度。要主动补一句：量化引擎的 token logp **不能**当 $\pi_{\mathrm{old}}$，ratio / KL 必须回 FSDP/Megatron 训练图重算，见 `meituan-verl-recompute-logprob`。slime 落地就是 BF16 Megatron + FP8 SGLang，再叠 `--use-tis` 修采样分布隙。量化引入的是分布偏移，不是免费的「同样策略更省」。holdout 掉了先 A/B 量化开关，再查异步 stale。

## 异步与减废：换时间线，买 stale

异步换的是 **生成与 backward 重叠**。veRL fully-async 用 staleness 阈值丢过期轨迹；slime 分清两档：挪 `train.py` 里的 `ray.get`（仍按 `rollout_id` 切步）和换 `train_async.py` + `generate_rollout_fully_async`（后台队列跨步交组）。`--colocate` 下 offload 把重叠窗口削掉，要吃异步先分卡。换来的是 $\pi$ stale，必须 TIS / freshness / 丢弃之一。算法侧减废：DAPO 丢掉 $\mathrm{std}(r)=0$ 的全对/全错组，slime 用 `--dynamic-sampling-filter-path`（如 `check_reward_nonzero_std`）+ `--over-sampling-batch-size`；半截走 `--partial-rollout`，旧 token 要 `--mask-offpolicy-in-partial-rollout` 或 `--use-tis`。截断过长、限制 `rollout.n` / `--n-samples-per-prompt` 也是减 KV，不是算法升级。验收：tokens/s、stale 比例、zero-std 组比例、eval，不看「开了异步」。

把三件优化画成三列再开口：引擎换吞吐、量化换采样显存、异步换时间重叠。每一列都有税——量化有分布偏移，异步有 trajectory age，动态过滤有 abort 白烧和半截 stale。面试被问「你们 rollout 做了哪些优化」时，先报当前瓶颈占比（生成 / KV / 最长样本 / 工具等待），再报开了哪一列、税怎么收。同卡 `--colocate` 时异步列几乎没窗口，先分卡；FP8 采样时量化列必须叠训练图重算和 `--use-tis`。不要用「我们上了 vLLM」代替这张表。长 CoT 任务默认 generation-bound，优化顺序是引擎与长尾，而不是先把 ZeRO-3 开满。Agent 任务默认 env-bound，优化顺序是工具超时和 fully-async 交组。两套负载用同一套开关会被追问拆穿。周报里写清 `n`、平均长度、是否量化、异步是哪一档，否则「rollout 快了 30%」无法复现。

## 验收口径

周报不要写「开了异步和量化」。写：生成占墙钟多少、KV 峰值、stale 年龄分位数、zero-std 组比例、holdout。量化只动采样副本，训练仍 bf16；异步分清挪 `ray.get` 和 `train_async.py`；过滤走 `--dynamic-sampling-filter-path`，半截走 `--partial-rollout` 并 mask/TIS。同卡先承认叠不动。这套口径比堆 flag 更像做过 Infra。

## 追问

- **量化、异步、过滤能不能一起开？** 能，但必须按瓶颈排序。显存爆先量化采样副本；墙钟被生成占满先换引擎和连续 batch；最长样本或工具等待再异步 / partial。三件一起开，分布偏移、stale、半截轨迹缠在一起，出了问题无法归因。面试先报当前占比再报开关。
- **量化 logp 能进 ratio 吗？** 不能。FP8 SGLang 与 FSDP/Megatron 差千分位，$\rho$ 会漂，clip 变假。训练图重算仍必要；`--use-tis` 只修采样分布隙，代替不了重算。BF16 训 + FP8 采是标准例子。
- **挪 `ray.get` 算 fully-async 吗？** 不算。那一档仍按 `rollout_id` 切步，只是训推重叠。真正 fully-async 换 `train_async.py` + `generate_rollout_fully_async`，后台队列交组，必须管 trajectory age 和 TIS。
- **`--colocate` 下异步有用吗？** 收益很小。`--offload-train` / `--offload-rollout` 让两边无法同时占 GPU，重叠窗口被物理削掉。要吃异步，先分卡。把一体部署说成异步会被拆穿。
- **动态过滤是调温度吗？** 不是。温度管组内多样性；`--dynamic-sampling-filter-path`（如 `check_reward_nonzero_std`）管这组有没有可学信号。半截不是新的 on-policy token，要 mask 或 TIS。over-sample 只为滤完仍凑满 batch。
