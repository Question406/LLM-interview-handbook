---
id: drustz-9dd017d24faee79354
section: mlsd
order: 160
level: A
title: 18 · Case：设计大规模分布式推理系统 · 14. 延伸阅读
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 14. 延伸阅读
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md
    type: primary
---
## 14. 延伸阅读

| 资料 | 分钟 | 用途 |
|---|---|---|
| [vLLM / PagedAttention 论文（SOSP'23）](https://arxiv.org/abs/2309.06180) | 30 | KV 分页管理的原始出处，碎片 60–80% → <4% 的数据来源 |
| [Orca（OSDI'22）](https://www.usenix.org/conference/osdi22/presentation/yu) | 25 | continuous batching / iteration-level scheduling 的出处 |
| [Sarathi-Serve（chunked prefill）](https://arxiv.org/abs/2403.02310) | 20 | 为什么长 prefill 会毁掉 TPOT，以及分块怎么解决 |
| [DistServe（PD 分离）](https://arxiv.org/abs/2401.09670) | 25 | goodput 这个指标的出处；prefill/decode 分池的取舍分析 |
| [Speculative Decoding（Leviathan et al.）](https://arxiv.org/abs/2211.17192) | 20 | rejection sampling保证分布等价的证明 |
| [DAPO](https://arxiv.org/abs/2503.14476) | 20 | dynamic sampling——和 §4.2 的探测筛选同思想，面试可主动引用 |
| [Anthropic Message Batches API 文档](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | 10 | 批量 = 5 折、典型 1h / 上限 24h，"延迟的市场定价"这个论点的一手来源 |
| 本地 [`../online_resource/question-bank/theory-and-mlsd.md`](?book=drustz-interview-2026&section=collections&question=drustz-10114ff26622b3e07c) §553–582 | 30 | KV cache 估算、PagedAttention 手写题、prefill/decode physics 的题目集 |
| [08 · evaluation & production](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) | 15 | 上线、阈值、监控闭环的通用部分，本篇不重复 |

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
