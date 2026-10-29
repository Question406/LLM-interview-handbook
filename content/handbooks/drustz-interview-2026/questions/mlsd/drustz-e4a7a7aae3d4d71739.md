---
id: drustz-e4a7a7aae3d4d71739
section: mlsd
order: 101
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 17. 延伸阅读
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 17. 延伸阅读
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md
    type: primary
---
## 17. 延伸阅读

| 资料 | 分钟 | 用途 |
|---|---|---|
| [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) | 30 | position bias、冗长偏差、80% 人类一致率的出处。**本篇最核心的一篇** |
| [Length-Controlled AlpacaEval](https://arxiv.org/abs/2404.04475) | 20 | length bias的量化与 LC 回归做法 |
| [Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates](https://arxiv.org/abs/2410.07137) | 15 | judge 可被定向刷爆的证明（86.5% LC win rate） |
| [LLM Evaluators Recognize and Favor Their Own Generations](https://arxiv.org/abs/2404.13076) | 20 | 自我偏好与自我识别的相关性 |
| [A Careful Examination of LLM Performance on Grade School Arithmetic (GSM1k)](https://arxiv.org/abs/2405.00332) | 20 | 污染的最佳量化证据（8–13pp） |
| [Proving Test Set Contamination in Black Box Language Models](https://arxiv.org/abs/2310.17623) | 20 | 顺序似然（exchangeability）检验，黑盒污染检测 |
| [Prediction-Powered Inference](https://arxiv.org/abs/2301.09633) | 25 | §10.3 那个估计量的出处，成本章节的技术亮点 |
| [tinyBenchmarks](https://arxiv.org/abs/2402.14992) | 15 | IRT 选题压缩 benchmark，对应 §10.2 / §10.4 |
| [XSTest: 识别over-refusal](https://arxiv.org/abs/2308.01263) | 15 | over-refusal测例的标准参考 |
| [StrongREJECT](https://arxiv.org/abs/2402.10260) | 20 | ASR 被高估的机制，安全评测必读 |
| [Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548) | 25 | 人类偏好数据本身奖励讨好 |
| [OpenAI · Expanding on what we missed with sycophancy](https://openai.com/index/expanding-on-sycophancy/) | 12 | §9.2 那个案例的一手复盘，在线评测章节必引 |
| [Chatbot Arena / LMArena style control 说明](https://lmarena.ai/) | 10 | 格式偏差被正式承认并做统计校正的例子 |
| [07 §8 · 预训练侧 decontamination pipeline](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) | 10 | 本篇 §6 的上游对应 |
| [08 · 通用 eval / production](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) | 15 | 本篇不重复的通用部分 |

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
