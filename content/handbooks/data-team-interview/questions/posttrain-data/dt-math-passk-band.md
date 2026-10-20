---
id: dt-math-passk-band
section: posttrain-data
order: 2
level: S
title: 数学 SFT 题太简单或太难，数据侧怎么切难度带？
quick: "用当前学生每题采样 $k$ 次的成功数量划分难度。全部正确的少留，部分正确的用成功轨迹做 SFT；全部失败的先降难度或找教师帮助，RLVR 也需要模型有机会获得非零奖励。不能只按竞赛名称判断难度，还要防止背诵 GSM8K 改写题。"
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

让当前学生模型对每题生成 $k$ 个回答，比如 $k=8$ 或 $16$，再按正确数量分成三个难度区间。不能只按「AIME 难、GSM8K 易」判断，同一题库内的难度也有很大差异。

不这么选的理由：同一套 MATH 里有送分也有压轴。WizardMath / MetaMath 堆题面、不谈这一带，容易变成背 GSM8K 变体。换学生版本要重切，lineage 记 `student_ckpt`。STaR 吃「当前会做对」的轨迹；s1K 要难度门。R1 的 强化学习（RL） 题也不是随机小学算术。`dt-rejection-sample-code` 写过 $k$ 由 pass@$1$ 定，这张把它落到题库。

苹果：种子来自许可题和验证合成，不拿用户作业当题库。中间带对学生切，门禁另开，见 `dt-math-rewrite-leak`。

## 三带

- $n_{\text{ok}}=k$：太易。监督微调（SFT） 再灌会占预算，最多留几条格式示范。
- $0 < n_{\text{ok}} < k$：中间带。正例做 SFT，错的做偏好 lose 或 RL 负样本。
- $n_{\text{ok}}=0$：太难。不要硬留教师长 思维链（CoT，即分步推理过程）。降一档演化（少一步、给引理），或留给更强教师 / 解释器，见 `dt-math-tir-data`。

教师全对、学生全错：蒸馏可以，但要过 验证器（verifier），见 `dt-teacher-bias`。教师也全错：题或金标有问题，进 quarantine。

污染：中间带如果全是 GSM8K 改数字，门禁会虚高，见 `dt-math-rewrite-leak`。

## 追问

- **基于可验证奖励的强化学习（RLVR） 是不是专吃全错带？** 不全是。全错没有正向奖励，GRPO 组内全零。R1 / Tulu 仍要有一部分能偶然做对的题，见 `dt-rlvr-data`。
- **难度会不会训完就过时？** 会。每轮后训练重扫 pass@$k$，这就是飞轮，见 `dt-data-flywheel`。
- **端侧 3B 和 server 同一带？** 不是。小模型的中间带在大模型上可能是太易带。分学生切。
