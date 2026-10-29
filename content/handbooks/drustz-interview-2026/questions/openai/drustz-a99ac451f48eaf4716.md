---
id: drustz-a99ac451f48eaf4716
section: openai
order: 121
level: A
title: Debug a Transformer Implementation and Modify It into a Classifier
quick: >-
  original-structured-preparation-guide · Debug a Transformer Implementation and
  Modify It into a Classifier
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/2255b47c-b6fa-4797-a06c-ffb8391f30c2
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Debug Transformer 并改造成分类器

> 原始代码未公开。旧正文覆盖了常见 attention bug，但没有 classifier 改造，现补全该部分。

## 调试阶段

依次检查 Q/K/V reshape、缩放、mask、softmax 维、residual、LayerNorm、位置编码和 padding。先让极小 batch 能稳定overfitting，再改任务头。

## 分类器改造

移除 token vocabulary head，增加 `Linear(d_model, num_classes)`。聚合方式必须和接口一致：

- 有 `[CLS]`：取 `hidden[:,0]`；
- 无 `[CLS]`：做 mask-aware mean pooling，padding 不进分母；
- 若从 causal LM 变 encoder classifier，按题意移除 causal mask，只保留 padding mask。

返回原始 logits，训练用 `CrossEntropyLoss`，不要先 softmax。

```python
mask_f = attention_mask.unsqueeze(-1).to(hidden.dtype)
pooled = (hidden * mask_f).sum(1) / mask_f.sum(1).clamp_min(1)
logits = classifier(pooled)
```



## 复杂度与边界

self-attention `O(B*T²*d)`，pooling `O(B*T*d)`，分类头 `O(B*d*C)`。覆盖全 padding、空序列、超长位置、`num_classes=1`、label 越界和 dropout train/eval。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/2255b47c-b6fa-4797-a06c-ffb8391f30c2)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
