---
id: drustz-cf7c7fcdeaf5a1e055
section: mlsd
order: 143
level: A
title: 17 · Case：设计合成数据生成系统 · 17. 延伸阅读
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 17. 延伸阅读
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 17. 延伸阅读

| 资料 | 分钟 | 用途 |
|---|---|---|
| Self-Instruct（Wang et al. 2022, [arXiv:2212.10560](https://arxiv.org/abs/2212.10560)） | 25 | 自举生成指令的原始方法，ROUGE-L 0.7 过滤那个数字的出处 |
| WizardLM / Evol-Instruct（[arXiv:2304.12244](https://arxiv.org/abs/2304.12244)） | 20 | in-depth / in-breadth 进化算子 + 淘汰失败进化 |
| Self-Alignment with Instruction Backtranslation（[arXiv:2308.06259](https://arxiv.org/abs/2308.06259)） | 20 | 从真实文档反推指令 + self-curation，"反推"范式的代表 |
| WRAP · Rephrasing the Web（[arXiv:2401.16380](https://arxiv.org/abs/2401.16380)） | 20 | 改写真实网页做预训练加速 |
| Textbooks Are All You Need（phi-1，[arXiv:2306.11644](https://arxiv.org/abs/2306.11644)） | 25 | 教科书质量合成语料，小模型高性能的代表作 |
| HuggingFace Cosmopedia 博客 | 20 | **多样性来自 seed** 这条结论最实操的一手复盘 |
| Nemotron-4 340B 技术报告（[arXiv:2406.11704](https://arxiv.org/abs/2406.11704)） | 30 | 对齐数据 98%+ 合成；宽松许可用于合成数据 |
| **AI models collapse when trained on recursively generated data**（Shumailov et al., Nature 2024） | 30 | 模型坍塌的权威引用，早期/晚期坍塌与三类误差 |
| Is Model Collapse Inevitable?（[arXiv:2404.01413](https://arxiv.org/abs/2404.01413)） | 25 | **accumulate vs replace**，本篇 §7.2 的出处 |
| Self-Consuming Generative Models Go MAD（[arXiv:2307.01850](https://arxiv.org/abs/2307.01850)） | 20 | 自噬循环的生成模型版本，质量 vs 多样性的取舍 |
| Strong Model Collapse（[arXiv:2410.04840](https://arxiv.org/abs/2410.04840)） | 20 | 反面张力：小比例合成数据也可能有害。用来展示"我知道这事没有定论" |
| DAPO（[arXiv:2503.14476](https://arxiv.org/abs/2503.14476)） | 25 | dynamic sampling，§5 的文献对应 |
| STaR（[arXiv:2203.14465](https://arxiv.org/abs/2203.14465)） | 20 | verifier 驱动的自举，rejection sampling 家族的源头 |
| MAUVE（[arXiv:2102.01454](https://arxiv.org/abs/2102.01454)） | 20 | 生成分布与真实分布的散度度量 |
| The Secret Sharer（[arXiv:1802.08232](https://arxiv.org/abs/1802.08232)） | 25 | canary exposure，记忆泄漏测试的标准做法 |
| **本地** [07 · Pre-training Data](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) §六/§八/§十 | 40 | 去重、污染、数据短缺阶梯的通用机制，本篇的地基 |
| **本地** [labs/lab01_dedup_quality](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab01_dedup_quality/) | 60 | 跑一遍去重 + 质量分类器，比读十遍强 |
| **本地** [../projects/decagon_finetune/data/](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/data/README.md) | 20 | 我自己写的确定性合成语料生成器（含"区分度必须来自语义"的设计说明） |

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
