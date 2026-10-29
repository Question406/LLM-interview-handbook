---
id: drustz-7c13a2efc8a5199ee6
section: openai
order: 76
level: A
title: Debug a MiniGPT Transformer and Implement KV Cache (PyTorch)
quick: >-
  original-structured-preparation-guide · Debug a MiniGPT Transformer and
  Implement KV Cache (PyTorch)
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
      https://www.1point3acres.com/interview/problems/1c94c41d-587d-4c4f-b98d-95d376048c0e
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Debug MiniGPT 并实现 KV Cache

> 原始 starter code 未公开。旧正文只有通用 Transformer bug hunt，没有完成标题要求的 KV cache；这里补成完整准备指南。

## 先修正确性

固定 seed，使用 `eval()`、greedy decode 和极小输入。逐层断言 Q/K/V shape、`1/sqrt(head_dim)`、causal mask 在 softmax 前应用、softmax 沿 key 维、residual/LayerNorm、position id 和 next-token target shift。

## KV Cache 接口

```text
forward(input_ids, past_key_values=None, use_cache=False)
past_key_values[layer] = (K, V)  # [B,H,past_len,Dh]
```



prefill 处理完整 prompt 并返回每层 K/V；之后每步只输入新 token，计算新 K/V 后与历史拼接或写入预分配 buffer。position id 从 `past_len` 开始；cached causal mask 要让第 `i` 个新 query 看到 `past_len+i` 之前的 key。

## 必做验证

同一模型、输入和decoding参数下，cached 与 non-cached 每步 logits 应在容差内一致，greedy 结果完全相同。还要比较 batch padding、多个新 token、不同 prompt 长度和 cache 重用。

## 复杂度与边界

单步decoding避免反复计算历史 K/V，使每层 token 的投影/attention 从重算整个前缀降为只处理新 query；总 decode 仍需让新 query 读取历史 key。缓存空间每层 `O(B*H*T*Dh)`。覆盖空 prompt、最大位置长度、cache batch/device/dtype 不匹配、FP16 误差和 cache 截断。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1c94c41d-587d-4c4f-b98d-95d376048c0e)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
