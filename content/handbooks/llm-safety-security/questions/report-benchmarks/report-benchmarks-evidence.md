---
id: report-benchmarks-evidence
section: report-benchmarks
order: 1
level: S
title: 官方采用证据表：Benchmark、Report、版本、公开程度与历史替换
quick: 我会把证据分成几类。实际运行或第三方对该模型评测，才算直接采用；改过 dataset、grading 或任务形式，就保留 adapted 标记。
companies: []
tags:
  - Frontier Report Benchmarks 2026-10-28
  - Safety / Security Research
  - 报告索引
realInterview: false
status: published
format: markdown
collapseAnswer: false
updatedAt: '2026-10-28'
sources:
  - title: Gray Swan IPI / historical ART · benchmark / original source
    url: 'https://arxiv.org/abs/2603.15714'
    type: primary
  - title: Claude Opus 5.5 System Card
    url: 'https://www.anthropic.com/claude-opus-5-5-system-card'
    type: primary
  - title: Gemini 4 Argon Safety & Security Report
    url: >-
      https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf
    type: primary
  - title: Claude Opus 4.6 System Card
    url: 'https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf'
    type: primary
  - title: StrongREJECT · benchmark / original source
    url: 'https://arxiv.org/abs/2402.10260'
    type: primary
  - title: Grok 4.7 Model Card
    url: 'https://media.x.ai/v1/website/card4p7-3a96f40b.pdf'
    type: primary
  - title: Grok 4.6 Model Card
    url: 'https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf'
    type: primary
  - title: Crescendo · benchmark / original source
    url: 'https://arxiv.org/abs/2404.01833'
    type: primary
  - title: CyberSecEval / CyberSecEval 2 · benchmark / original source
    url: 'https://arxiv.org/abs/2404.13161'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/html/2407.21783v1'
    type: primary
  - title: Cybench · benchmark / original source
    url: 'https://arxiv.org/abs/2408.08926'
    type: primary
  - title: CyberGym · benchmark / original source
    url: 'https://arxiv.org/abs/2506.02548'
    type: primary
  - title: CVE-Bench · benchmark / original source
    url: 'https://arxiv.org/abs/2503.17332'
    type: primary
  - title: GPT-5.6 System Card
    url: 'https://deploymentsafety.openai.com/gpt-5-6'
    type: primary
  - title: ExploitBench · benchmark / original source
    url: 'https://arxiv.org/abs/2605.14153'
    type: primary
  - title: ExploitGym · benchmark / original source
    url: 'https://arxiv.org/abs/2605.11086'
    type: primary
  - title: SHADE-Arena · benchmark / original source
    url: 'https://www.anthropic.com/research/shade-arena-sabotage-monitoring'
    type: primary
  - title: LinuxArena · benchmark / original source
    url: 'https://www.redwoodresearch.org/blog/introducing-linuxarena'
    type: primary
  - title: MASK / MASK-Rectified · benchmark / original source
    url: 'https://arxiv.org/abs/2503.03750'
    type: primary
  - title: BBQ · benchmark / original source
    url: 'https://arxiv.org/abs/2110.08193'
    type: primary
  - title: WMDP · benchmark / original source
    url: 'https://arxiv.org/abs/2403.03218'
    type: primary
  - title: ProtocolQA Open-Ended · benchmark / original source
    url: 'https://arxiv.org/abs/2407.10362'
    type: primary
  - title: Virology Capabilities Test (VCT) · benchmark / original source
    url: 'https://arxiv.org/abs/2504.16137'
    type: primary
  - title: FORTRESS / FORTRESS-RN · benchmark / original source
    url: 'https://arxiv.org/abs/2506.14922'
    type: primary
  - title: HealthBench / HealthBench Hard · benchmark / original source
    url: 'https://arxiv.org/abs/2505.08775'
    type: primary
  - title: HealthBench Professional · benchmark / original source
    url: 'https://arxiv.org/abs/2604.27470'
    type: primary
  - title: ChatGPT Agent System Card
    url: 'https://deploymentsafety.openai.com/chatgpt-agent'
    type: primary
  - title: >-
      CoT monitorability / controllability evaluations · benchmark / original
      source
    url: 'https://arxiv.org/abs/2512.18311'
    type: primary
  - title: HarmBench · benchmark / original source
    url: 'https://arxiv.org/abs/2402.04249'
    type: primary
  - title: XSTest · benchmark / original source
    url: 'https://arxiv.org/abs/2308.01263'
    type: primary
  - title: >-
      AgentDojo / InjecAgent / AgentHarm / AgentDyn / AgentLAB · benchmark /
      original source
    url: 'https://arxiv.org/abs/2406.13352'
    type: primary
  - title: Llama 4 official model card
    url: >-
      https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md
    type: primary
  - title: Qwen3 Technical Report
    url: 'https://arxiv.org/html/2505.09388v1'
    type: primary
