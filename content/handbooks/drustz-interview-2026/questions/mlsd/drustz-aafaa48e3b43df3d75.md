---
id: drustz-aafaa48e3b43df3d75
section: mlsd
order: 46
level: A
title: >-
  07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 四、Data
  acquisition：从哪里来，以及如何管理权利 ⭐⭐⭐
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 四、Data
  acquisition：从哪里来，以及如何管理权利 ⭐⭐⭐
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
## 四、Data acquisition：从哪里来，以及如何管理权利 ⭐⭐⭐

### 4.1 Source portfolio

| Source | 价值 | 风险/偏差 | 需要保留的 metadata |
|---|---|---|---|
| Web crawl / Common Crawl | 规模、长尾、时效 | spam、重复、未知权利、PII、网页模板 | URL、crawl/fetch time、WARC offset、HTTP headers、robots/terms snapshot |
| Wikipedia / public knowledge | 高结构、事实密度、多语言 | 风格单一、覆盖偏差 | revision ID、license、language |
| Public-domain/licensed books | 长文、叙事、知识 | OCR、版本/许可、文化偏差 | edition、rights basis、page/section |
| Scientific papers | technical reasoning、公式 | PDF extraction、版权、引用结构 | DOI、publisher/license、version、sections |
| Documentation/forums/Q&A | procedural knowledge、真实问题 | 许可、用户 PII、低质量回答 | thread/revision、author visibility、license |
| Code repositories | syntax/API/SE patterns | license、secrets、vendored/generated code、malware | repo/commit/path、SPDX、fork lineage |
| First-party/customer data | 产品分布、独特价值 | consent、purpose limitation、tenant leakage | consent/purpose、tenant、retention、access policy |
| Licensed publisher/vendor data | 高质量、稳定 | 成本、scope/term 限制、续约 | contract/version、allowed uses、expiration |
| Synthetic data | 稀有能力、可控 rubric | model collapse、teacher bias、contamination | generator/judge/prompt/version、seed、provenance |
| Human-created curriculum | 高难度、目标明确 | 贵、规模小、annotator bias | rubric、annotator/adjudication、rights |

### 4.2 Crawl 系统需要讲的组件

```text
seed URLs / sitemap / feeds / discovered links
  → URL frontier (priority, host, next_fetch_at)
  → robots/terms/policy check
  → per-host politeness + DNS/HTTP fetch
  → immutable response/WARC + metadata
  → link extraction + canonicalization
  → recrawl scheduler based on change rate/value
```



重要设计：

- URL canonicalization 去 tracking parameters、fragment，处理 redirects/canonical tags；但不能把有语义的 query parameters 全删。
- Per-host rate limit、robots、legal/policy registry、deny/allow list。
- Content hash 判断 change；按 domain/URL 历史变化率安排 recrawl。
- Raw bytes immutable，parser bug 修复时不用重新抓取。
- HTML status、MIME、encoding、fetch time、IP/region、response headers 进入 provenance。
- Tombstone/deletion event 不能只删除 catalog row；要能定位所有 derived docs/shards 和未来 dataset release。

### 4.3 Licensing / consent 不是一个 boolean

推荐 rights record：

```text
RightsRecord
  source_id, asset_id, owner/provider
  legal_basis_or_license_id
  allowed_purposes: [research, commercial_train, redistribution, eval]
  geography, effective_at, expires_at
  attribution_required, share_alike, opt_out_path
  policy_review_version, evidence_pointer
```



一个 URL “公开可访问”不自动等于可用于任何商业训练。具体判断交给 legal/privacy/security；ML system 的责任是保留证据、执行 policy、隔离未知权利数据，并能响应删除/期限变化。

对于 code，每个 repository/file 的 license、fork/vendor lineage、attribution 可能不同。The Stack 的做法值得作为治理案例：保留逐样本 provenance、选择 permissive licenses，并提供 opt-out/removal 流程；不是说它解决了所有法律问题。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
