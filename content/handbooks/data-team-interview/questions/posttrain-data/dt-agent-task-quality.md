---
id: dt-agent-task-quality
section: posttrain-data
order: 19
level: S
title: 怎么判断一条 agent 训练任务质量好不好？
quick: >-
  好任务要满足五条：参考修复让测试从失败变成通过，说明足够定位问题，测试考的正是说明里的要求，环境能从头复现，任务和评测隔开。题面像 issue
  还说明不了它能用；人审也只代表当时的质量，之后还要复查 contamination 和失效测试。
companies:
  - apple
tags:
  - Apple
  - Agent
  - Evaluation
  - SWE
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Introducing SWE-bench Verified
    url: 'https://openai.com/index/introducing-swe-bench-verified/'
    type: primary
  - title: SWE-bench
    url: 'https://arxiv.org/abs/2310.06770'
    type: primary
  - title: SWE-Gym
    url: 'https://arxiv.org/abs/2412.21139'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

好任务要有足够清楚的说明、能跑的环境，以及正好验证这些要求的测试。标准是一个人拿着这些材料能把任务做完；题面长得像 GitHub issue，还说明不了它能用。

举个例子，issue 只说「导出时日期格式不对」，测试却要求修复必须调用某个特定名字的函数。模型的修复功能上完全正确，只因为函数名不一样被判失败。测试和说明对不上时，RL 优化的就是错的目标。OpenAI 2024-08 人审放出 SWE-bench Verified 500 条，并按「15 分钟能修」和「一小时以上」evaluation slices，就是因为原版 SWE-bench 里有说明不足、测试范围不对、甚至不可解的题，这些题会让分数低估模型。

## 收任务时问的五个问题

先看有没有 fail-to-pass：reference patch 打上之前测试失败，打上之后通过。修复前后都通过，就没有修复信号；一直失败，要查环境或参考修复本身有没有问题。

再看说明够不够定位。如果 agent 只能去猜标识符名，这题就该滤掉（见 `dt-agent-rl-filter`），Verified 人审专门抓的就是 underspecified。

接着看测试是不是在考说明里的事。测得太宽，无关的回归会把正确修复拖死；测得太窄，改测试或硬编码也能过（见 `dt-swe-success-noise`）。

然后看环境能不能冷启动复现。Docker 和依赖都要锁住，只在某台机器上跑通，说明不了别人也能复现。最后确认和 held-out evaluation set 分开了，训练任务不能是 Verified 或 Pro 的 test。

人审过的题也会过期。OpenAI 后来把 Verified 里模型经常失败的子集重新审了一遍，发现一半以上测试过窄或过宽，而且这些题已经进了训练 corpus，最后连 Verified 都因 contamination 停报（见 `dt-agent-verified-stale`）。所以训练池要能按月更新，evaluation set 一旦被发现不可靠，也要能撤掉它作为发布检查的资格。

## 追问

**人审 500 条太贵怎么办？**
训练池用自动过滤（flaky、import 错误）加抽查，evaluation gate 才用真人。OpenAI 也把全部 test 的人工标注放出来了，方便按难度 evaluation slices。

**训练侧有没有用同一套标准的公开数据？**
有，SWE-Gym 用的就是这套：可执行仓库、单测、自然语言任务说明。没有测试的「agent 数据集」只是对话。

**网页或客服 agent 没有单测怎么办？**
用环境状态 assertion，也就是 τ-bench 那一套。说明不清的同样扔掉，见 `dt-tau-passk`。

**reference patch 必须唯一吗？**
不必。功能等价的补丁都应该能过测试。用和 reference patch 的 diff 相似度判好坏会 false rejection，见 `dt-agent-reward-spec`。
