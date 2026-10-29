---
id: report-benchmarks-map
section: report-benchmarks
order: 0
level: S
title: "Frontier Reports：主流 Safety / Security Benchmarks 速查与阅读顺序"
quick: "我会先看跨报告出现的 agent-security 与 control 设置，再读 model-level safeguards。Gray Swan IPI、SHADE-Arena、LinuxArena 是这条线的重要入口；CyberSecEval 则把多种风险放进公开套件。"
companies: []
tags:
  - Frontier Report Benchmarks 2026-10-28
  - Safety / Security Research
  - "报告索引"
realInterview: false
status: published
format: markdown
collapseAnswer: false
updatedAt: '2026-10-28'
sources:
  - title: "Gray Swan IPI / historical ART · benchmark / original source"
    url: "https://arxiv.org/abs/2603.15714"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Gemini 4 Argon Safety & Security Report"
    url: "https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
  - title: "CyberSecEval / CyberSecEval 2 · benchmark / original source"
    url: "https://arxiv.org/abs/2404.13161"
    type: primary
  - title: "The Llama 3 Herd of Models"
    url: "https://arxiv.org/html/2407.21783v1"
    type: primary
  - title: "StrongREJECT · benchmark / original source"
    url: "https://arxiv.org/abs/2402.10260"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
  - title: "SHADE-Arena · benchmark / original source"
    url: "https://www.anthropic.com/research/shade-arena-sabotage-monitoring"
    type: primary
  - title: "LinuxArena · benchmark / original source"
    url: "https://www.redwoodresearch.org/blog/introducing-linuxarena"
    type: primary
  - title: "MASK / MASK-Rectified · benchmark / original source"
    url: "https://arxiv.org/abs/2503.03750"
    type: primary
  - title: "BBQ · benchmark / original source"
    url: "https://arxiv.org/abs/2110.08193"
    type: primary
  - title: "CyberGym · benchmark / original source"
    url: "https://arxiv.org/abs/2506.02548"
    type: primary
  - title: "CVE-Bench · benchmark / original source"
    url: "https://arxiv.org/abs/2503.17332"
    type: primary
  - title: "GPT-5.6 System Card"
    url: "https://deploymentsafety.openai.com/gpt-5-6"
    type: primary
  - title: "CoT monitorability / controllability evaluations · benchmark / original source"
    url: "https://arxiv.org/abs/2512.18311"
    type: primary
---

## 题目描述

你想优先准备 frontier labs 官方报告真正采用的 evaluations，而不是把所有近期论文平均用力。

需要讨论：按直接采用证据、研究目标和复现条件建立优先清单。

## 回答思路

> **Situation：** 你想优先准备 frontier labs 官方报告真正采用的 evaluations，而不是把所有近期论文平均用力。  
> **Task：** 按直接采用证据、研究目标和复现条件建立优先清单。  
> **Approach / Why：** 先读 agent robustness/control，再补 safeguards、bias/honesty 与危险能力 probes。  
> **Result / Check：** 每项都能解释测什么、报告怎么用、结果不能外推到什么。

## 可以这样回答

我会先看跨报告出现的 agent-security 与 control 设置，再读 model-level safeguards。Gray Swan IPI、SHADE-Arena、LinuxArena 是这条线的重要入口；CyberSecEval 则把多种风险放进公开套件。

StrongREJECT、MASK、BBQ 分别帮助理解 jailbreak 输出、honesty 与 bias。CyberGym/CVE-Bench 以及更高难度 exploitation tests 测的是危险能力，不能当成拒绝或授权分数。

优先级来自这批官方报告中的可核实使用和研究相关性，不是全行业频率统计。内部 suites 也要读，但必须保留公开程度和配置差异。

## 报告实际采用证据

### Gray Swan IPI / historical ART

**类别：** external benchmark / competition-derived replay。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.1；PDF pp.84–85 · `external_evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2.6 / Figure 6.9；PDF pp.211–212 · `external_evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §5.2.1；PDF pp.83–84 · `external_evaluated`。历史名称 ART；与当前 IPI 分开

