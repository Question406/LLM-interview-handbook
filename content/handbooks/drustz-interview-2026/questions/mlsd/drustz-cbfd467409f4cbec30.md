---
id: drustz-cbfd467409f4cbec30
section: mlsd
order: 132
level: A
title: 17 · Case：设计合成数据生成系统 · 6. 多样性 vs 质量的张力 ⭐⭐⭐
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 6. 多样性 vs 质量的张力 ⭐⭐⭐
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
## 6. 多样性 vs 质量的张力 ⭐⭐⭐

### 6.1 温度不是多样性旋钮

| 温度 ↑ 的四个后果 | 说明 |
|---|---|
| 表面多样性 ↑ | 用词、句式变化变大 |
| **语义多样性 ↑ 得很有限** | 还是那几个主题——因为主题由 prompt/seed 决定 |
| 质量 ↓ | 事实错误、格式错误、不可解题增多 |
| **闸门通过率 ↓ → 单位有效样本成本 ↑** | 这是关键：温度调高看似免费，实际把成本推到了漏斗里 |

**结论**：温度是在"生成成本"和"筛选成本"之间做交换，不是在制造新信息。要真正提升多样性，去改 seed、改 taxonomy、改 evol 算子。

### 6.2 多样性的正确来源（按杠杆从大到小）

1. **seed 的多样性**（最大杠杆）：从真实语料聚类出主题、从真实错误日志采集失败模式、从多个来源采集。
2. **条件维度的显式笛卡尔积**：主题 × 难度 × 语言 × 受众 × 文体 × 长度 × 干扰项类型。把这些写成结构化的生成配置，而不是塞进一句 prompt。
3. **evol 算子的多样性**：不同的变换算子（加约束 / 换领域 / 加干扰信息 / 改问法）。
4. **generator 的多样性**：用 2–3 个不同家族的模型生成，能显著打散单模型的风格指纹。
5. **sampling温度**（最小杠杆，且有副作用）。

### 6.3 去重：合成数据和真实数据的去重不一样

通用机制（exact hash → MinHash/LSH near-dup → embedding 语义去重）在 [07 §六](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)，这里只讲**差异**：

| 差异点 | 说明 |
|---|---|
| **合成数据的重复是"模式重复"不是"字符串重复"** | 两条题换了人名和数字，字符串距离很大，但对模型是同一条。exact/MinHash 抓不到 |
| 因此必须做 **embedding 层的近邻去重 + 聚类去重** | 对每条新样本查 embedding 近邻，相似度超阈值就丢；或者聚类后限制每cluster最大条数 |
| **还要对"骨架"去重** | 把数字、变量名、实体名normalization成占位符之后再做 exact/n-gram 去重——这一步能抓到模板化生成最典型的重复 |
| **Self-Instruct 的具体做法可以引用** | 新生成的指令与任何已有指令 ROUGE-L 相似度 > 0.7 就丢弃。一个便宜、有效、可直接说出数字的基线 |
| **必须对 seed 去重** | 合成样本和它的 seed 太像 = 没有增加信息，只是换了个说法（隐私场景下还是泄漏风险，§9） |
| **必须对所有 eval 集去重** | 合成数据是**污染的高危来源**：generator 可能记得 benchmark 题目并"重新发明"它们。exact match 不够，要做语义近重复检测（[07 §八](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)） |

### 6.4 覆盖度怎么量（四个可落地的指标）

| 指标 | 怎么算 | 读什么 |
|---|---|---|
| **taxonomy 网格填充率** | 预先定义维度网格（主题 × 难度 × 类型），统计非空格子比例 + 每格最少条数 | 最可解释、最能驱动行动。空格子直接告诉你下一批该生成什么 |
| **相对真实数据的聚类覆盖** | 在真实数据上跑 k-means（k=200～1000），把合成数据投进去，看每cluster的质量占比 | 空cluster = 真实分布里有而合成数据没覆盖的区域 |
| **新 n-gram 率** | 相对 seed 的新 n-gram 比例 | 太低 = 只是在复读 seed；太高 = 可能在胡说 |
| **self-BLEU / distinct-n** | 样本两两之间的相似度 | 便宜的模式坍塌告警。**必须在质量闸门之后算**，否则垃圾会让它虚高 |

**一句话**：我会把覆盖度做成一个**带空格告警的网格看板**，而不是一个标量分数——因为标量分数不能告诉团队下一步生成什么。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
