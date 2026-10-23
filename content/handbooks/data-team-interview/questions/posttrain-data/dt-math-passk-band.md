---
id: dt-math-passk-band
section: posttrain-data
order: 2
level: S
title: 数学 SFT 题太简单或太难，数据侧怎么切难度带？
quick: "按当前学生模型每题采样 $k$ 次、做对几次来切，竞赛名称只能粗分。全对的太易少留；部分对的是中间带，成功轨迹做 SFT、错的做负样本；全错的先降难度或找教师 / 解释器，RLVR 也需要模型有机会拿到非零奖励。换学生要重切，还要防止中间带被 GSM8K 改写题填满。"
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
updatedAt: 2026-10-12
sources:
  - title: "STaR: Bootstrapping Reasoning With Reasoning"
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: "s1: Simple test-time scaling"
    url: https://arxiv.org/abs/2501.19393
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

按当前学生模型来切：每道题让它生成 $k$ 个回答，比如 $k=8$ 或 $16$，按做对的个数分成三个难度带。「AIME 难、GSM8K 易」只是粗分，同一套 MATH 里既有送分题也有压轴题。

难度要看学生，是因为同一道题对不同模型的价值不一样。学生每次都做对的题，再训也学不到什么；一次都做不对的题，给它看答案它也接不住。WizardMath / MetaMath 这类做法只管堆题面、不谈难度带，容易变成背 GSM8K 的变体。公开配方都在挑对学生有用的那一段：STaR 用的是「当前模型会做对」的轨迹，s1K 设了难度门，R1 的强化学习（RL）题也不是随机的小学算术。也因为难度相对于学生，换了学生版本就要重新切，lineage 里记下 `student_ckpt`。

## 三个难度带怎么处理

全对的（$n_{\text{ok}}=k$）太易，再拿去做监督微调（SFT）只会占预算，最多留几条当格式示范。

部分对的（$0 < n_{\text{ok}} < k$）是中间带，最有用。做对的回答当 SFT 正例，做错的当偏好数据里的 lose 或 RL 负样本。

全错的（$n_{\text{ok}}=0$）太难，别硬塞教师的长思维链（CoT，即分步推理过程）。可以降一档重新演化（少一步、给出引理），或者交给更强的教师或解释器，见 `dt-math-tir-data`。全错带里还要再看教师：教师全对、学生全错，可以蒸馏，但教师答案要先过验证器（verifier），见 `dt-teacher-bias`；教师也全错，多半是题目或金标答案有问题，放进 quarantine。

切完之后查一遍污染。中间带如果全是 GSM8K 改个数字，门禁成绩会虚高，见 `dt-math-rewrite-leak`。

## 追问

**基于可验证奖励的强化学习（RLVR）是不是专吃全错带？**
不是。全错的题没有正向奖励，GRPO 一组全是零，学不到东西。R1 / Tulu 仍然要有一部分模型能偶尔做对的题，见 `dt-rlvr-data`。

**$k$ 取多大？**
由学生的 pass@$1$ 决定，`dt-rejection-sample-code` 里讲过怎么定，这张卡只是把它落到题库上。

**难度会不会训完就过时？**
会。每轮后训练后重新扫一遍 pass@$k$，这就是数据飞轮，见 `dt-data-flywheel`。

**小模型和大模型用同一套难度带吗？**
不用。小模型的中间带，在大模型上可能已经是太易带，要按学生分别切。

相关：`dt-math-tir-data`、`dt-teacher-bias`、`dt-math-rewrite-leak`、`dt-rlvr-data`