**读分数时看：** Attack success within k attempts；固定 Q1/Q2、场景集、model endpoint 与 safeguards。

**适用范围：** ART 与后续 IPI 的版本、surface 与 k 可能改变，不能直接合并历史 scores。

### CyberSecEval / CyberSecEval 2

**类别：** public benchmark suite。**优先级：** P0。

- [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v1) · §5.4.5；Figure 23 / §5.5 Prompt Guard · `evaluated`。

**读分数时看：** 按 secure code、interpreter abuse、text injection、CTF 等具体 task 分开评分。

**适用范围：** 不同 sub-evals 的安全方向不同，不存在统一的“越高越安全”解释。

### StrongREJECT

**类别：** public benchmark + evaluator。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · `evaluated`。

**读分数时看：** 有害目标相关的 response quality / compliance；需说明 report 采用的 grading。

**适用范围：** 不能把文字拒绝率或 provider 的 binary compliance 与原论文连续评分当同一指标。

### SHADE-Arena

**类别：** public agent-control benchmark。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.1；PDF pp.141–143 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §6.4.1；PDF pp.142–144 · `evaluated`。

**读分数时看：** Harmful side-task success AND monitor evasion；主任务结果另报。

**适用范围：** Monitor、可见 reasoning、side-goal induction 与 red-team elicitation 都影响得分。

### LinuxArena

**类别：** public privileged-environment control setting。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.2；PDF pp.144–146 · `evaluated`。

**读分数时看：** 在真实 Linux 工作流中的 main/side task outcomes 与监控效果。

**适用范围：** 不同 task subset、privileges 与 monitor 不是同一个实验。

### MASK / MASK-Rectified

**类别：** public benchmark + provider adaptation。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.5.4.2；PDF p.130 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §11.1；PDF p.26 · `evaluated_adapted`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §12.1；PDF p.38 · `evaluated_adapted`。

**读分数时看：** Stated belief 与 pressured response 的 contradiction / honesty；记录 exclusions。

**适用范围：** MASK-Rectified 修改 roleplay 判定；不同评分版本和方向不能直接对比。

### BBQ

**类别：** public QA benchmark。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §4.4.2；PDF pp.75–76 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · Bias Benchmark for QA；PDF pp.71–72 · `evaluated`。

**读分数时看：** Ambiguous/disambiguated accuracy 与 bias score。

**适用范围：** QA stereotypes 与真实 agent 的 allocation / action fairness 分别测。

### CyberGym

**类别：** public real-world vulnerability benchmark。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §6.1；PDF p.17 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §7.1；PDF p.29 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §2.17；PDF p.28 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.4；PDF p.53 · `retired`。该报告明确说明 retired due to saturation

**读分数时看：** 按版本定义的 vulnerability reproduction success。

**适用范围：** Reproduce vulnerability 与 working exploit 不同；最新报告可能因 saturation 换用更难任务。

### CVE-Bench

**类别：** public web-application benchmark。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.2.2 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §6.2；PDF p.18 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §7.2；PDF p.30 · `evaluated`。

**读分数时看：** 任务成功、zero-day / one-day、source access、pass@k 与有效 challenges 数。

**适用范围：** 版本/运行子集不同会改变分母；不等于所有 CVE 或真实网络的攻防能力。

### CoT monitorability / controllability evaluations

**类别：** public methodology + internal environments。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §7.3.1 / §7.3.2 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.4；PDF p.149 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §3.4.5 · `evaluated`。

**读分数时看：** TPR/TNR-dependent metric、observations、reasoning length 与任务分布。

**适用范围：** Monitorability score 不是 misalignment incidence；与学术 MonitorBench 区分。

## 本轮范围

本章新增 **20 张 cards**：2 张索引、18 张 benchmark / report-reading 专题。结构化目录共 **31 个条目**，包含公开 benchmarks、attack methodologies、provider-specific suites、能力对照和研究补充。