---

## 题目描述

同名 benchmark 可能被直接运行、改成一个 variant、只在参考文献提到，或已经退役。

需要讨论：给每项保留报告和章节证据，避免把“提到了”误写成“采用了”。

## 回答思路

> **Situation：** 同名 benchmark 可能被直接运行、改成一个 variant、只在参考文献提到，或已经退役。  
> **Task：** 给每项保留报告和章节证据，避免把“提到了”误写成“采用了”。  
> **Approach / Why：** 区分 evaluated、external_evaluated、adapted、component、method_used、retired 与 referenced_only。  
> **Result / Check：** 原始 benchmark 链接和报告链接都可追溯，缺少直接证据时明确标注。

## 可以这样回答

我会把证据分成几类。实际运行或第三方对该模型评测，才算直接采用；改过 dataset、grading 或任务形式，就保留 adapted 标记。

一篇报告讨论 XSTest，不说明它实际运行了公开 XSTest；一个报告说 CyberGym 退役，也不说明所有 labs 都不用了。保留这些区别，清单才适合长期维护。

下方是本轮抽查的证据表。它展示已核实的关系，不以未找到来证明某个实验室从未使用。

## 报告实际采用证据

### Gray Swan IPI / historical ART

**类别：** external benchmark / competition-derived replay。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.1；PDF pp.84–85 · `external_evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2.6 / Figure 6.9；PDF pp.211–212 · `external_evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §5.2.1；PDF pp.83–84 · `external_evaluated`。历史名称 ART；与当前 IPI 分开

**读分数时看：** Attack success within k attempts；固定 Q1/Q2、场景集、model endpoint 与 safeguards。

**适用范围：** ART 与后续 IPI 的版本、surface 与 k 可能改变，不能直接合并历史 scores。

### StrongREJECT

**类别：** public benchmark + evaluator。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · `evaluated`。

**读分数时看：** 有害目标相关的 response quality / compliance；需说明 report 采用的 grading。

**适用范围：** 不能把文字拒绝率或 provider 的 binary compliance 与原论文连续评分当同一指标。

### Crescendo

**类别：** attack methodology。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · `evaluated_as_component`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · `evaluated_as_component`。

**读分数时看：** 固定 turn / query budget 下的 harmful completion 或攻击成功。

**适用范围：** 它是一种多轮攻击方法；报告中的 long-horizon suite 可能混合多种 attacks。

### CyberSecEval / CyberSecEval 2

**类别：** public benchmark suite。**优先级：** P0。

- [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v1) · §5.4.5；Figure 23 / §5.5 Prompt Guard · `evaluated`。

**读分数时看：** 按 secure code、interpreter abuse、text injection、CTF 等具体 task 分开评分。

**适用范围：** 不同 sub-evals 的安全方向不同，不存在统一的“越高越安全”解释。

### Cybench

**类别：** public CTF benchmark。**优先级：** P1。

- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §8.4.7；PDF p.201 · `evaluated`。

**读分数时看：** Task/subtask success、pass@k、可用 hints 与 scaffold。

**适用范围：** 能力评估，不能读成模型拒绝 malicious requests 或 agent 抵抗 injection。

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

### ExploitBench

**类别：** public capability-ladder benchmark。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.2.4.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.1；PDF p.49 · `evaluated`。

**读分数时看：** Verifier-confirmed capabilities / report-specific aggregation。

**适用范围：** 中间能力与最终 working exploit 分开，不能把 capability percentage 当 full compromise rate。

### ExploitGym

**类别：** public working-exploit benchmark。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.2.4.2 / ExploitGym · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.4；PDF pp.53–54 · `evaluated`。

**读分数时看：** 按 pinned protections 与 task set 的 verified exploit success。

**适用范围：** 论文与报告 task count 可能不同；固定 release 与可评估 subset，区分 crash 和安全影响。

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

