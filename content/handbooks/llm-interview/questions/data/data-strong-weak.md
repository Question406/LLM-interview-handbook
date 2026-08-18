---
id: data-strong-weak
section: data
order: 12
level: A
title: Strong-to-Weak Distillation 什么时候有效？什么时候会失败？
quick: >-
  Teacher 能提供 student 自己难以搜索到但仍可模仿的高质量 trajectory 时有效；若 teacher reasoning 超出
  student capacity、风格过长、依赖不可见工具/知识或分布不匹配，直接 imitation 可能失败。
tags:
  - Distillation
  - Data
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Teacher 能提供 student 自己难以搜索到但仍可模仿的高质量 trajectory 时有效；若 teacher reasoning 超出 student capacity、风格过长、依赖不可见工具/知识或分布不匹配，直接 imitation 可能失败。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>蒸馏有效需要 <b>teacher signal 可学</b>。强模型产生的 final answer 很好，不代表每个 token 都是最佳 supervision。可通过 simplification、rationale compression、difficulty filtering、student-aware rejection sampling 把数据推回 student learnable frontier。</p><p>一个实用方法是用 student likelihood / success rate 衡量 teacher trace 的“可学性”：完全不可能复现的 trajectory 先通过 curriculum 或分解 task，而不是直接塞进 SFT。</p></div>
