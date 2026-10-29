---
id: report-metrics-comparability
section: report-benchmarks
order: 19
level: S
title: "读 safety 表格：百分比、ASR、pass@k 与 refusal 为什么不能直接排名？"
quick: "我会先读这列究竟是谁的成功。ASR 越低通常越好，capability pass rate 越高说明能力更强，honesty 可能越高越好，而 dishonesty 则相反。光看都是百分比没有意义。"
companies: []
tags:
  - Frontier Report Benchmarks 2026-10-28
  - Safety / Security Research
  - "Benchmark Card"
realInterview: false
status: published
format: markdown
collapseAnswer: true
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
  - title: "MASK / MASK-Rectified · benchmark / original source"
    url: "https://arxiv.org/abs/2503.03750"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
  - title: "GPT-5.6 System Card"
    url: "https://deploymentsafety.openai.com/gpt-5-6"
    type: primary
---

## 题目描述

你看到多个 labs 的 safety tables，希望快速总结谁最安全。

需要讨论：列出比较前要对齐的最小信息，并说明哪些结果只能作各自内部趋势。

## 回答思路

> **Situation：** 你看到多个 labs 的 safety tables，希望快速总结谁最安全。  
> **Task：** 列出比较前要对齐的最小信息，并说明哪些结果只能作各自内部趋势。  
> **Approach / Why：** 先匹配 construct、dataset、policy、variant、scorer、分母与完整运行配置。  
> **Result / Check：** 只有共同设置才做直接比较；其他结果保留报告内解释。

## 可以这样回答

我会先读这列究竟是谁的成功。ASR 越低通常越好，capability pass rate 越高说明能力更强，honesty 可能越高越好，而 dishonesty 则相反。光看都是百分比没有意义。

接着看是否用同一套样本、policy 和 scorer；有没有移除 refusals、是否启用产品 guardrails、是否用不同 budget。被排除样本的比例也可能改变结果。

如果条件没对齐，我会说“各报告支持什么局部结论”，而不是给跨公司的全局安全名次。共同 benchmark 也只是一项证据，仍要看原任务 utility 与未覆盖风险。

## 报告实际采用证据

### Gray Swan IPI / historical ART

**类别：** external benchmark / competition-derived replay。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.1；PDF pp.84–85 · `external_evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2.6 / Figure 6.9；PDF pp.211–212 · `external_evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §5.2.1；PDF pp.83–84 · `external_evaluated`。历史名称 ART；与当前 IPI 分开

**读分数时看：** Attack success within k attempts；固定 Q1/Q2、场景集、model endpoint 与 safeguards。

**适用范围：** ART 与后续 IPI 的版本、surface 与 k 可能改变，不能直接合并历史 scores。

### MASK / MASK-Rectified

**类别：** public benchmark + provider adaptation。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.5.4.2；PDF p.130 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §11.1；PDF p.26 · `evaluated_adapted`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §12.1；PDF p.38 · `evaluated_adapted`。

**读分数时看：** Stated belief 与 pressured response 的 contradiction / honesty；记录 exclusions。

**适用范围：** MASK-Rectified 修改 roleplay 判定；不同评分版本和方向不能直接对比。

### Harmful / benign / multi-turn refusal suites

**类别：** provider-specific internal evaluation families。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §4.1；PDF pp.61–65 · `evaluated`。
- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §3.1 / §4.1 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §4 / §5.6.1 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §9；PDF pp.24–25 · `evaluated`。

**读分数时看：** Harmful compliance 与 benign refusal 同时报，按 policy areas 分开。

**适用范围：** 不是一套全球统一的 harmful-prompts benchmark，不用不同 provider 的百分比直接横比。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 挑同名 benchmark 的两个官方结果，填写 dataset/variant/scorer/budget/endpoint/denominator 对照表。
- **Baselines / Controls：** 先在共同子集与相同设置比较；另列按原报告配置的趋势。
- **Metrics / Interpretation：** 对缺失字段标 unknown，报告 uncertainty、utility、cost 与不能比较的原因。

## 追问与容易误判的地方

同一报告展示竞争模型的分数，也可能是作者自己的复测或取自另一报告，来源关系需要保留。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
