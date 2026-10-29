---
id: dt-math-passk-band
section: posttrain-data
order: 2
level: S
title: 数学 SFT 题太简单或太难，数据侧怎么切 difficulty band？
quick: >-
  按当前 student model 每题 sampling $k$ 次、做对几次来切，竞赛名称只能粗分。全对的太易少留；部分对的是中间带，成功
  trajectories 做 SFT、错的做负样本；全错的先降难度或找 teacher / 解释器，RLVR 也需要模型有机会拿到非零奖励。换
  student 要重切，还要防止中间带被 GSM8K 改写题填满。
companies:
  - apple
tags:
  - Apple
  - Math
  - SFT
  - Difficulty
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'STaR: Bootstrapping Reasoning With Reasoning'
    url: 'https://arxiv.org/abs/2203.14465'
    type: primary
  - title: 's1: Simple test-time scaling'
    url: 'https://arxiv.org/abs/2501.19393'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

按当前 student model 来切：每道题让它生成 $k$ 个回答，比如 $k=8$ 或 $16$，按做对的个数分成三个 difficulty band。「AIME 难、GSM8K 易」只是粗分，同一套 MATH 里既有送分题也有压轴题。

难度要看 student，是因为同一道题对不同模型的价值不一样。student 每次都做对的题，再训也学不到什么；一次都做不对的题，给它看答案它也接不住。WizardMath / MetaMath 这类做法只管堆题面、不谈 difficulty band，容易变成背 GSM8K 的变体。公开配方都在挑对 student 有用的那一段：STaR 用的是「当前模型会做对」的 trajectories，s1K 设了难度门，R1 的 RL 题也不是随机的小学算术。也因为难度相对于 student，换了 student 版本就要重新切，lineage 里记下 `student_ckpt`。

## 三个 difficulty band 怎么处理

全对的（$n_{\text{ok}}=k$）太易，再拿去做 SFT 只会占预算，最多留几条当格式示范。

部分对的（$0 < n_{\text{ok}} < k$）是中间带，最有用。做对的回答当 SFT 正例，做错的当 preference data 里的 lose 或 RL 负样本。

全错的（$n_{\text{ok}}=0$）太难，别硬塞 teacher 的长 chain of thought（CoT，即分步推理过程）。可以降一档重新演化（少一步、给出引理），或者交给更强的 teacher 或解释器，见 `dt-math-tir-data`。全错带里还要再看 teacher：teacher 全对、student 全错，可以 distillation，但 teacher 答案要先过 verifier（verifier），见 `dt-teacher-bias`；teacher 也全错，多半是题目或 gold labels 答案有问题，放进 quarantine。

切完之后查一遍 contamination。中间带如果全是 GSM8K 改个数字，held-out evaluation scores 会虚高，见 `dt-math-rewrite-leak`。

## 追问

**基于 verifiable reward 的 RL（RLVR）是不是专吃全错带？**
不是。全错的题没有正向奖励，GRPO 一组全是零，学不到东西。R1 / Tulu 仍然要有一部分模型能偶尔做对的题，见 `dt-rlvr-data`。

**$k$ 取多大？**
由 student 的 pass@$1$ 决定，`dt-rejection-sample-code` 里讲过怎么定，这张卡只是把它落到题库上。

**难度会不会训完就过时？**
会。每轮 post-training 后重新扫一遍 pass@$k$，这就是 data flywheel，见 `dt-data-flywheel`。

**small model 和 large model 用同一套 difficulty band 吗？**
不用。small model 的中间带，在 large model 上可能已经是太易带，要按 student 分别切。

相关：`dt-math-tir-data`、`dt-teacher-bias`、`dt-math-rewrite-leak`、`dt-rlvr-data`
