---
id: arch-decoder-only
section: arch
order: 18
level: A
title: 为什么大多数生成式 LLM 使用 Decoder-only？
quick: >-
  Decoder-only 用统一 causal next-token objective 覆盖预训练、续写、对话和 in-context
  learning，数据格式简单、scale 方便；encoder-decoder 在条件输入/输出分离任务上仍有优势。
tags:
  - Transformer
  - Architecture
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Decoder-only 用统一 causal next-token objective 覆盖预训练、续写、对话和 in-context learning，数据格式简单、scale 方便；encoder-decoder 在条件输入/输出分离任务上仍有优势。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Decoder-only 所有 tokens 在同一 stream，用 causal mask 学 p(x_t|x_{<t})。大规模互联网文本无需人工构造 source/target pair，训练 pipeline 简单。</p><p>Encoder-decoder 能让输入 bidirectional encode，再 cross-attend 输出，在翻译/摘要等固定条件生成任务可能更高效；但通用 chat/reasoning 生态更偏 decoder-only。</p></div>