### WMDP

**类别：** public multiple-choice proxy。**优先级：** P1。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.5；PDF p.22 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §8.4；PDF p.33 · `evaluated`。

**读分数时看：** Bio/Chem/Cyber 子集 accuracy。

**适用范围：** 危险知识 proxy，与 refusal / safeguard effectiveness 分开解释。

### LAB-Bench

**类别：** public benchmark。**优先级：** P1。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.6；PDF p.22 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §8.5；PDF p.34 · `evaluated`。

**读分数时看：** 按实际使用的 practical / 子任务 split 报 accuracy。

**适用范围：** 通用生物研究能力，不自动等于 harmful uplift。

### Virology Capabilities Test (VCT)

**类别：** public multimodal benchmark。**优先级：** P1。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §2.2.3.1；PDF pp.20–21 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.2；PDF p.21 · `evaluated`。

**读分数时看：** 按具体 release 的 expert-graded accuracy。

**适用范围：** Biology knowledge 与安全拒绝不同；Biosecurity VCT 是报告中另列的 internal companion。

### ProtocolQA Open-Ended

**类别：** report-adapted task variant。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.1.2 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.7；PDF p.22 · `evaluated`。

**读分数时看：** Free-text protocol troubleshooting accuracy。

**适用范围：** 不能把 open-ended variant 当成原 multiple-choice task 的同一分数。

### FORTRESS / FORTRESS-RN

**类别：** public benchmark + report subset。**优先级：** P1。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §9.3；PDF p.25 · `evaluated_adapted`。

**读分数时看：** Harmful-risk rubric 与 benign counterpart 的 over-refusal；报告注明 RN subset。

**适用范围：** FORTRESS-RN 不能代表完整 FORTRESS；accuracy / refusal / risk score 需分别解释。

### HealthBench / HealthBench Hard

**类别：** public rubric benchmark。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §5.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.15.1；PDF p.213 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · Health section；PDF pp.176–178 · `evaluated`。

**读分数时看：** Rubric-based score，指定 Hard / Consensus 等 variant。

**适用范围：** 有 health safety 维度，但不是通用 jailbreak 或 agent authorization benchmark。

### HealthBench Professional

**类别：** public clinician-task benchmark。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §5.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.15.2；PDF p.213 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · Health；PDF p.177 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §5.1；PDF p.15 · `evaluated`。

**读分数时看：** Clinician-use rubric score；注明长度调整与采样协议。

**适用范围：** 与 HealthBench 是不同分布，不能把 rubric 分数当临床安全概率。

### GPT-Red

**类别：** attacker model / methodology。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §4.2；2026-08-03 update · `method_used`。

**读分数时看：** 指定 defender queries 下的 attack success，单次 attempt 与累计风险分开。

**适用范围：** 它是攻击生成方法，不是一套与所有 benchmark 等价的固定测试集。

### OpenAI connector / search / function-calling injection evals

