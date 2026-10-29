---
id: drustz-90d6dc3cbd9fcf2ac0
section: forum-notes
order: 81
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · The Design Problem
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · The Design Problem
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## The Design Problem

**Goal:** Design a "playground" tool for Prompt Engineering, similar to the OpenAI Playground or Anthropic Console. This is a **full-stack system design** question. You need to focus on product features, how the UI looks, how the code works, and how it scales.

### What is Prompt Engineering?

**Prompt engineering** means testing and changing input text (prompts) to get the best result from an AI model.

- **Not a Chatbot:** This is not like ChatGPT. There is no conversation history.
- **Independent Runs:** Every time you click "Run," the model starts fresh. It has no memory of the previous run.

### Example User Flow

- **Write:** A user types: "Write a recipe."
- **Refine:** They change it to: "You are a chef. Write a recipe for pasta."
- **Test:** They add examples of good recipes to help the model.
- **Repeat:** They keep changing the prompt until the result is perfect.
- **Save:** They save the best version to use later.

### Follow-up Questions

The interviewer might ask about these harder topics:

- **Scale:** How do we handle 10MB text files?
- **Versions:** How do we track changes if a user saves 1000 times?
- **Cost:** How do we stop users from spending too much money on the LLM API?
- **Search:** How do you search through huge text documents?

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
