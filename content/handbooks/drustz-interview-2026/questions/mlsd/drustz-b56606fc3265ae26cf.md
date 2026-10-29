---
id: drustz-b56606fc3265ae26cf
section: mlsd
order: 47
level: A
title: >-
  07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 五、Extraction：坏 parser
  会比坏模型更早毁掉数据
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 五、Extraction：坏
  parser 会比坏模型更早毁掉数据
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
## 五、Extraction：坏 parser 会比坏模型更早毁掉数据

### 5.1 统一 document schema

```text
DocumentRecord
  doc_id, source_id, source_uri, fetched_at, published_at
  mime_type, language_probs
  title, sections[{heading_path, text, offsets, type}]
  tables/code/math/alt_text
  raw_blob_pointer, content_hash, parent_doc_id
  rights_record_id
  extractor_name/version/config
  quality/safety/pii signals
  dedup_cluster_id, canonical_doc_id
  filter_decisions[{stage, version, signal, threshold, action, reason}]
  lineage_parents, created_at
```



`doc_id` 应基于 immutable source/version；`content_hash` 用于内容相同判断；二者不要混为一谈。

### 5.2 HTML

- Decode encoding，保留 DOM/block structure。
- 去 nav、cookie banners、ads、footer、related links 等 boilerplate。
- 保留 headings、lists、tables、code blocks、alt text 与 link anchors。
- 识别 main content，但不要把短页面/论坛回答一刀切掉。
- 处理 JS-rendered content 要受资源/安全策略约束；不是每页开 headless browser。
- Parser output 抽样做 visual/text comparison，测 text coverage、boilerplate rate、order correctness。

### 5.3 PDF / scans / OCR

```text
native text extraction first
  → layout blocks / reading order
  → OCR only for image regions or scanned pages
  → tables/math/captions specialized extraction
  → confidence + bounding boxes + page provenance
```



OCR 置信度低、双栏顺序错、页眉页脚重复、公式乱码会产生“看似语言、实则噪声”的 token。按 page/block 保存 confidence，低质量 section 可以 filter 或降权，而不是整篇全留/全删。

### 5.4 Code

- 去 vendored/minified/generated/binary/notebook output。
- 解析 repo structure、language、file type；保留 path/import/test relationships。
- secret/credential scanner 在早期运行；malware/security policies 单独处理。
- fork dedup 要保留 canonical upstream 和 license。
- 可做 file-level、repo-level sequence；训练 FIM 时构造 prefix/suffix/middle，同时保证 split 不跨 repo 泄漏。

### 5.5 Normalization 要保守

可以统一 Unicode、换行和明显 encoding error，但要避免：

- lowercase 破坏代码/实体；
- 全删标点破坏句法/公式；
- 空白压缩破坏 Python/表格；
- language-specific normalization 抹除变音符号；
- 在 dedup 前做过强 normalization 导致不同内容碰撞。

保留 raw → normalized offset mapping，便于审计和引用。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
