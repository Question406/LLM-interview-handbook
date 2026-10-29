---
id: byte-grpo-rollout-tail-gpu
section: systems
order: 100
level: S
title: 字节 27 暑期：GRPO rollout 长尾拖低 GPU 利用率，工程上怎么解？
quick: >-
  我会把问题拆成生成、调度、训练三段处理：连续 / 动态 batching、按长度分组、每组完成就送训、截断和预算控制、异步 actor-learner
  解耦。异步会引入旧策略，所以要盯住 policy freshness，别靠堆并发把 off-policy 盖过去。
tags:
  - ByteDance
  - 2027 Summer Intern
  - GRPO
  - RL Infrastructure
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节27暑期 大模型算法一面凉经分享（候选人原帖）
    url: >-
      https://www.nowcoder.com/feed/main/detail/28b254940eb940189188d795f4606c52?urlSource=home-api
    type: candidate-first-hand
  - title: vLLM
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary-paper
---

## 真题记录

- 公司：字节跳动
- 团队 / 岗位：大模型算法
- 届别 / 流程：27 届暑期实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GRPO 中 roll out 过程的长尾问题，导致 GPU 使用率低，有什么工程上的解决方案”**

我会先测量尾部是谁，再从调度入手：连续 batching、按长度分组、组完成就送训、加预算和可审计的截断，最后才上异步 actor-learner，并且管住 policy freshness。直接「加大并发」或「把 max_len 砍短」都不够。问题的根源是 GRPO 的一个 group 要等最慢的那条样本，等的时候 generation worker 空转，padding 变厚，learner 也出现 bubble。

先测量。收集生成长度的分布、工具等待时间、拒答和 retry 的比例，以及每张 GPU 的 idle。长尾分两种：一种是模型 decode 的长尾，少数超长的 chain of thought（CoT，即分步推理过程）拖住整组；另一种是环境的长尾，搜索或沙箱超时。比如一组里其他回答很快就结束了，只剩一条一直在想，整组都得陪着等，这是前一种。前一种靠分组、预算和连续 batch；后一种靠并发可交换的 action、超时和缓存。没看到直方图之前，别急着改 `max_new_tokens`。

调度上能做的有几件。按长度 packing 或分组，避免为一条长样本 pad 整组。推理引擎用连续 batching，结束的请求立刻让位。加 token 或时间预算，配上可审计的截断，避免模型无限地想。已经完成的 group 尽早做后处理、算优势、进 learner，不用等全局 step 里最慢的那个 bucket。工具型任务里，幂等的查询做缓存，可交换的工具并行调。这些都能抬高 GPU 的有效 token，但截断会改变奖励分布，日志里要打标。

再往后是异步。actor 和 learner 解耦、backlog 设上限，能把 bubble 盖住，代价是 sampling 轨迹（rollout）用的是旧权重。所以要记录 policy version、age 分布、有效样本比例和 holdout，超过 freshness 阈值的样本丢掉，或者做受控修正（IS / TIS）。用过 slime 的话可以落到开关上：`--partial-rollout` 加 abort 回收半成品；长尾 Agent 换 `train_async.py` / `generate_rollout_fully_async`；旧 prefix 用 `--mask-offpolicy-in-partial-rollout` 或 `--use-tis` 处理，见 `sys-staleness`、`slime-async-train`。

## 追问

**只砍 max_len 行不行？**
能压尾部，但可能砍掉本来能解出来的轨迹，奖励分数（reward）会失真。要做成可审计的截断，并且看 holdout。

**连续 batch 为什么有用？**
decode 过程中短请求一结束，马上填进新请求，减少为长尾 pad 出来的空算力。

**partial rollout 怎么保证正确？**
半成品要做 mask 或修正，否则就是拿过期的 prefix 去训当前策略。

**怎么证明 GPU 利用率真的变好了？**
看 tokens/s、idle 时间、group 完成时间的 P99，瞬时的 SM% 说明不了问题。

相关：`infra-rl-rollout-optimize`、`slime-dynamic-partial`、`sys-cont-batch`
