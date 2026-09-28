---
id: meituan-grpo-stage-bottleneck
section: systems
order: 232
level: A
title: 美团二面：GRPO 哪个阶段最耗时？rollout 采样卡在哪？
quick: >-
  默认是 rollout：自回归 + 长 CoT + `rollout.n` 组采样，往往占墙钟 70%+。工具 / 沙箱一加入，环境等待会超过
  GPU decode。训练反向通常不是第一瓶颈，除非 70B+ 还在做频繁 all-gather。先画时间线再优化。
tags:
  - Meituan
  - GRPO
  - VeRL
  - Rollout
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型研发二面-日常实习
    url: https://www.nowcoder.com/feed/main/detail/23e19d8300c54f2eb9ed9933aeaa5129
    type: candidate-first-hand
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

## 真题记录

- 公司：美团
- 岗位：大模型研发；日常实习二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“grpo哪个阶段最耗时”**；**“rollout采样”**

错法：答成「训练反向最慢」或「先上 ZeRO-3」。我会把一步拆开计时：权重 reshard / `update_weights` → vLLM/SGLang 生成（含长尾序列）→ 训练图重算 logp → reward / verifier → advantage → actor backward。长推理任务里生成远大于 backward；Agent 任务里搜索 / 代码执行 RTT 会把 GPU 空转。7B 更容易 generation-bound；70B+ 的 all-gather / reshard 才会让 update 重新抬头。先画时间线再优化。字节有「rollout 长尾拖低 GPU」卡，本题问的是阶段归因。同场重算 logp 见 `meituan-verl-recompute-logprob`。

## 默认瓶颈在 rollout

自回归每步一个 token，反复读权重和 KV，memory-bound。veRL `actor_rollout_ref.rollout.n`、slime `--n-samples-per-prompt` 把同一 prompt 乘 $n$ 条；长 CoT 再乘长度。墙钟 70%+ 在生成很正常，不要用预训练 MFU 来骂这段，见 `infra-rl-mfu-6nd`。采样卡在哪要再拆：

- 引擎调度：静态 batch 被最长序列拖死；上 continuous batching、prefix cache。
- 长度长尾：一组里一条 8k、一条 200，padding 或不 abort 会空转。DAPO 动态过滤、截断、`--partial-rollout` 回收半截。
- 环境等待：工具 / 沙箱 RTT 超过 GPU decode。这时加卡没用，要并行工具、超时、fully-async 队列交组。

不要先上 ZeRO-3 幻想加速生成。分片救的是更新侧参数，不救 decode。

## 其他段各占什么

权重同步：HybridEngine reshard 或 slime `update_weights`，同卡 IPC 快、磁盘慢，见 `infra-rl-weight-sync`。重算 logp：一次训练图前向，micro-batch 小，利用率一般，但是数学必要，省不掉。reward：规则便宜，模型 verifier 或沙箱可能变第二瓶颈。advantage：组内统计，CPU 可忽略。actor backward：才是 $6ND$，7B 上通常短于生成；70B + 频繁 all-gather 才会反超。`--colocate` 下 offload 拷贝气泡要单独计，不要算进 decode。

优化顺序跟占比走：generation-bound → 换引擎、连续 batch、减 $n$/长度、动态过滤、异步。env-bound → 工具并行和超时。update-bound → 并行策略、少切布局。验收看分段墙钟，不看「开了 FSDP」。

## 采样侧具体开关

veRL：`rollout.n`、引擎 vLLM/SGLang、DAPO recipe、fully async staleness。slime：`--n-samples-per-prompt`、`--dynamic-sampling-filter-path`、`--partial-rollout`、挪 `ray.get` vs `train_async.py`。半截旧 token 要 mask 或 `--use-tis`。

## 追问

- **为什么不是 backward？** 7B 长 CoT 下自回归 decode 占墙钟大头，memory-bound，MFU 看起来差是负载变了。backward 吃显存，但不一定吃时间。70B + 频繁 all-gather 才要重新 profile update。
- **ZeRO-3 能加速采样吗？** 不能。它切训练参数、换 all-gather。采样要 vLLM/SGLang、continuous batching、截断长尾。先上 ZeRO-3 幻想加速生成是这题的标准错答。
- **工具任务瓶颈还在 GPU 吗？** 常常不是。搜索和代码沙箱 RTT 会让 GPU 空转。这时加卡浪费，应并行工具、设超时，并用 `train_async.py` 让已完成组先训。
- **长尾怎么砍？** 连续 batch 避免陪跑；abort 过长；`--dynamic-sampling-filter-path` 丢掉零方差组；`--partial-rollout` 回收半截并用 mask/TIS 处理旧 token。见 `byte-grpo-rollout-tail-gpu`。
- **和显存那题怎么分？** 本题是墙钟归因；`meituan-grpo-7b-mem` 是峰值显存。KV 同时是显存和采样时间的来源，减 `rollout.n` 两边都赚。重算 logp 是必要前向，通常不是第一瓶颈。
