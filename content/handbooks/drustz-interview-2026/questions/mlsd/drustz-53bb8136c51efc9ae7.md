---
id: drustz-53bb8136c51efc9ae7
section: mlsd
order: 63
level: A
title: 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 二十一、延伸阅读（按面试价值排序）
quick: 作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 二十一、延伸阅读（按面试价值排序）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md
    type: primary
---
## 二十一、延伸阅读（按面试价值排序）

1. [FineWeb paper](https://arxiv.org/abs/2406.17557) 与 [FineWeb processing write-up](https://huggingfacefw-blogpost-fineweb-v1.static.hf.space/index.html)：96 个 Common Crawl snapshots、filter/dedup ablation、FineWeb-Edu。
2. [DataComp-LM](https://proceedings.neurips.cc/paper_files/paper/2024/hash/19e4ea30dded58259665db375885e412-Abstract-Datasets_and_Benchmarks_Track.html)：固定训练/eval 框架比较 filter、mixture 与 data design。
3. [Dolma](https://aclanthology.org/2024.acl-long.840/) 与 [Dolma toolkit](https://allenai.github.io/dolma/)：open corpus、可复现 curation pipeline 与数据文档。
4. [The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)：大规模 pretraining data filtering、mixture、tokenizer、scaling 的系统案例。
5. [DoReMi](https://arxiv.org/abs/2305.10429)：用 proxy model + group DRO 优化 domain mixture。
6. [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)：参数、tokens 与固定 compute 的联合规划。
7. [The Stack](https://arxiv.org/abs/2211.15533) 与 [BigCode data governance](https://www.bigcode-project.org/docs/about/the-stack/)：permissive code、provenance、near dedup、opt-out/removal。
8. [ROOTS](https://arxiv.org/abs/2303.03915)：多语言 composite corpus 与 governance/documentation。
9. [RedPajama-V2](https://github.com/togethercomputer/RedPajama-Data)：raw artifacts、quality signals 与 dedup 分离的开放实现。

阅读方法：对每篇只回答六个问题——raw pool 是什么、rights/provenance 如何记录、filter/dedup 具体做了什么、用什么 proxy 选方案、下游怎么评、作者承认什么 limitation。不要只背最终 token 数。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
