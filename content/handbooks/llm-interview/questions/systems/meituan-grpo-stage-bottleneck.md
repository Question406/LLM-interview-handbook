---
id: meituan-grpo-stage-bottleneck
section: systems
order: 232
level: A
title: 美团二面：GRPO 哪个阶段最耗时？rollout sampling 卡在哪？
quick: >-
  长 CoT 的 GRPO 通常在 rollout 上花最多时间：每题 sampling $n$ 条回答，autoregressive 生成要逐 token
  读权重和 KV，可能占实际耗时 70% 以上。工具或沙箱任务还可能主要慢在环境等待；我会分别计时权重同步、生成、重算 logp、奖励和
  backward，再按占比优化。
tags:
  - Meituan
  - GRPO
  - VeRL
  - Rollout
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 美团大模型研发二面-日常实习
    url: 'https://www.nowcoder.com/feed/main/detail/23e19d8300c54f2eb9ed9933aeaa5129'
    type: candidate-first-hand
  - title: verl
    url: 'https://github.com/verl-project/verl'
    type: primary
---

## 可以这样回答

长推理任务的 GRPO 通常最耗时的是 rollout，但我会用分段计时确认。比如一题要生成 $n$ 条长回答，每条都得逐 token decoding；如果还要搜索或执行代码，工具 RTT 又可能让 GPU 等着。7B 更容易受生成限制，70B+ 则要重新看 all-gather 和 reshard 的占比。

我会把一步画成权重 reshard / `update_weights`、vLLM/SGLang 生成、训练图重算 logp、奖励计算 / 验证器、advantage 和 actor backward。这个时间线先区分生成、环境和更新各占多少，再选优化方法。重算 logp 的原因见 `meituan-verl-recompute-logprob`。

## 技术备查

## 真题记录

- 公司：美团
- 岗位：大模型研发；日常实习二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“grpo 哪个阶段最耗时”**；**“rollout sampling”**

长推理任务的 GRPO 通常最耗时的是 rollout，但我会用分段计时确认。比如一题要生成 $n$ 条长回答，每条都得逐 token decoding；如果还要搜索或执行代码，工具 RTT 又可能让 GPU 等着。7B 更容易受生成限制，70B+ 则要重新看 all-gather 和 reshard 的占比。

我会把一步画成权重 reshard / `update_weights`、vLLM/SGLang 生成、训练图重算 logp、奖励计算 / 验证器、advantage 和 actor backward。这个时间线先区分生成、环境和更新各占多少，再选优化方法。重算 logp 的原因见 `meituan-verl-recompute-logprob`。

## 默认瓶颈在轨迹 sampling（rollout）

autoregressive 每步生成一个 token，反复读权重和 KV，memory-bound。veRL `actor_rollout_ref.rollout.n`、slime `--n-samples-per-prompt` 把同一 prompt 生成 $n$ 条回答；长 CoT 又增加每条回答的长度。实际耗时 70%+ 在生成很正常，不要按预训练的 MFU 标准判断这段负载是否正常，见 `infra-rl-mfu-6nd`。sampling 卡在哪要再拆：

- 引擎调度：静态 batch 被最长序列拖死；上 continuous batching、prefix cache。
- 长度长尾：一组里一条 8k、一条 200，padding 或不 abort 会空转。DAPO 动态过滤、截断、`--partial-rollout` 回收半截。
- 环境等待：工具 / 沙箱 RTT 超过 GPU 的逐 token 生成（decode）。这时加卡没用，要并行工具、超时、fully-async 队列交组。

ZeRO-3 切分的是更新侧参数，decode 的耗时还要靠 sampling 引擎和调度解决。

## 其他阶段也要单独计时

权重同步：HybridEngine reshard 或 slime `update_weights`，同卡 IPC 快、磁盘慢，见 `infra-rl-weight-sync`。重算 logp：一次训练图前向，micro-batch 小，利用率一般，但是数学必要，省不掉。reward：规则便宜，模型 verifier 或沙箱可能变第二瓶颈。advantage：组内统计，CPU 可忽略。actor backward：才是 $6ND$，7B 上通常短于生成；70B + 频繁 all-gather 才会反超。`--colocate` 下 offload 拷贝气泡要单独计，不要算进 decode。

优化顺序跟占比走：generation-bound → 换引擎、连续 batch、减 $n$/长度、动态过滤、异步。env-bound → 工具并行和超时。update-bound → 并行策略、少切布局。验收时比较各阶段实际耗时，才能确认资源是否用在了瓶颈上。



veRL：`rollout.n`、引擎 vLLM/SGLang、DAPO recipe、fully async staleness。slime：`--n-samples-per-prompt`、`--dynamic-sampling-filter-path`、`--partial-rollout`、挪 `ray.get` vs `train_async.py`。半截旧 token 要 mask 或 `--use-tis`。

## 追问

**为什么不是 backward？**
7B 长 CoT 下 autoregressive decode 占实际耗时大头，memory-bound，MFU 看起来差是负载变了。backward 吃显存，但不一定吃时间。70B + 频繁 all-gather 才要重新 profile update。
**ZeRO-3 能加速 sampling 吗？**
不能。它切训练参数、换 all-gather。sampling 要 vLLM/SGLang、continuous batching、截断长尾。生成阶段应单独优化。
**工具任务瓶颈还在 GPU 吗？**
常常不是。搜索和代码沙箱 RTT 会让 GPU 空转。这时加卡浪费，应并行工具、设超时，并用 `train_async.py` 让已完成组先训。
**长尾怎么砍？**
连续 batch 避免陪跑；abort 过长；`--dynamic-sampling-filter-path` 丢掉零方差组；`--partial-rollout` 回收半截并用 mask/TIS 处理旧 token。见 `byte-grpo-rollout-tail-gpu`。
**和显存那题怎么分？**
本题是实际耗时归因；`meituan-grpo-7b-mem` 是峰值显存。KV 同时是显存和 sampling 时间的来源，减 `rollout.n` 两边都赚。重算 logp 是必要前向，通常不是第一瓶颈。
