---
id: data-contamination
section: data
order: 8
level: A
title: 怎么做 Benchmark Contamination 检测？
quick: >-
  不能只查 exact string。要从 exact/normalized overlap、n-gram/MinHash
  near-duplicate、semantic similarity、答案/解析泄漏、时间戳与 source provenance 多层检查。
tags:
  - Data
  - Eval
  - Contamination
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>不能只查 exact string。要从 exact/normalized overlap、n-gram/MinHash near-duplicate、semantic similarity、答案/解析泄漏、时间戳与 source provenance 多层检查。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可分四级：1) exact hash；2) normalization 后 exact；3) n-gram MinHash/LSH 发现局部改写；4) embedding / model-assisted semantic match。对于代码/数学，还应规范化变量名、格式和答案模板。</p><p>更重要的是 provenance：记录数据来源、抓取时间、是否包含 benchmark solution/review/blog。只检测 question text 不够，训练数据可能只有答案解析但仍会泄漏。</p><p>对高风险 benchmark 可以做 canary、held-out private variants、题目扰动、时间切分与生成式 leakage probe。</p></div>
