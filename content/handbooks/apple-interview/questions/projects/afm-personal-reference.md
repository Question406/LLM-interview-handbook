---
id: afm-personal-reference
section: projects
order: 0
level: S
title: Jiabao Ji × AFM：个人研究、Benchmark 与面试 Reference
quick: >-
  主线用 DeepAmbigQA 谈合成与完整性，用 HarnessLLM/HardTestGen 谈奖励可靠性，用 Skill
  Usage/VisualSkill 谈 feedback loop 与 multimodal，再接工具
  RL、效率和遗忘评测。公开团队成果、个人职责和建议实验分开表述。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Jiabao Ji
  - AFM 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Jiabao Ji — personal homepage
    url: 'https://question406.github.io/'
    type: primary
  - title: Jiabao Ji — public CV
    url: 'https://question406.github.io/assets/cv/cv.pdf'
    type: primary
  - title: DeepAmbigQA — public paper v1
    url: 'https://arxiv.org/html/2511.01323v1'
    type: primary
  - title: HarnessLLM — public paper v1
    url: 'https://arxiv.org/html/2511.01104v1'
    type: primary
  - title: HARDTESTGEN — ICLR 2026 proceedings
    url: >-
      https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf
    type: primary
  - title: How Well Do Agentic Skills Work in the Wild — v1
    url: 'https://arxiv.org/html/2604.04323v1'
    type: primary
  - title: Speculate While You Reason — v1
    url: 'https://arxiv.org/html/2607.25816v1'
    type: primary
  - title: VisualSkill — v1
    url: 'https://arxiv.org/html/2606.18448v1'
    type: primary
  - title: Reversing the Forget-Retain Objectives — v1
    url: 'https://arxiv.org/html/2406.08607v1'
    type: primary
  - title: Apple Foundation Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 这份 reference 怎么用
基于2026-10-27核对的[主页](https://question406.github.io/)、公开 CV 和论文。这里的“我参与的工作”仅表示公开作者身份；“我具体负责什么”仍须你确认，不能从作者顺序推断。英文段落是面试参考表达。建议实验均是待做方案，不是已获得的结果。

你的匹配点是把一个能力缺口变成可验证的任务、数据与反馈。无需将自己包装成已经负责过整套大规模 AFM pre-training 平台的人。

## 最值得准备的六条线
| 优先级 | 相关公开研究 | 熟悉/可对照的 benchmark 或 setting | AFM 话题 | 深读入口 |
| --- | --- | --- | --- | --- |
| 1 | DeepAmbigQA | 自己的多跳歧义 QA；AmbigQA / ASQA / MuSiQue 作对照 | synthetic data、完整性、评测驱动诊断 | `afm-ref-qa-completeness` |
| 2 | HarnessLLM / HARDTESTGEN | 错误程序识别；LiveCodeBench、EvalPlus；固定题换 verifier | RL 奖励质量、verifier 盲点、困难负例 | `afm-ref-verifier-reward` |
| 3 | Skill Usage | SkillsBench 的递进检索设定；论文中的 Terminal-Bench 2.0实验 | 失败诊断、skill refinement、self-iteration | `afm-ref-skill-flywheel` |
| 4 | Speculate While You Reason | 部分 trajectories 预测下次调用；搜索 QA 和 tau-bench；tau2作扩展 | on-policy 训练信号、proxy reward、成本 | `afm-ref-joint-tool-rl` |
| 5 | VisualSkill | CUA-World / OSExpert-Eval；OSWorld 作跨模型补充 | multimodal 数据、对照实验、judge bias | `afm-ref-visual-setting` |
| 6 | ULD unlearning | TOFU 的 forget/retain；移除后的效用与再提取 | 治理、遗忘与保留权衡 | `afm-ref-unlearning-governance` |

列出的外部 benchmark 不等于你亲自运行过；每张卡会标明论文实际使用与建议扩展。先练前三条，再按面试官问题调用其余材料。

## 60秒总开场参考
> My research connects agent capability gaps with better supervision and evaluation. I have coauthored work on ambiguous multi-hop QA, executable verification, and agent skills. For this role, I would focus on how we define a failure precisely, construct verifiable examples, and check that improvements transfer beyond the data generator or evaluator. I am especially interested in turning failures into training signals while keeping evaluation independent. My direct experience is strongest in research settings; applying these ideas to a large-scale production data pipeline would be a next step.

这里没有声称你主导了每篇合作论文，也没有声称已有生产飞轮经历。追问具体责任时补一句 “My specific contribution was [真实职责]”，说出可展示的实验或代码。

## 原始面试要求怎样接
- **synthetic data 具体案例**：从 DeepAmbigQA 开场，讲任务可验证性与完整性，再讨论训练扩展；不能把 benchmark 合成直接当作已完成 SFT 收益。
- **benchmark debugging**：使用 QA 的漏分支，或 verifier 放过错误程序，给区分假设的 controlled substitution。
- **data flywheel / self-improvement**：用技能选择与 refinement 说明运行时迭代，再解释何时值得转成权重训练。
- **reward / preference**：以 verifiable reward 为实际研究案例，补 learned RM 需要人群、标签、calibration 与 OOD 验证的差别。
- **multimodal**：用 VisualSkill 的图文技能对照，讨论视觉证据、预算和评审方式。
- **privacy**：用 unlearning 研究谈评测限制，同时明确它不授予训练私有数据的许可。
- **See Around Corners**：可讨论“现有指标可能漏掉答案完整性/真实检索难度”的研究动机；没有事前时间线证据，就不要说自己提前预防了产品事故。

## 没有具体经验时的三种自然回答
**没做过 learned RM：** “I have worked on verifiable feedback rather than owning a production preference-modeling pipeline. A useful connection is verifier bias: a policy can optimize what the evaluator rewards without becoming more correct. For a learned RM, I would additionally examine annotator variation, calibration, and current-policy coverage.”

**没负责过超大规模 pre-training：** “My direct experience is closer to post-training and evaluation. For pre-training or mid-training, I would test whether the gap reflects missing coverage rather than behavior, and validate the data intervention with controlled continued-training experiments.”

**没做过线上私有反馈飞轮：** “I would use permitted aggregate failure categories to decide what to reproduce with licensed or synthetic data. I would not assume private user traces can be turned into global training examples.”

## 阅读顺序与最小产出
第一遍：读六张卡的 setting 和英文段落。第二遍：只深读前三条的论文方法、实验与限制，亲自挑一个失败样本。第三遍：每条用一张纸写任务、数据、监督、独立评测、负结果和你个人贡献。读懂资料后才使用“我了解该 setting”，真正运行后才说“我复现过”。

会前至少补齐：DeepAmbigQA 具体贡献__；一个真实错误__；合成 QA 质量检查__；HarnessLLM/HardTests 本人负责部分__；最熟悉的 RL 实现细节__；VisualSkill 本人贡献__；一个事前判断的时间证据__。这些信息公开资料无法可靠替你填写。

[公开研究入口](https://question406.github.io/)；本仓库的来源审计在 `content/sources/afm-personal-reference-2026-10-27/README.md`。论文版本与主页/CV 的发表状态有差异时，讲内容、按确定的版本引用，不混报成果状态。

## 进一步展开成数据 Pipeline

`afm-pipeline-overview` 串起 Skill/Harness、代码验证和 multimodal 工具操作三条具体设计：每条包含来源、数据契约、data quality checks、训练视图与 feedback loop。本册完整参考稿为 AFM-DATA-PIPELINE-EXAMPLES.md；正文不把建议方案称为个人实绩。