抽查 **10 份官方资料**：GPT-5.6、ChatGPT Agent、Claude Opus 5.5 / 4.6、Gemini 4 Argon、Grok 4.7 / 4.6，以及 Llama 3 / 4、Qwen3 的原始报告或 model cards。报告数量是取样范围，不是独立实验室数量。

对于 Llama 4 和 Qwen3，本次抽查未建立下表具体公开 safety benchmark 的逐项采用证据，保留它们为披露范围对照；不会因出现 safety 段落就推断用了某个测试。

## 优先阅读清单

| 优先级 | Benchmark / evaluation | 主要用途 | 对应 card |
| --- | --- | --- | --- |
| P0 | Gray Swan IPI / ART | Agent 对 indirect injection 的稳健性 | [[report-gray-swan-ipi]] |
| P0 | CyberSecEval | Secure code、tool/interpreter abuse、injection 等具体子项 | [[report-cyberseceval]] |
| P0 | SHADE-Arena | Side-goal success 与 monitor evasion | [[report-shade-arena]] |
| P0 | LinuxArena | 高权限真实工作环境中的 AI control | [[report-linux-arena]] |
| P0 | Internal injection / behavior suites | Coding、browser、tools、GUI 与真实动作 | [[report-internal-injection]]、[[report-internal-alignment]] |
| P0 | StrongREJECT / Crescendo | Jailbreak 输出有效性与多轮攻击 | [[report-strongreject]]、[[report-crescendo]] |
| P0 | MASK / BBQ | Honesty under pressure 与 demographic bias | [[report-mask-honesty]]、[[report-bbq]] |
| P0–P1 | CyberGym / CVE-Bench / Cybench | Cyber capability，与 safeguards 分开读 | [[report-cybergym]]、[[report-cve-bench]]、[[report-cybench]] |
| P1 | ExploitBench / ExploitGym | Saturation 后更细、更难的能力测试 | [[report-exploit-frontier]] |
| P1 | WMDP / LAB-Bench / VCT / ProtocolQA / FORTRESS | Knowledge / practical capability / safeguard 的区别 | [[report-bio-risk-suite]] |
| P1 | HealthBench / Professional | 健康场景的 performance 与 safety | [[report-healthbench]] |
| P1 | SWE-bench / Terminal-Bench / OSWorld / MCP-Atlas | 安全研究中的正常能力对照 | [[report-capability-controls]] |

如果只准备 agentic-system safety/security，先读前五行；如果想读懂整个 frontier safety report，再补 jailbreak、honesty/bias 和 dangerous-capability 部分。

## 本轮特别需要记住的变化

- **CyberGym 的位置在变：** Claude Opus 5.5 的 §3.3.4 明确说因 saturation 在该报告中退役；Grok 4.7 的 §6.1 仍有实际评估。分别记录，不能简化成整个领域已经不用。
- **公开研究热门 ≠ 本次报告核实采用：** 前版的 AgentDojo、AgentDyn、AgentLAB 等继续作为研究基准；本章不把它们整组升级成广泛采用的 release benchmarks。
- **相同名字 ≠ 相同协议：** MASK-Rectified、ProtocolQA Open-Ended、FORTRESS-RN，以及 ART / IPI 的历史版本，都保留后缀和具体设置。
- **方法不伪装成 dataset：** Crescendo 是攻击方法，GPT-Red 是自动化 red-teaming 方法；它们不等于一份固定 prompt 集。
- **能力不伪装成安全：** CyberGym、CVE-Bench、WMDP 高分主要说明能力；需要与 refusal、authorization 和真实危害分别解释。

这些是本轮取样的阅读判断。逐条来源见 [[report-benchmarks-evidence]]，原始报告链接也在每张 card 中。


## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 先读下方阅读路线，并打开每张 card 的报告章节核对 metric。
- **Baselines / Controls：** 用相同 manifest 比较相同 construct，缺失字段写 unknown。
- **Metrics / Interpretation：** 形成两张表：报告采用证据；自己拟做的可复现实验。

## 追问与容易误判的地方

本轮资料核对截止 2026-10-28；具体报告可能继续更新，应保留版本与来源。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
