---
id: drustz-560a5e95bfd1c99c6f
section: mlsd
order: 49
level: A
title: >-
  07 · Pre-training Data Systems：从原始网页到可审计训练 tokens ·
  七、Filtering：规则、分类器、模型评分如何组合 ⭐⭐⭐
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens ·
  七、Filtering：规则、分类器、模型评分如何组合 ⭐⭐⭐
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
## 七、Filtering：规则、分类器、模型评分如何组合 ⭐⭐⭐

### 7.1 Filter funnel

```text
malformed / unsupported MIME
  → language + encoding
  → policy/safety/PII/secrets
  → structural heuristics / repetition / boilerplate
  → spam / quality classifiers
  → domain-specific filters
  → dedup / contamination
  → retain signals for mixture weighting
```



不是所有 signal 都要 hard drop。可分：

- `BLOCK`：权利/安全硬约束。
- `DROP`：高置信垃圾/损坏。
- `DOWNWEIGHT`：低质量但可能有长尾价值。
- `REVIEW/QUARANTINE`：不确定、高风险。
- `KEEP + TAG`：保留并用于 mixture/slice。

### 7.2 Heuristic signals

- document/line length；
- alphabetic/number/punctuation/symbol ratio；
- repeated lines/paragraphs/n-grams；
- average word/sentence length；
- stopword/function-word proportion；
- terminal punctuation；
- HTML/JavaScript residue；
- URL/domain patterns；
- lorem ipsum、SEO keyword stuffing；
- code/text ratio、comment ratio；
- OCR confidence/gibberish。

规则便宜、可解释，但跨语言/domain 不可直接复用。每个阈值做 sweep + human sample + proxy train ablation，不要复制另一个 corpus 的 magic number。

### 7.3 Learned quality classifier

一种常见方法：用高质量 reference（百科、教材、精选文章等）为 positives，随机 web 为 negatives，训练 fastText/small transformer/LLM classifier。

风险：

- classifier 学到 source/style，而不是 knowledge utility；
- “像 Wikipedia”会压制口语、论坛、dialect 和新领域；
- random web negatives 太容易，线上 tail calibration 差；
- 用 LLM 评分会继承其语言/政治/文化偏差；
- threshold 把 continuum 伪装成 truth。

改进：

1. 人工 rubric 区分 coherence、information density、originality、instructional value、factual/support quality。
2. 每个 language/domain 单独 sampling 和 calibration。
3. Hard negatives 加入流畅但错误/SEO/AI-slop；positives 加入真实 forums、minority styles。
4. 输出 calibrated score + uncertainty，很多场景 downweight 比 hard drop 更稳。
5. Human blind audit kept/dropped boundary cases。
6. 以固定 compute proxy LM downstream 作为最终验证。

FineWeb-Edu 和 DCLM 的重要启示不是“LLM classifier 永远最好”，而是：**data filtering decisions 需要以训练后能力做受控实验；model-based quality filtering 可以很强，但必须calibration和审计其selection bias。**

### 7.4 Safety、PII 与 secrets

多层检测：

```text
deterministic regex/checksum (emails, phones, keys, cards)
  + NER/contextual PII model
  + secret scanners / entropy / known key formats
  + source-level policy
  + human red-team test set
```



区分：公开机构电话 vs 私人电话；虚构示例 vs 真实 secret；medical/legal context。可采取 redact、drop document、quarantine、source block。记录 span 和 reason，但检测结果本身也是敏感 metadata，要限权。

PII recall 优先时会有 false positives；按风险类别设置阈值，不用一个 global F1 决定所有处理。训练后还要做 canary/membership/extraction tests，因为过滤器通过不代表不会 memorization。

### 7.5 Bias 与 representational harm

“clean”经常隐含标准书面英语/主流文化。要报告：

- 各语言/dialect/source 的保留率；
- 人口群体相关文本的 false-positive filter rate；
- geographic/domain concentration；
- toxicity/hate 的 context：研究/反驳/引用是否被误删；
- 被删样本的分层 human audit。

安全过滤与能力数据可以做 policy-separated pools，不代表所有研究模型都用同一 mixture。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
