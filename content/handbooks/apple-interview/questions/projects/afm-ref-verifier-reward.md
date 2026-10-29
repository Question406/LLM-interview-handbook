---
id: afm-ref-verifier-reward
section: projects
order: 2
level: S
title: 个人 Reference 2：HarnessLLM／HardTestGen，奖励错了比模型弱更危险？
quick: 我最直接的经验连接是代码验证：一个可重复运行的测试也会漏掉错误。如果模型一直优化这种反馈，就可能学会利用测试的盲点。
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
  - title: HarnessLLM — public paper v1
    url: 'https://arxiv.org/html/2511.01104v1'
    type: primary
  - title: HARDTESTGEN — ICLR 2026 proceedings
    url: >-
      https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf
    type: primary
  - title: 'EvalPlus: rigorous evaluation of generated code'
    url: 'https://arxiv.org/abs/2305.01210'
    type: primary
  - title: LiveCodeBench — original benchmark paper
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
---

## 面试官可能这样问

你没有独立负责过 learned RM，怎么理解 reward modeling 里的数据问题？

## 可以这样回答

我比较直接的连接是代码验证。在我参与的测试生成研究里，我们关心的是：一个程序看起来能通过测试，它到底是不是真的正确？因为测试一旦漏掉某类错误，这些错误程序就可能被选进 training set，或者在 RL 里拿到正奖励。

我觉得这和 learned RM 有一个共同点：模型得到的是评审器的判断，而这个判断可能和我们真正想要的质量有差距。代码里可能是漏了长链这种 edge-case inputs，preference model 里可能是把回答长、语气自信当成质量好。

所以我会先看评审器在哪些样本上容易错，再决定补什么标签。然后用另一套独立检查验证模型有没有变好。我没有负责过生产级 preference model 的话，会直接说明这一点；我能深入讲的是验证反馈怎么影响数据选择和优化。

## 被追问时再展开

**那两种奖励能直接互换吗？** 不能。代码测试对应一个明确的功能要求；preference labels 还涉及谁来评、按什么标准评，以及分歧怎么处理。共同的问题是反馈可靠性，具体标签和验证办法仍然不同。

## 技术备查

## 已核对的相关研究
[HarnessLLM](https://arxiv.org/html/2511.01104v1) 生成可执行测试 harness，使用 SFT 和 RLVR；[HARDTESTGEN](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf) 构造更可靠的算法代码测试。两篇公开作者名单包含你，个人模块仍待确认。后者使用的 LiveCodeBench-105为特定版本的 C++标准输入输出子集，不能当作整个 LiveCodeBench。

## 最相关的对照资料
[EvalPlus](https://arxiv.org/abs/2305.01210) 展示扩充测试可以揭露原测试未发现的错误；[LiveCodeBench](https://arxiv.org/abs/2403.07974) 的时间化题目采集帮助讨论 contamination。时间较新不等于绝对无 contamination，运行时必须固定版本、时间窗和语言。

## 一个可深入的 setting（建议实验）
固定题库、候选代码、生成模型和预算；每题同时保存可信实现、多个错误算法和有效输入约束。对比随机测试、LLM 输入输出测试和 harness，区分无效输入、错误 oracle、false rejection 正确程序与 false acceptance 错误程序。

假设任务求树上路径长度：随机平衡树可能放过在链状树上超时的低效算法。困难测试要覆盖约束内的对抗结构，而非单纯变大。CPU 超时、编译器、运行 seed 和 sandbox 版本必须固定；资源问题不能混成逻辑错误。

用独立人工测试/可信实现建立审计标签，报告“判通过中真正正确的比例”和“错误程序被抓住的比例”，写清正负类定义。训练实验保持相同题、token 和算力，只替换 verifier，再比较独立代码生成质量；不要用训练奖励涨证明成功。评审器不完美时可设置弃权/专家复核，但阈值只用 development set 选。

## 英文60秒参考
> My connection to reward modeling is strongest through executable verification. In work I coauthored on test generation, the central issue is whether the feedback distinguishes correct programs from convincing wrong ones. This matters twice: it selects synthetic training data and it defines the optimization signal. To isolate verifier quality, I would hold the problems and candidate programs fixed, audit both false acceptance and false rejection, and then evaluate downstream learning independently. A learned preference model adds further concerns about annotators, calibration, and distribution shift.

## 高频追问与回答方向
**rule-based reward 不是客观的吗？** 执行可重复不意味着测试完整；测试契约、oracle 和资源限制同样可能有偏。
**和 learned RM 有何差别？** 执行标签针对定义的功能契约，learned RM 还拟合人类偏好；两者共同风险是优化者利用代理漏洞。
**模型改了自己的测试后通过了？** 测试与训练程序权限隔离，独立隐藏评价不可由策略修改；变更测试必须重新审计。
**如果所有 trajectories 都0或1？** 先判断任务难度与 verifier 覆盖，组内无相对信号时调整课程或冷启动，而非无条件放宽正确性。

继续练 `afm-rm-bestofn-overoptimization`、`afm-rm-prm-credit`、`dt-verifier-counterfactual`。

