---
id: sec-research-map
section: guide
order: 0
level: S
title: "Research Map：LLM / Agentic Safety & Security 应该怎样系统读？"
quick: "我会先沿 agent 的完整执行链读：user objective、读取外部内容、planning、tool actions、memory 与后续迭代。每一段都问：谁能改变输入，谁拥有权限，什么结果才算违规。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
  - "2026 Research"
realInterview: false
status: published
format: markdown
collapseAnswer: false
updatedAt: '2026-10-28'
sources:
  - title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
    url: "https://arxiv.org/abs/2406.13352"
    type: primary
  - title: "Defeating Prompt Injections by Design (CaMeL)"
    url: "https://arxiv.org/abs/2503.18813"
    type: primary
  - title: "AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?"
    url: "https://arxiv.org/abs/2602.03117"
    type: primary
  - title: "Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks"
    url: "https://arxiv.org/abs/2602.20156"
    type: primary
  - title: "OSGuard: A Benchmark for Safety in Computer-Use Agents"
    url: "https://arxiv.org/abs/2606.15034"
    type: primary
  - title: "Evaluating Control Protocols for Untrusted AI Agents"
    url: "https://arxiv.org/abs/2511.02997"
    type: primary
---

## 题目描述

你需要把分散的 safety/security 论文组织成能解释机制、评估证据并提出新问题的研究路线。

需要讨论：从 threat models、攻击入口、persistent state、runtime defenses 和 evaluation 串起全书。

## 回答思路

> **Situation：** 你需要把分散的 safety/security 论文组织成能解释机制、评估证据并提出新问题的研究路线。  
> **Task：** 从 threat models、攻击入口、persistent state、runtime defenses 和 evaluation 串起全书。  
> **Approach / Why：** 每条研究线先问受保护对象与 attacker access，再读机制、保证和实验，最后形成可证伪问题。  
> **Result / Check：** 能说明一篇论文改变了哪个假设、没有解决什么，以及自己会做哪个最小实验。

## 可以这样回答

我会先沿 agent 的完整执行链读：user objective、读取外部内容、planning、tool actions、memory 与后续迭代。每一段都问：谁能改变输入，谁拥有权限，什么结果才算违规。

然后用三条线并行：模型训练是否学会区分来源，runtime 是否限制即使模型受骗后的动作，以及 benchmark 是否真的测到安全而非基础能力。

读完一篇论文，不只记 ASR。我要能说出设置、关键方法、证据适用范围，以及一个最可能推翻结论的实验。后面的 research proposals 给出这种讨论的起点。

## 官方报告 Benchmarks 新入口

优先看 [[report-benchmarks-map]]，再查 [[report-benchmarks-evidence]]。本轮按官方报告采用证据新增 20 张 cards 与 31 个条目；公开研究基准与报告实际采用、内部套件分别列明。

## 全书范围与证据

这本题本有 **80 张 cards、12 个章节**，其中 76 张专题题、4 张总览/参考索引。引用 **79 个 primary sources**，包括论文、作者官方研究报告和 versioned protocol documentation。检索截止 **2026-10-28**。

这些 cards 是围绕公开研究整理的讨论题。每题把文献依据、拟议实验和个人经历分开；本书没有把 research questions 标成公司面试原题，也没有把拟议结果写成已完成的成果。`preprint`、已核对的会议与官方报告在参考卡中分别标注。

| 章节 | Cards | 要回答的核心问题 |
| --- | ---: | --- |
| Frontier Reports Benchmarks | 20 | 哪些被报告实际采用，什么版本，测的是什么？ |
| Foundations | 6 | 谁被保护、谁能攻击、什么结果算失败？ |
| Prompt Injection | 6 | 外部文本通过什么机制影响 planning 与 action？ |
| MCP / Tools / Skills | 6 | Metadata、delegation 与执行权限如何组合？ |
| Memory / RAG | 5 | 内容怎样持久化、跨 session 传播和被清除？ |
| Multimodal / Computer Use | 4 | 视觉与 UI state 如何改变 safety judgement？ |
| Defenses | 7 | Model training 与 runtime constraints 各能保证什么？ |
| Evaluation | 7 | Benchmark 真在测安全，还是能力与拒绝倾向？ |
| Control / Alignment | 6 | 模型自身不可信时，怎样监控与限制它？ |
| Privacy | 4 | 数据可读取、可传播与可训练是否分别被授权？ |
| Research Proposals | 7 | 怎样提出一个可证伪、能交付的项目？ |

## 最先读的 12 张 cards

