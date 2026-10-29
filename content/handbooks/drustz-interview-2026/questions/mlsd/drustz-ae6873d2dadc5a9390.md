---
id: drustz-ae6873d2dadc5a9390
section: mlsd
order: 117
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 14. 常见失败模式：这个系统最容易在哪坏掉 ⭐⭐⭐
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 14. 常见失败模式：这个系统最容易在哪坏掉 ⭐⭐⭐
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
## 14. 常见失败模式：这个系统最容易在哪坏掉 ⭐⭐⭐

按「我实际会先怀疑什么」排序：

| # | 症状 | 最可能的根因 | 诊断 |
|---|---|---|---|
| 1 | **训练 pass rate 上翘但下游 eval 不动** | verifier 假阳性被找到（§9.4） | 抽 reward 最高的 trace 人工看；比对隐藏测试 vs 公开测试 |
| 2 | **训到中期梯度「消失」，loss 平了** | 难度漂移，池子整体变简单（§7.4） | 看有效梯度产出率和 p̂ 分布的众数 |
| 3 | 有效梯度率崩了但 p̂ 分布健康 | **熵坍缩**，不是数据问题（§7.1） | 看策略熵 + 组内答案唯一值个数；改 KL/温度/lr，别去改数据 |
| 4 | 平均长度翻倍但准确率平 | 失控推理或格式化推理（§10.1） | CoT ablation study；truncation 率 |
| 5 | 难度标注和实际训练表现系统性偏差 | **探测与训练的sampling参数不一致**（尤其 `max_tokens`） | 校验 schema 里的 sampling 字段 |
| 6 | 某个题族占据 batch 的大比例 | 去重不足，尤其缺解法骨架去重（§8.2） | 按解法cluster统计 batch 组成 |
| 7 | 换了一版 judge 之后所有难度标注不可比 | verifier 未版本化 | `verifier.version` 进缓存键，换版即重探 |
| 8 | 好题莫名其妙变少 | **污染导致 p̂→1 被当简单题静默丢弃**（§8.3） | 去污前置 + 记录删除原因 |
| 9 | 模型在简单题上退化 | curriculum 升得太快，没有保留低难度锚点 | 难度桶比例里保留 [0.8, 0.95] 的一小部分 |
| 10 | 合成数据加了很多但没提升 | 多样性坍缩（种子太少） | 语义聚类看有效cluster数，而不是看条数 |
| 11 | 每步耗时忽长忽短，GPU 利用率锯齿 | 域同质 batch + 慢 verifier 阻塞（§11.2） | 生成/验证解耦，异步缓冲 |
| 12 | 重跑同一个实验结果对不上 | 缓存键缺字段 / 未记种子（§13.3） | 补齐 lineage |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
