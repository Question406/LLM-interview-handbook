---
id: arch-tokenizer
section: arch
order: 15
level: A
title: BPE、WordPiece、SentencePiece、Byte-level BPE 大致区别？
quick: >-
  BPE 迭代合并高频 symbol pairs；WordPiece 选择更偏 likelihood 增益的 subword；SentencePiece
  是可直接在 raw text 上训练的 tokenizer framework；byte-level BPE 从 bytes 出发，几乎无 OOV。
tags:
  - Tokenizer
  - Basics
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>BPE 迭代合并高频 symbol pairs；WordPiece 选择更偏 likelihood 增益的 subword；SentencePiece 是可直接在 raw text 上训练的 tokenizer framework；byte-level BPE 从 bytes 出发，几乎无 OOV。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>面试不必把 SentencePiece 说成一种独立 merge objective：它更像 tokenizer toolkit，可实现 Unigram/BPE，并把空格等当普通符号处理。</p><p>Byte-level 方法的优点是任意 Unicode 文本最终可映射 bytes，避免 unknown token；代价是某些语言/特殊字符 token 数更多。中文 tokenizer 的粒度会直接影响 sequence length、训练 compute、context utilization 和数字/代码处理。</p></div>