**类别：** internal suite。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §4.2 · `evaluated`。
- [ChatGPT Agent System Card](https://deploymentsafety.openai.com/chatgpt-agent) · Prompt injection / robustness sections · `evaluated`。

**读分数时看：** 各 surface 的 attack success / robustness，具体版本见 report。

**适用范围：** Full dataset / harness 不应假设公开；与 Gray Swan scenario reuse 区分。

### Anthropic adaptive coding / computer / browser injection evals

**类别：** internal / partner evaluation suites。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.2；PDF pp.86–91 · `evaluated`。

**读分数时看：** 固定 surface、attacker budget、harness、fallback 与 safeguards。

**适用范围：** Shade attacker 与 SHADE-Arena benchmark 不同；同名 surface 不保证样本一致。

### Gemini held-out tool / grounding / computer / coding / replay suites

**类别：** mixed internal suites + external replay。**优先级：** P0。

- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2；PDF pp.204–212 · `evaluated`。

**读分数时看：** Survival@N attempts，并列合法任务完成情况。

**适用范围：** 五个 suites 的来源与场景不同；只有 external replay 才归入 Gray Swan 证据。

### CoT monitorability / controllability evaluations

**类别：** public methodology + internal environments。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §7.3.1 / §7.3.2 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.4；PDF p.149 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §3.4.5 · `evaluated`。

**读分数时看：** TPR/TNR-dependent metric、observations、reasoning length 与任务分布。

**适用范围：** Monitorability score 不是 misalignment incidence；与学术 MonitorBench 区分。

### Destructive actions / confirmation-consent / behavioral audits

**类别：** provider-specific internal evaluations。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §3.3 / §3.4 / §7.3.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.4 / §6.5.2；PDF pp.104–126 · `evaluated`。

**读分数时看：** 按具体 outcome：protected changes、inappropriate confirmation、misleading claims 等。

**适用范围：** 不同 provider 的行为标签不是同一个 benchmark；不能共用分母或直接排名。

### Harmful / benign / multi-turn refusal suites

**类别：** provider-specific internal evaluation families。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §4.1；PDF pp.61–65 · `evaluated`。
- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §3.1 / §4.1 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §4 / §5.6.1 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §9；PDF pp.24–25 · `evaluated`。

**读分数时看：** Harmful compliance 与 benign refusal 同时报，按 policy areas 分开。

**适用范围：** 不是一套全球统一的 harmful-prompts benchmark，不用不同 provider 的百分比直接横比。

### SWE-bench / Terminal-Bench / OSWorld / MCP-Atlas

**类别：** public task benchmarks / versioned variants。**优先级：** P1。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.2 / §8.5 / §8.13.3；PDF pp.175 / 177 / 205 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §2.16 MCP-Atlas；PDF p.28 · `evaluated`。

**读分数时看：** Task completion、strict/partial score、cost 与 tool competence。

**适用范围：** 这些是安全实验的能力对照，不将通过率称为 safety score。

### HarmBench

**类别：** public benchmark。**优先级：** P2。

- 本轮未建立直接采用证据，保留为研究对照。

**读分数时看：** Harmful completion / red-team evaluation。

**适用范围：** 保留为研究 baseline；本次抽查未以这些报告提供其直接采用证据。

### XSTest

**类别：** public benchmark。**优先级：** P2。

- [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v1) · §5.4.1 · `referenced_only`。

**读分数时看：** Safe prompt refusal 与 unsafe contrasts。

**适用范围：** Llama 3 将它作为已有外部 benchmark 讨论；此处不升级为直接采用证据。

### AgentDojo / InjecAgent / AgentHarm / AgentDyn / AgentLAB

**类别：** public research benchmark families。**优先级：** P2。

- 本轮未建立直接采用证据，保留为研究对照。

**读分数时看：** 按各自 threat model 和 evaluator 定义。

**适用范围：** 前版研究题本中的重要资料；本次报告抽样不支持把整组都称为广泛采用的 release benchmarks。

## 证据类型

- `evaluated` / `external_evaluated`：报告明确运行或说明外部机构对该模型进行了测试。
- `evaluated_adapted`：修改过 grading、子集或任务形式；实际 variant 单独记录。
- `evaluated_as_component` / `method_used`：攻击或评测方法，不冒充固定数据集。
- `retired`：该份报告明确说明不再报告此 benchmark。
- `referenced_only`：讨论或参考引用，不作为采用证据。

定位的 **PDF p.** 是文件页序号，从 1 开始；Grok 与 Gemini 的印刷页码可能比 PDF 页序号少一。它们在页脚可见。报告链接可能继续更新，本批保存下载文件的 SHA-256 以便核对。

## 完整目录与出处

| 条目 | 类别 / 优先级 | 报告证据与定位 | 读数限制 | Question card |
| --- | --- | --- | --- | --- |
| [Gray Swan IPI / historical ART](https://arxiv.org/abs/2603.15714) | external benchmark / competition-derived replay / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.1；PDF pp.84–85 · 外部评估； [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2.6 / Figure 6.9；PDF pp.211–212 · 外部评估； [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §5.2.1；PDF pp.83–84 · 外部评估 · 历史名称 ART；与当前 IPI 分开 | ART 与后续 IPI 的版本、surface 与 k 可能改变，不能直接合并历史 scores | [[report-gray-swan-ipi]] |
| [StrongREJECT](https://arxiv.org/abs/2402.10260) | public benchmark + evaluator / P0 | [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · 直接评估； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · 直接评估 | 不能把文字拒绝率或 provider 的 binary compliance 与原论文连续评分当同一指标 | [[report-strongreject]] |
| [Crescendo](https://arxiv.org/abs/2404.01833) | attack methodology / P0 | [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · suite 中的方法组件； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · suite 中的方法组件 | 它是一种多轮攻击方法；报告中的 long-horizon suite 可能混合多种 attacks | [[report-crescendo]] |
| [CyberSecEval / CyberSecEval 2](https://arxiv.org/abs/2404.13161) | public benchmark suite / P0 | [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v1) · §5.4.5；Figure 23 / §5.5 Prompt Guard · 直接评估 | 不同 sub-evals 的安全方向不同，不存在统一的“越高越安全”解释 | [[report-cyberseceval]] |
| [Cybench](https://arxiv.org/abs/2408.08926) | public CTF benchmark / P1 | [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §8.4.7；PDF p.201 · 直接评估 | 能力评估，不能读成模型拒绝 malicious requests 或 agent 抵抗 injection | [[report-cybench]] |
| [CyberGym](https://arxiv.org/abs/2506.02548) | public real-world vulnerability benchmark / P0 | [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §6.1；PDF p.17 · 直接评估； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §7.1；PDF p.29 · 直接评估； [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §2.17；PDF p.28 · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.4；PDF p.53 · 该报告退役 · 该报告明确说明 retired due to saturation | Reproduce vulnerability 与 working exploit 不同；最新报告可能因 saturation 换用更难任务 | [[report-cybergym]] |
| [CVE-Bench](https://arxiv.org/abs/2503.17332) | public web-application benchmark / P0 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.2.2 · 直接评估； [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §6.2；PDF p.18 · 直接评估； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §7.2；PDF p.30 · 直接评估 | 版本/运行子集不同会改变分母；不等于所有 CVE 或真实网络的攻防能力 | [[report-cve-bench]] |
| [ExploitBench](https://arxiv.org/abs/2605.14153) | public capability-ladder benchmark / P1 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.2.4.1 · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.1；PDF p.49 · 直接评估 | 中间能力与最终 working exploit 分开，不能把 capability percentage 当 full compromise rate | [[report-exploit-frontier]] |
| [ExploitGym](https://arxiv.org/abs/2605.11086) | public working-exploit benchmark / P1 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.2.4.2 / ExploitGym · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.4；PDF pp.53–54 · 直接评估 | 论文与报告 task count 可能不同；固定 release 与可评估 subset，区分 crash 和安全影响 | [[report-exploit-frontier]] |
| [SHADE-Arena](https://www.anthropic.com/research/shade-arena-sabotage-monitoring) | public agent-control benchmark / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.1；PDF pp.141–143 · 直接评估； [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §6.4.1；PDF pp.142–144 · 直接评估 | Monitor、可见 reasoning、side-goal induction 与 red-team elicitation 都影响得分 | [[report-shade-arena]] |
| [LinuxArena](https://www.redwoodresearch.org/blog/introducing-linuxarena) | public privileged-environment control setting / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.2；PDF pp.144–146 · 直接评估 | 不同 task subset、privileges 与 monitor 不是同一个实验 | [[report-linux-arena]] |
| [MASK / MASK-Rectified](https://arxiv.org/abs/2503.03750) | public benchmark + provider adaptation / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.5.4.2；PDF p.130 · 直接评估； [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §11.1；PDF p.26 · 改编版评估； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §12.1；PDF p.38 · 改编版评估 | MASK-Rectified 修改 roleplay 判定；不同评分版本和方向不能直接对比 | [[report-mask-honesty]] |
| [BBQ](https://arxiv.org/abs/2110.08193) | public QA benchmark / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §4.4.2；PDF pp.75–76 · 直接评估； [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · Bias Benchmark for QA；PDF pp.71–72 · 直接评估 | QA stereotypes 与真实 agent 的 allocation / action fairness 分别测 | [[report-bbq]] |
| [WMDP](https://arxiv.org/abs/2403.03218) | public multiple-choice proxy / P1 | [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.5；PDF p.22 · 直接评估； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §8.4；PDF p.33 · 直接评估 | 危险知识 proxy，与 refusal / safeguard effectiveness 分开解释 | [[report-bio-risk-suite]] |
| [LAB-Bench](https://arxiv.org/abs/2407.10362) | public benchmark / P1 | [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.6；PDF p.22 · 直接评估； [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §8.5；PDF p.34 · 直接评估 | 通用生物研究能力，不自动等于 harmful uplift | [[report-bio-risk-suite]] |
| [Virology Capabilities Test (VCT)](https://arxiv.org/abs/2504.16137) | public multimodal benchmark / P1 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §2.2.3.1；PDF pp.20–21 · 直接评估； [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.2；PDF p.21 · 直接评估 | Biology knowledge 与安全拒绝不同；Biosecurity VCT 是报告中另列的 internal companion | [[report-bio-risk-suite]] |
| [ProtocolQA Open-Ended](https://arxiv.org/abs/2407.10362) | report-adapted task variant / P1 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.1.2 · 直接评估； [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.7；PDF p.22 · 直接评估 | 不能把 open-ended variant 当成原 multiple-choice task 的同一分数 | [[report-bio-risk-suite]] |
| [FORTRESS / FORTRESS-RN](https://arxiv.org/abs/2506.14922) | public benchmark + report subset / P1 | [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §9.3；PDF p.25 · 改编版评估 | FORTRESS-RN 不能代表完整 FORTRESS；accuracy / refusal / risk score 需分别解释 | [[report-bio-risk-suite]] |
| [HealthBench / HealthBench Hard](https://arxiv.org/abs/2505.08775) | public rubric benchmark / P1 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §5.1 · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.15.1；PDF p.213 · 直接评估； [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · Health section；PDF pp.176–178 · 直接评估 | 有 health safety 维度，但不是通用 jailbreak 或 agent authorization benchmark | [[report-healthbench]] |
| [HealthBench Professional](https://arxiv.org/abs/2604.27470) | public clinician-task benchmark / P1 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §5.1 · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.15.2；PDF p.213 · 直接评估； [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · Health；PDF p.177 · 直接评估； [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §5.1；PDF p.15 · 直接评估 | 与 HealthBench 是不同分布，不能把 rubric 分数当临床安全概率 | [[report-healthbench]] |
| [GPT-Red](https://deploymentsafety.openai.com/gpt-5-6) | attacker model / methodology / P0 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §4.2；2026-08-03 update · 评测方法 | 它是攻击生成方法，不是一套与所有 benchmark 等价的固定测试集 | [[report-internal-injection]] |
| [OpenAI connector / search / function-calling injection evals](https://deploymentsafety.openai.com/gpt-5-6) | internal suite / P0 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §4.2 · 直接评估； [ChatGPT Agent System Card](https://deploymentsafety.openai.com/chatgpt-agent) · Prompt injection / robustness sections · 直接评估 | Full dataset / harness 不应假设公开；与 Gray Swan scenario reuse 区分 | [[report-internal-injection]] |
| [Anthropic adaptive coding / computer / browser injection evals](https://www.anthropic.com/claude-opus-5-5-system-card) | internal / partner evaluation suites / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.2；PDF pp.86–91 · 直接评估 | Shade attacker 与 SHADE-Arena benchmark 不同；同名 surface 不保证样本一致 | [[report-internal-injection]] |
| [Gemini held-out tool / grounding / computer / coding / replay suites](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) | mixed internal suites + external replay / P0 | [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2；PDF pp.204–212 · 直接评估 | 五个 suites 的来源与场景不同；只有 external replay 才归入 Gray Swan 证据 | [[report-internal-injection]] |
| [CoT monitorability / controllability evaluations](https://arxiv.org/abs/2512.18311) | public methodology + internal environments / P1 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §7.3.1 / §7.3.2 · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.4；PDF p.149 · 直接评估； [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §3.4.5 · 直接评估 | Monitorability score 不是 misalignment incidence；与学术 MonitorBench 区分 | [[report-internal-alignment]] |
| [Destructive actions / confirmation-consent / behavioral audits](https://deploymentsafety.openai.com/gpt-5-6) | provider-specific internal evaluations / P0 | [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §3.3 / §3.4 / §7.3.1 · 直接评估； [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.4 / §6.5.2；PDF pp.104–126 · 直接评估 | 不同 provider 的行为标签不是同一个 benchmark；不能共用分母或直接排名 | [[report-internal-alignment]] |
| [Harmful / benign / multi-turn refusal suites](https://www.anthropic.com/claude-opus-5-5-system-card) | provider-specific internal evaluation families / P0 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §4.1；PDF pp.61–65 · 直接评估； [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §3.1 / §4.1 · 直接评估； [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §4 / §5.6.1 · 直接评估； [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §9；PDF pp.24–25 · 直接评估 | 不是一套全球统一的 harmful-prompts benchmark，不用不同 provider 的百分比直接横比 | [[report-metrics-comparability]] |
| [SWE-bench / Terminal-Bench / OSWorld / MCP-Atlas](https://www.anthropic.com/claude-opus-5-5-system-card) | public task benchmarks / versioned variants / P1 | [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.2 / §8.5 / §8.13.3；PDF pp.175 / 177 / 205 · 直接评估； [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §2.16 MCP-Atlas；PDF p.28 · 直接评估 | 这些是安全实验的能力对照，不将通过率称为 safety score | [[report-capability-controls]] |
| [HarmBench](https://arxiv.org/abs/2402.04249) | public benchmark / P2 | 本轮未建立直接采用证据；研究补充 | 保留为研究 baseline；本次抽查未以这些报告提供其直接采用证据 | [[sec-jailbreak-generalization]] |
| [XSTest](https://arxiv.org/abs/2308.01263) | public benchmark / P2 | [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v1) · §5.4.1 · 仅讨论引用 | Llama 3 将它作为已有外部 benchmark 讨论；此处不升级为直接采用证据 | [[sec-jailbreak-generalization]] |
| [AgentDojo / InjecAgent / AgentHarm / AgentDyn / AgentLAB](https://arxiv.org/abs/2406.13352) | public research benchmark families / P2 | 本轮未建立直接采用证据；研究补充 | 前版研究题本中的重要资料；本次报告抽样不支持把整组都称为广泛采用的 release benchmarks | [[sec-benchmark-selection-matrix]] |

## 报告取样与披露范围

| Report | 核对范围 |
| --- | --- |
| [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) | 2026-07 release，含 2026-08 更新；重点核对 prompt injection、cyber、monitorability 与 health sections |
| [ChatGPT Agent System Card](https://deploymentsafety.openai.com/chatgpt-agent) | Agent-level evaluation，重点核对 prompt injection、cyber ranges 与 self-improvement sections |
| [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) | 2026-09；核对 safety / agentic / alignment / capability 相关 pages，含 PDF visual review |
| [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) | 2026-02；核对 Cybench、CyberGym、ART 与 capability sections，追踪历史版本 |
| [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) | 2026-10；重点核对 Section 6.1、Gray Swan IPI figure 与 monitoring / health sections |
| [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) | 重点核对 Sections 6–11 与 references；jailbreak table 已 visual review |
| [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) | 重点核对 Sections 7–12，作为上一代沿用证据 |
| [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v1) | 重点核对 Sections 5.4 / 5.5；CyberSecEval 为实际使用，ToxiGen / XSTest 区分为讨论引用 |
| [Llama 4 official model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md) | 核对 safety / cyber sections；本次未从该页确认对下表具体公开 safety benchmark 的逐项采用 |
| [Qwen3 Technical Report](https://arxiv.org/html/2505.09388v1) | 核对 evaluation / safety mentions；本次未据此认定下表某个 named public safety benchmark 被实际采用 |

## 每个结果需要一起保存的 manifest

```json
{
  "benchmark": "exact-name-and-variant",
  "dataset_revision": "pinned-release",
  "report_source": "official-url-and-section",
  "evidence_role": "evaluated-or-adapted",
  "model_endpoint": "exact-model-or-fallback",
  "harness_revision": "pinned-commit",
  "attack_surface": "tool-or-coding-or-browser-or-GUI",
  "attacker_access": "explicit-editable-observation",
  "attempt_budget": 15,
  "safeguards": "explicit-on-off-and-components",
  "scorer_revision": "exact-rubric-and-grader",
  "eligible_n": null,
  "infrastructure_failures": null,
  "safe_task_success": null,
  "attack_success": null
}
```

这里的数值是字段示例；`null` 表示尚未记录。没有披露的信息填 unknown，不猜测。不同 policy、scorer 或 task subset 的结果保留各自设置。


## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 先核对报告章节，再回到原始 benchmark 的 release、scorer 与 dataset。
- **Baselines / Controls：** 对同名 variants、provider adaptations 和历史版本分别建记录。
- **Metrics / Interpretation：** 记录实际证据角色、公开性和限制；不计算没有代表性抽样支持的“全行业采用率”。

## 追问与容易误判的地方

本表包含 benchmarks、攻击方法、internal suites 和能力对照。31 个条目不是 31 个互相独立的固定安全测试集。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
