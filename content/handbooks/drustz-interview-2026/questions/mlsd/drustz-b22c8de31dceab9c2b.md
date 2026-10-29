---
id: drustz-b22c8de31dceab9c2b
section: mlsd
order: 55
level: A
title: >-
  07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十三、如何证明 data
  有用：scaling、ablation 与 evaluator independence ⭐⭐⭐
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十三、如何证明 data
  有用：scaling、ablation 与 evaluator independence ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md
    type: primary
---
## 十三、如何证明 data 有用：scaling、ablation 与 evaluator independence ⭐⭐⭐

### 13.1 Data experiment ladder

```text
static statistics + human samples
  → tiny LM smoke test
  → proxy LM matched-compute ablations
  → scaling across ≥2 model/token scales
  → selected full-scale confirmation
  → downstream/post-training/production validation
```



### 13.2 一次合格的 ablation

要固定：

- architecture、tokenizer、optimizer/schedule；
- total training tokens 和 approximate FLOPs；
- sampling seed（最好多 seed）；
- eval suite/version；
- base raw pool，除被研究变量外其余 pipeline 相同。

例：比较 dedup A/B：

```text
A: global cross-snapshot MinHash dedup
B: per-snapshot MinHash dedup

Both:
  same 1.3B model, 30B train tokens, tokenizer, LR schedule
  when B has fewer unique tokens, define repeat policy explicitly

Report:
  per-domain val loss
  downstream capability
  memorization/extraction
  source/language retention
  processing cost + final unique tokens
```



### 13.3 不要用大模型 judge 替代训练实验

LLM quality scores 很便宜，可做 triage，但它可能偏好自身写作风格。真正 data value 是：在控制其他变量后，训练出来的模型在独立 target distribution 上更好。

Judge 的正确位置：

- 标注边界/active learning；
- 生成多维 quality signals；
- human-calibrated audit；
- 不是最终 ground truth。

### 13.4 Proxy model 外推风险

小模型喜欢的数据不一定让大模型获益：capacity、memorization、emergent tasks 和 optimizer dynamics 不同。做法：

- 至少两个 proxy scales 和 token budgets；
- 看 mixture/filter ranking 是否稳定；
- top candidates 在更大 scale 复验；
- 报 confidence interval/seed variance；
- 不把 0.2% 单 seed 提升写成确定结论。

### 13.5 指标组合

| 维度 | 指标 |
|---|---|
| LM fit | overall + per-domain validation loss/perplexity |
| Target capability | code/math/multilingual/retrieval/domain fresh eval |
| General retention | broad clean held-out suite |
| Data efficiency | quality at fixed tokens/FLOPs；tokens-to-target |
| Memorization | canary exposure、membership/extraction、rare-sequence recall |
| Safety/privacy | PII/secret extraction、toxicity/bias slices |
| Diversity | source/language/topic/entity distribution、effective unique tokens |
| Operations | bytes/tokens retained、CPU/GPU hours、cost/TB、pipeline failure |

### 13.6 Scaling study

在多个 `N, D` 上拟合经验关系，而不是直接套别家公司曲线：

\[
L(N,D) \approx L_\infty + \frac{A}{N^\alpha}+\frac{B}{D^\beta}
\]

Mixture/quality 变化会改变常数和有效数据量。真正决策通常是：固定总训练+未来 inference 成本，选择 `N, D, mixture` 的 Pareto point。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
