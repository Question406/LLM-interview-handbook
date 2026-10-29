---
id: afm-ref-skill-flywheel
section: projects
order: 3
level: S
title: 个人 Reference 3：Skill Usage，如何从评测失败构造 self-improvement feedback loop？
quick: 我会从 skill 没有帮上忙的一次失败讲起，先找到失败发生在哪，再决定修 skill、补选择数据，还是训练适配能力。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Jiabao Ji
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: How Well Do Agentic Skills Work in the Wild — v1
    url: 'https://arxiv.org/html/2604.04323v1'
    type: primary
  - title: SkillsBench — official repository
    url: 'https://github.com/benchflow-ai/skillsbench'
    type: primary
---

## 面试官可能这样问

你会怎么用模型失败推动下一轮数据改进？

## 可以这样回答

我会用 skill 的例子。给 agent 一条写得很好的 skill，它做得更好了，这还不能说明真实使用时也会更好，因为真实情况下它首先得找到这条 skill，还得判断什么时候用。

我们在相关研究里看了更接近这种使用方式的设置。对数据迭代来说，我会把任务失败和 skill 使用过程放在一起看。相关 skill 没找到，就先查检索；找到了却没用，要看选择；用了还是失败，再看它缺什么步骤，或者是不是没有适配当前任务。

下一轮我会围绕那个具体问题补数据，再换一批任务验证。这里也要分清两件事：把 skill 文件改得更好，是运行时改进；让模型本身学会选择和适配，需要另外的训练实验。我不会把前者的收益直接算成后者的证据。

## 被追问时再展开

**什么时候值得训进模型？** 当同一种行为在很多任务里反复有用，而且外部 skill 已经很清楚、模型仍然不会用时，我会考虑训练。经常变化的知识则可能更适合继续放在 skill 里。

## 技术备查

## 已核对的相关研究
[Skill Usage 研究](https://arxiv.org/html/2604.04323v1) 在 SkillsBench 上逐步引入干扰、检索和移除定制技能，并测试 refinement；论文还在 Terminal-Bench 2.0检验迁移。这里的运行时 skill 更新不是自动等于模型权重 self-training。

## 对照材料与版本
[SkillsBench 官方仓库](https://github.com/benchflow-ai/skillsbench) 用于理解任务与技能评测接口。Terminal-Bench 相关讨论以你论文的2.0设定为准，不混报旧版、不同 harness 或新排行榜。先读论文§3.3、§4，再追对应数据版本。

## 可讲的飞轮 setting（建议扩展）
任务输入→检索 skill→选择加载→执行→独立状态检查→归类失败→修订 skill→新任务验证。日志至少记 task_family、skill_id/version、retrieved_rank、loaded、tool-use trajectories、终局状态和运行预算。没有加载、检索不到和加载后不会用是不同的数据干预对象。

设计四个受控分支：no-skill、oracle 相关 skill、真实检索、真实检索＋refinement。固定模型与总预算，分别记录召回、加载、任务成功、耗时和 token。强制加载只是诊断上界，不是部署方案。若 oracle skill 也无收益，应先看内容和执行能力，不能继续只优化 retriever。

训练扩展需将改进保留到独立任务家族，保存失败与有效恢复片段，过滤任务答案 leakage。只有反复有用、压缩后可迁移的行为才考虑 SFT 或 RL；项目特有且会变化的知识可以留在外部 skill。预先设成本、跨任务收益和回归的停止条件。这是建议，不声称你论文已完成整个训练飞轮。

## 英文60秒参考
> A useful example is our work on skill usage under more realistic retrieval conditions. I would separate finding a relevant skill, deciding to load it, and adapting its content to the task. That makes the intervention testable: improving retrieval will not fix an execution bottleneck. The next step I would propose is to collect verified recovery trajectories and test whether the benefit transfers to new task families. I would distinguish runtime skill refinement from updating the model weights, because they change different parts of the system.

## 高频追问与回答方向
**skill load 率上涨就是模型更强？** 不一定，可能浪费 context；以独立任务成功和预算为目标。
**query-specific refinement 是否 leakage？** 利用当前指令本身不必然 leakage，使用隐藏答案、测试结果反复定制才有问题；训练型结论还要新任务验证。
**如何接 See Around Corners？** 可以讲为何理想化提供 skill 不能代表真实检索；若称提前发现产品风险，要补当时证据。
**与数据选择有什么关系？** 选择缺口决定采什么 trajectories，失败分层也决定是否值得再生更多同类 skill。

继续练 `dt-data-flywheel`、`dt-self-improve`、`dt-curriculum-moving-target`。

