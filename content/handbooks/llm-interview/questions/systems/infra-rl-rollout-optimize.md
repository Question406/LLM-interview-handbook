---
id: infra-rl-rollout-optimize
section: systems
order: 238
level: A
title: AI Infra 实习：RL rollout 有哪些优化？量化、异步分别换什么？
quick: >-
  我会先看 rollout 慢在生成 throughput、显存还是长样本等待，再选优化。vLLM/SGLang 和连续 batch 能提高
  throughput，sampling 副本量化能省显存，异步 rollout 能让生成和更新重叠，但会增加策略滞后；训练仍用 bf16。
tags:
  - RL Infra
  - Rollout
  - Async RL
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: AI infra实习面经（小厂）
    url: 'https://www.nowcoder.com/feed/main/detail/166e576d5afa4a298cf9492ed51bed04'
    type: candidate-first-hand
  - title: verl fully async
    url: 'https://github.com/verl-project/verl/blob/main/docs/advance/fully_async.md'
    type: primary
---

## 可以这样回答

RL rollout 的优化要先对应到瓶颈：生成 tokens/s 不够，就换推理引擎和连续 batch；显存不够，就量化 sampling 副本；时间耗在长样本或工具等待上，再考虑异步。比如一组请求里只有一个回答特别长，静态 batch 会让其余请求跟着等，continuous batching 可以在引擎内交错处理请求。它不涉及策略版本差，和异步 RL 要分开讲。

量化、异步和动态过滤最好逐项打开、分别验收。否则 sampling 分布偏移、policy stale 和半截轨迹的问题混在一起，很难判断效果变化来自哪里。

## 技术备查

## 真题记录

- 岗位：AI Infra 实习
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“rl 里 rollout 有哪些优化点（rollout 量化 异步 rollout 等）”**

RL rollout 的优化要先对应到瓶颈：生成 tokens/s 不够，就换推理引擎和连续 batch；显存不够，就量化 sampling 副本；时间耗在长样本或工具等待上，再考虑异步。比如一组请求里只有一个回答特别长，静态 batch 会让其余请求跟着等，continuous batching 可以在引擎内交错处理请求。它不涉及策略版本差，和异步 RL 要分开讲。

量化、异步和动态过滤最好逐项打开、分别验收。否则 sampling 分布偏移、policy stale 和半截轨迹的问题混在一起，很难判断效果变化来自哪里。

## 先提高生成效率，再检查 sampling 精度

HF `generate` 是逐步同步、静态 batch，最长序列拖死整组。换成 vLLM / SGLang：continuous batching、PagedAttention、prefix cache。公共 system prompt 的 KV 能复用，但 key 必须带 `policy_version`，否则旧激活会续进新权。Agent 任务再开工具超时和 session 亲和，请求打 router 而不是绑死某一个 engine。验收看有效 tokens/s 和 KV 占用，不要报 MFU，逐 token 生成（decode） 本就是 memory-bound。veRL 走 `actor_rollout_ref.rollout` 接 vLLM/SGLang；slime 默认 SGLang + `--sglang-router-ip/port`。引擎优化解决的是「同样 $n$ 条、同样长度，生成更快」，不解决全对/全错组没有梯度。



量化主要减少 sampling 侧的显存和带宽开销。常见做法是训练用 BF16，sampling 用 FP8/INT8 权重或 KV 量化。actor backward、Adam、reference 仍用训练精度。量化引擎的 token logp 不能直接当 $\pi_{\mathrm{old}}$，ratio / KL 必须回 FSDP/Megatron 训练图重算，见 `meituan-verl-recompute-logprob`。slime 落地就是 BF16 Megatron + FP8 SGLang，再叠 `--use-tis` 修 sampling 分布隙。量化引入的是分布偏移，不是免费的「同样策略更省」。holdout 掉了先 A/B 量化开关，再查异步 stale。

## 让训练和 sampling 重叠，并减少无效样本

异步让生成与 backward 同时运行。veRL fully-async 用 staleness 阈值丢过期轨迹；slime 分清两档：挪 `train.py` 里的 `ray.get`（仍按 `rollout_id` 切步）和换 `train_async.py` + `generate_rollout_fully_async`（后台队列跨步交组）。`--colocate` 下 offload 把重叠窗口削掉，要获得异步收益，先让训推使用不同 GPU。代价是 sampling 策略 $\pi$ 会滞后，需要用 TIS 修正、限制 freshness，或丢弃过旧轨迹。

算法侧还可以减少没有学习信号的样本。DAPO 丢掉 $\mathrm{std}(r)=0$ 的全对/全错组，slime 用 `--dynamic-sampling-filter-path`（如 `check_reward_nonzero_std`）+ `--over-sampling-batch-size`；半截走 `--partial-rollout`，旧 token 要 `--mask-offpolicy-in-partial-rollout` 或 `--use-tis`。截断过长、限制 `rollout.n` / `--n-samples-per-prompt` 也是减 KV，不是算法升级。验收时要一起看 tokens/s、stale 比例、zero-std 组比例和 eval，才能判断异步有没有带来有效收益。周报写生成占实际耗时多少、KV 峰值、stale 年龄分位数、zero-std 组比例、holdout；量化只动 sampling 副本，异步分清挪 `ray.get` 和 `train_async.py`，同卡部署时要说明训推难以同时运行。

## 追问

**量化、异步、过滤能不能一起开？**
能，但必须按瓶颈排序。显存爆先量化 sampling 副本；实际耗时被生成占满先换引擎和连续 batch；最长样本或工具等待再异步 / partial。三件一起开，分布偏移、stale、半截轨迹缠在一起，出了问题无法归因。面试先报当前占比再报开关。
**量化 logp 能进 ratio 吗？**
不能。FP8 SGLang 与 FSDP/Megatron 差千分位，$\rho$ 会漂，clip 变假。训练图重算仍必要；`--use-tis` 只修 sampling 分布隙，代替不了重算。BF16 训 + FP8 采是标准例子。
**挪 `ray.get` 算 fully-async 吗？**
不算。那一档仍按 `rollout_id` 切步，只是训推重叠。真正 fully-async 换 `train_async.py` + `generate_rollout_fully_async`，后台队列交组，必须管 trajectory age 和 TIS。
**`--colocate` 下异步有用吗？**
收益很小。`--offload-train` / `--offload-rollout` 让两边无法同时占 GPU，重叠窗口被物理削掉。要吃异步，先分卡。同卡部署时要说明训练和 sampling 实际能重叠多少。
**动态过滤是调温度吗？**
不是。温度管组内多样性；`--dynamic-sampling-filter-path`（如 `check_reward_nonzero_std`）管这组有没有可学信号。半截不是新的 on-policy token，要 mask 或 TIS。over-sample 只为滤完仍凑满 batch。
