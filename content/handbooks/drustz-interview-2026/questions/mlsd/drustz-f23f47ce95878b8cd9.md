---
id: drustz-f23f47ce95878b8cd9
section: mlsd
order: 107
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 4. 指标先于方案：这条 pipeline 怎么算成功 ⭐⭐⭐
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 4. 指标先于方案：这条 pipeline 怎么算成功 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 4. 指标先于方案：这条 pipeline 怎么算成功 ⭐⭐⭐

### 4.1 先说不能用的指标

| 常见但错的指标 | 为什么错 |
|---|---|
| **产出了多少条数据** | 最容易刷，且和梯度信号完全正交。一百万条全对的题价值为 0 |
| **LLM 打的平均质量分（1–5）** | 「题目写得好」和「有梯度信号」是两个维度。一道措辞完美的送分题质量分 5.0、价值 0 |
| **训练时的 pass rate 上升** | 三种解释：真变强 / 难度筛太松 / verifier 被 hack。**单看它无法区分**，必须配合下游 eval 和长度曲线 |
| **judge 平均分** | judge 会漂移、会被风格骗（§9.3）。作为主指标等于把方向盘交给一个没calibration的模型 |
| **verifier 通过率** | 同上，它是被优化的对象，不能同时当尺子（Goodhart） |

### 4.2 该用的分层指标

| 层 | 指标 | 说明 |
|---|---|---|
| **数据产出（快，小时级）** | **有效梯度产出率** = 一个 batch 里非退化组的比例 = `1 − P(全对) − P(全错)` | 这是本篇的核心指标。它直接量化「多少 rollout 算力换来了非零 advantage」 |
| | **有效 token 效率** = 产生非零 advantage 的 rollout token / 总生成 token | 把上一条换算成钱 |
| | **保留率 yield** = 通过全部 gate 的 prompt / 候选 prompt | 决定单位经济学。**yield 太高（>0.9）说明 gate 太松，太低（<0.2）说明供给侧选错了源** |
| | **每条可用 prompt 的成本** | `(C_合成 + C_探测 + C_去污 + C_人工抽检) / yield` |
| **训练动态（天级）** | 组内 reward 方差的分布、策略熵、平均生成长度、truncation 率 | 熵坍缩和长度爆炸是最早的预警信号（§14） |
| **模型质量（周级，最终裁判）** | **固定 compute 下的下游 eval 提升 per GPU-hour** | 唯一能证明「这批数据有用」的方法：加这批 vs 不加的等算力 A/B。对应 [07 §13](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) 的 data ablation ladder |
| **Guardrail** | 与 eval 集的污染率、prompt 重复率、**verifier 假阳性抽检率**、长度中位数、成本/步 | 假阳性抽检率是唯一能提前抓住 reward hacking 的离线指标 |

### 4.3 一句高分句

> 我不会用「产出了多少条数据」汇报。我报的是**有效梯度产出率**——一个 batch 里既不是全对也不是全错的组占多少。这个数字直接可以换算成钱：如果它是 60%，意味着我 40% 的 rollout 预算生成的 token 对应的 advantage 恒等于 0，那些 GPU 小时是纯烧掉的。而它也是唯一一个能同时诊断数据侧（题太简单）和优化侧（熵坍缩）的指标。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
