---
id: drustz-c5f35d3ab2c3f69238
section: forum-notes
order: 233
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Common Follow-Ups
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Common Follow-Ups
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
## Common Follow-Ups

### 1. Why use squared distance instead of Euclidean distance?

Because square root is monotonic:

```text
argmin_i ||q - x_i|| = argmin_i ||q - x_i||^2
```



Squared distance is easier to vectorize and algebraically rewrite into an affine form.

### 2. Where did the `||q||^2` term go in Part 2?

It does not affect the `argmin` over training examples because it is the same constant for every candidate `i` for a fixed query.

### 3. Why does softmax not change the answer?

Softmax is monotonic with respect to each input coordinate when the others are fixed, so the index of the largest logit remains the index of the largest probability.

### 4. What shape mistakes commonly happen?

- Forgetting `keepdims=True` for query norms and ending up with broadcast errors
- Mixing up `(n, d)` vs `(d, n)` when building the affine layer
- Applying softmax over the wrong axis
- Forgetting that `b` should broadcast across the batch dimension

### 5. How would you scale this up?

- Chunk the query batch to reduce peak memory
- Use approximate nearest-neighbor methods for very large `n`
- Normalize vectors first if the interviewer pivots to cosine similarity

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100237*)

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
