---
id: drustz-ff1823dc484e161ed4
section: mlsd
order: 128
level: A
title: 17 · Case：设计合成数据生成系统 · 2. 指标先于方案：怎么算成功 ⭐⭐⭐
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 2. 指标先于方案：怎么算成功 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 2. 指标先于方案：怎么算成功 ⭐⭐⭐

### 2.1 唯一有效的证据

```text
固定：模型架构、tokenizer、优化器、总训练 token / FLOPs、eval suite 版本、随机种子（最好多个）
变量：只有"是否加入这批合成数据"（或配比 x%）
结论：在【纯真实】的 held-out / prospective 集上的下游指标差异
```



这就是 [07 §13.2](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) 那套 ablation 规范在合成数据上的落地。**没有 matched-compute ablation 的合成数据结论都是猜。**

### 2.2 不能用的指标（面试里主动列出来）

| 常见但错的指标 | 为什么错 |
|---|---|
| **generator 自评分 / "这条题质量 9/10"** | 生成和评分是同一个模型（或同族），偏好高度相关。它在给自己打分 |
| **LLM judge 的平均分上升** | judge 偏好长度、格式、礼貌、自身写作风格。分数升了可能只是学会了讨好 judge。judge 只能做 triage 和排序，不能当 ground truth（[07 §13.3](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)） |
| **人评"看起来像真人写的"** | 真实性 ≠ 有用性。最像真实分布的合成数据往往信息增益最低（它只是复述你已有的东西） |
| **多样性分数（distinct-n / self-BLEU）单看** | 把温度调到 2.0 可以让任何多样性指标变好，同时让质量崩掉。多样性必须**在质量闸门之后**测 |
| **生成条数 / token 数** | 这是产能不是价值。1000 万条全对全错的题在 RL 里价值是 0（§5） |
| **验证集 loss 下降** | 如果验证集也含合成数据，这就是自证。真实 held-out 必须 100% 真实 |

### 2.3 验收合同（acceptance contract，开工前写死）

在生成一条数据之前，先把这份东西写下来并让对方签字：

```text
1. 主指标：目标域真实 held-out 上的 <具体指标>，相对 baseline 提升 ≥ X%（给绝对值和置信区间）
2. Guardrail：通用能力回归 ≤ Y%；目标 slice 提升不能以头部 slice 退化换取
3. 污染：与所有 eval 集的 n-gram / embedding 近重复率 ≤ Z（且报告检测方法，不承诺"零污染"）
4. 多样性下限：taxonomy 网格覆盖率 ≥ A%，每格最少 N 条；embedding 聚类熵 ≥ B
5. Provenance：每条样本可追溯 generator / checkpoint / prompt 版本 / seed / 闸门通过记录
6. 成本上限：每条【通过闸门】的样本成本 ≤ $C（注意分母，见 §11）
7. 失败判据：ablation 不显著就是不显著，写进报告，不补测到显著为止
```



第 7 条来自我在 Anthropic take-home 里的做法：两个被数据推翻的先验（refuted prior）我如实写进了报告。**主动说"我会预先定义失败判据"，比任何漂亮设计都更能证明是个能被信任的数据人。**

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
