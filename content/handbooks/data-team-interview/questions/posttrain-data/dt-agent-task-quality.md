---
id: dt-agent-task-quality
section: posttrain-data
order: 19
level: S
title: 怎么判断一条 agent 任务是好任务，而不是「看起来像 GitHub issue」？
quick: "收工程任务时检查：参考修复是否让测试从失败变为通过，说明是否充分，测试是否对应要求，环境是否能从头复现，以及任务是否与评测隔离。人审只说明当时的质量，后续还要复查污染和失效测试。"
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
updatedAt: 2026-10-12
sources:
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: primary
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: SWE-Gym
    url: https://arxiv.org/abs/2412.21139
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

好任务要有足够清楚的说明、可运行的环境，以及能验证要求的测试。人应能根据这些材料完成任务；题面长得像 issue，还不足以证明它可用。

常见误区是：题面像 GitHub issue 就收进池。如果测试与说明不一致，RL 优化的就是错误目标。公开配方里 OpenAI 2024-08 做人审放出 Verified 500 条，并按「15 分钟能修 / 一小时以上」切片，就是因为原版 SWE-bench 里有说明不足、测试范围不对、甚至不可解的题，分数会低估模型。

## 现场五问

1. Fail-to-pass 有没有。金补丁打上之前测失败、之后通过。修复前后始终通过，就没有修复信号；始终失败则要检查环境或参考修复是否有问题。
2. 说明够不够定位。agent 只能猜标识符名的，见 `dt-agent-rl-filter`。Verified 人审专门抓 underspecified。
3. 测试是不是在考说明里的事。测太宽：无关回归拖死。测太窄：改测试或硬编码也能过，见 `dt-swe-success-noise`。
4. 环境能不能冷启动复现。Docker / 依赖锁住。只在某台本机跑通过，不能证明别人能复现。
5. 和门禁切开了吗。训练任务不能是 Verified / Pro 的 test。OpenAI 后来连 Verified 都因污染停报，见 `dt-agent-verified-stale`。

SWE-Gym 把同一套标准用到训练侧：可执行仓库 + 单测 + 自然语言任务。没有测试的「agent 数据集」只是对话。

人审过一次不等于永远好。OpenAI 后来对 Verified 里模型常挂的子集再审，一半以上测试过窄或过宽，而且题进了训练语料，见 `dt-agent-verified-stale`。训练池需要支持按月更新，发现评测不可靠时也要能撤销它作为发布检查的资格。

苹果：许可仓库或合成仓库，同样过这五问。用户工单默认不进基础模型，也不能拿「看起来像 issue」当训练题。

## 追问

- **人审 500 条太贵？** 训练池我会用自动过滤（flaky、import 错误）加抽查。门禁用真人。OpenAI 把全部 test 的人标也放出来，方便按难度切片。
- **网页 / 客服 agent 没有单测？** 我会用环境状态断言，τ-bench 那套。说明不清同样扔掉，见 `dt-tau-passk`。
- **金补丁必须唯一？** 不必须。功能等价的补丁应该过测试。用和金补丁的 diff 相似度当好坏，会误杀，见 `dt-agent-reward-spec`。
