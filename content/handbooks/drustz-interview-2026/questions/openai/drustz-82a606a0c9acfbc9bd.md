---
id: drustz-82a606a0c9acfbc9bd
section: openai
order: 86
level: A
title: Implement Multi-Head Attention (NumPy or PyTorch)
quick: >-
  original-structured-preparation-guide · Implement Multi-Head Attention (NumPy
  or PyTorch)
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
      https://www.1point3acres.com/interview/problems/78579ab8-67cd-40c9-9a7c-892d7157cb14
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Multi-Head Attention（NumPy / PyTorch）

> 旧正文只有 Transformer bug checklist，没有实现 MHA。以下采用输入 `[B,T,D]`、头数 `H`、`D % H == 0`。

## Forward

1. 线性投影得到 Q/K/V；
2. reshape 为 `[B,T,H,Dh]`，transpose 到 `[B,H,T,Dh]`；
3. `scores = Q @ K.transpose(-1,-2) / sqrt(Dh)`；
4. softmax 前应用 padding/causal mask；
5. 沿 key 维做稳定 softmax，再乘 V；
6. transpose、合并 heads，经过 output projection。

```python
scores = q @ k.transpose(-1, -2) / math.sqrt(head_dim)
scores = scores.masked_fill(~mask, float("-inf"))
weights = torch.softmax(scores, dim=-1)
context = weights @ v
output = context.transpose(1, 2).contiguous().reshape(batch, query_len, model_dim)
```



交叉 attention 中 query/key 长度不同，不能假设方阵。PyTorch transpose 后 tensor 可能不连续，应使用 `reshape` 或 `contiguous().view()`。

## 复杂度与边界

attention 时间 `O(B*Tq*Tk*D)`，投影约 `O(B*T*D²)`，score 空间 `O(B*H*Tq*Tk)`。覆盖 D 不能整除 H、mask 广播与真假语义、全 mask 行、causal 方向、fp16、dropout train/eval。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/78579ab8-67cd-40c9-9a7c-892d7157cb14)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