1. [[sec-safety-security-threat-model]]：先统一问题定义。
2. [[sec-safe-completion-objective]]：定义既有用又安全的结果。
3. [[sec-indirect-injection-causal-chain]]：定位从内容到副作用的因果链。
4. [[sec-mcp-tool-metadata-poisoning]]：扩展到 discovery-time tool metadata。
5. [[sec-skill-inject-supply-chain]]：把 skills 放入 supply chain。
6. [[sec-memory-attacker-models]]：理解 persistent-state threat models。
7. [[sec-camel-security-guarantees]]：理解结构性 defense 与保证前提。
8. [[sec-ipiguard-dynamic-planning]]：讨论安全与动态能力的取舍。
9. [[sec-computer-use-benign-context-risk]]：看正常任务中的不安全执行。
10. [[sec-ignored-not-refused-outcomes]]：审查低 ASR 的含义。
11. [[sec-control-protocols-critical-actions]]：面对 untrusted agent policy。
12. [[sec-proposal-research-pitch]]：形成自己的讨论切入点。

## 2026 更新优先看什么

| Research line | 本版资料 | 要追问的 gap |
| --- | --- | --- |
| Dynamic tasks | AgentDyn、AgentLAB | 静态 plan 的保证能否支持真实探索？ |
| Role perception | Prompt Injection as Role Confusion | Probes 是预测信号，还是可干预机制？ |
| Skills | Skill-Inject、SkillGuard | Context influence 怎样与执行权限关联？ |
| Computer use | OS-BLIND、OSGuard | 用户目标正常，过程中怎样违反 state constraints？ |
| Model safeguards | IH-Challenge、Constitutional Classifiers++ | Generalization、over-refusal 与成本怎样共同测？ |
| Monitoring | MonitorBench、Summer 2026 misalignment cases | CoT 与 action/state observations 各提供什么证据？ |
| Persistent state | eTAMP、StegoMemory | Write、retrieval 与 action-time checks 怎样互补？ |
| Measurement validity | Safety, or Just Capability?、Ignored, Not Refused | 低风险分是否只是低 capability 或没有 exposure？ |

StegoMemory 和 Ignored, Not Refused 是 2026-10 preprints，本版用于提出问题与复现实验，不将其初步结果当成领域定论。OSGuard 引用页包含 2026-10 revision；阅读论文时核对版本。

## 可直接用于 paper discussion 的模板

| 要素 | 必须说清楚 |
| --- | --- |
| Claim | 论文想证明哪个可观察性质？ |
| Attacker | 控制什么、看见什么、试多少次、能否持久化？ |
| Defender | 改模型、prompt、harness、permissions，还是 evaluator？ |
| Trusted components | 哪些 policy、interpreter、tools 与 labels 被假定正确？ |
| Utility | 正常任务能否完成，是否存在安全路径？ |
| Oracle | 判的是输出、action、环境状态，还是长期结果？ |
| Generalization | 新 task、template、domain、model 和 horizon 是否测试？ |
| Counterevidence | 哪个实验结果会削弱论文或自己的假设？ |

## 两周研究起步路线

- **第 1–2 天：** 选一条 threat model，读 benchmark 与一种 runtime defense，固定版本和术语。
- **第 3–5 天：** 做 10–20 个能重放的 synthetic tasks，先证明 clean task 可解、oracle 正确。
- **第 6–8 天：** 跑 clean、无 defense、保守 baseline 与目标方法，归因 failures。
- **第 9–11 天：** 加 matched helpful instructions、held-out variants 或小预算 adaptive evaluation。
- **第 12–14 天：** 写 raw counts、uncertainty、cost 和反例，整理一页 proposal 与 90 秒口述。

这些数字是起步规划，不是已有实验。需要使用付费模型时，先估算预算；本次创建题本没有调用付费模型或执行外部攻击实验。


## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 先读本卡的章节地图，再选一条主线，固定一份最小 threat-model template。
- **Baselines / Ablations：** 每条线至少比较 prompt/model/runtime 三类方法，并留一个能力与拒绝基线。
- **Metrics 与判读：** 完成一页 paper notes：claim、assumptions、oracle、utility、adaptive test 和 open question。

## 追问与容易误判的地方

检索与内容核对截止 2026-10-28；2026 preprints 在卡片中标注。研究前沿是这一版的 snapshot，需要随新证据修订。

## 论文依据与适用范围

- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) · 2024 · NeurIPS 2024。
- [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) · 2025 · research paper。
- [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) · 2026 · preprint。
- [Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks](https://arxiv.org/abs/2602.20156) · 2026 · preprint。
- [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) · 2026 · preprint · revision 2026-10。
- [Evaluating Control Protocols for Untrusted AI Agents](https://arxiv.org/abs/2511.02997) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
