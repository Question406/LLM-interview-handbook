---
id: drustz-efd7465ad6c5b1a38e
section: forum-notes
order: 235
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · The Problem
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · The Problem
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## The Problem

You have an `n × m` grid that represents a group of people. Each spot in the grid is a person. They are either **healthy** (`0`) or **infected** (`1`).

The infection spreads based on a simple rule:

- **A healthy person gets infected if they have at least `N` infected neighbors.**
Neighbors are the 4 people directly next to them (up, down, left, right). We do not count diagonals.

Your job is to find out **how many time steps** it takes for everyone in the grid to get infected. If it is impossible to infect everyone, return `-1`.

This is similar to the Game of Life, but here we focus on how a virus spreads.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
