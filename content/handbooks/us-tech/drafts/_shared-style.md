# US Tech 真题写作规范（sub-agent 必读）

只写本手册题目。不要改 `_handbook.md`、不要改 `llm-interview`、不要改 `content/generated/`。

## 落盘

把 **published** 文件写到：

`content/handbooks/us-tech/questions/<section>/<id>.md`

`section` 必须是 prompt 里指定的模块 id。`id` 必须用 prompt 里给出的 kebab-case，不要自造、不要和已有 id 撞车。

## Front matter（逐字段）

```yaml
---
id: assigned-kebab-id
section: assigned-section
order: N
level: S  # 或 A / B
title: 公司：一句话题面
quick: >-
  30 秒结论，口语，不要空话。
tags:
  - Company
  - Topic
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: 真实标题
    url: https://...
    type: secondary
---
```

- `sources` 至少一个 **真实可访问** 的 `http(s)` URL。`type` 只能是 `candidate-first-hand` | `primary` | `secondary`。
- **不要编造** Exponent experience id、一亩三分地帖号。找不到第一手报告就 `realInterview: false`，用论文 / 官方博客 / 面经指南。
- 只有 URL 真是候选人报告时才把 `realInterview` 设为 `true`。
- `title` / `quick` 不能含 HTML。公式用 `$...$`。

## 正文结构

口语中文，第一人称讲「我会怎么答」。密度对齐现有卡（约 70–120 行，不要 20 行空壳）。

1. 若 `realInterview: true`：先写 **真题记录**（公司、岗位、轮次、来源、题面大意）。
2. 否则写 **题怎么来的**（哪类岗、为什么会问、和论文/产品的关系），不要假装有隐藏面经。
3. 中间分 2–4 个小标题讲答法、取舍、一个具体例子或 shape/公式。
4. 结尾 **追问** 2–4 条，每条先加粗问题再给短答。

## 硬限制

- **禁止 raw HTML。** 构建器用 `/<\/?[a-z][^>]*>/i` 扫描，`</w>`、`<div>`、`<B,T>` 都会挂。张量 shape 写 `[B, T, D]`，特殊 token 写「end-of-word 标记」或 `` `endofword` ``，不要写 XML 闭合标签。
- 公式只用 `$...$` / `$$...$$`。不要 Unicode 拼公式（`δₜ`、`ℝ`）。KaTeX `throwOnError`，非法命令会失败。
- 比较符号在公式里写 `$a < b$` 可以；不要写看起来像标签的 `<foo>`。
- 本手册内互链：只反引号 **本手册已有或本次会写的 id**。不要链 `code-attention`、`arch-gqa`、`pt-rlhf-why-reverse-kl` 等 llm-interview id（不会跳转）。代码标识符（`batch_size`）可以反引号。
- 不要用 `[[id]]` 或 `(question:id)`，除非你 100% 确定该 id 已存在。
- 不要写「作为 AI」「下面给出完整方案」这类套话。

## 内容标准

- 技术上要能过 Research Engineer / MLE 面试：有公式或复杂度或 shape，有错法，有取舍。
- 公司特色要写出来（OpenAI 爱 debug；Anthropic 爱分层实现；NVIDIA 爱 kernel/并行；Apple 爱端侧约束）。
- 代码可以给 15–40 行 Python 关键片段，不要贴一整份框架。
