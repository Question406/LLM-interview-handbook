---
id: drustz-cde1fbe5b3a12bcda8
section: mlsd
order: 53
level: A
title: >-
  07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十一、Tokenizer 与 sequence
  construction
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十一、Tokenizer 与
  sequence construction
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
## 十一、Tokenizer 与 sequence construction

### 11.1 Tokenizer 选择

常见 subword：BPE、Unigram；现代系统通常有 byte fallback，避免 `<unk>`。需决定：

- vocab size；
- normalization；
- whitespace/newline 处理；
- special tokens；
- language/code sampling；
- byte fallback；
- reserved tokens for post-training/tools/multimodal。

### 11.2 关键 trade-off

| 选择 | 好处 | 代价 |
|---|---|---|
| 大 vocab | 常见词更短、sequence 少 | embedding/output 参数和 memory 大；长尾 token 学不充分 |
| 小 vocab | 参数省、组合泛化 | sequence 长、训练/推理 FLOPs 上升 |
| English-heavy training | 英语 fertility 好 | 多语言/代码被拆得很碎 |
| Aggressive normalization | 减少表面变体 | 丢代码、实体、语言差异 |
| Byte fallback | 任意字符可编码 | rare scripts 可能 token 很长 |

**Fertility** 可用每词/每字符 token 数表示；按 language、code、math、emoji、OCR noise 分 slice。Tokenizer 本身改变每个 source 的 token mixture，所以 mixture 统计必须在最终 tokenizer 下重算。

### 11.3 Train tokenizer 的数据

- 从目标 mixture stratified sampling，而非直接从最大 web pool 随机抽。
- 限制 domain/site 重复，防 tokenizer 记住 boilerplate。
- 包含所有目标 scripts、code whitespace、math symbols。
- 单独 held-out 测 compression/fertility、round-trip、normalization collision。
- Tokenizer 一旦大规模训练开始应锁 version；更换 tokenizer 不是普通 config update。

### 11.4 Packing

目标是减少 padding，提高 GPU utilization：多个 document 拼成 fixed-length sequences。

需要明确：

- document boundary token；
- attention 是否跨文档（通常 causal LM 可跨但可能学习伪关系；可用 mask/position reset，取决实现）；
- 不切断特殊结构/代码文件，或记录 continuation；
- long document chunk overlap 是否制造重复；
- validation packing 与 training 一致但样本独立。

Long-context curriculum 应保留真实结构连续性（书、repo、thread、paper），而不是仅把随机短文 packing 到 128K。

### 11.5 Code FIM

从一个 code file 采 prefix/middle/suffix，序列可为：

```text
<PRE> prefix <SUF> suffix <MID> middle
```



FIM rate、span length、repo/file boundaries 需 ablation。Tests/definitions/import context 可增强，但避免同 repo 跨 train/eval。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
