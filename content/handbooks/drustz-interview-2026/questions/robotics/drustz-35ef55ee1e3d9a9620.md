---
id: drustz-35ef55ee1e3d9a9620
section: robotics
order: 33
level: A
title: >-
  04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 4. Curation 与 Active
  Learning
quick: >-
  作者文档章节 · 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 4. Curation 与
  Active Learning
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Robotics · Data、Learning 与 System Design
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md
    type: primary
---
## 4. Curation 与 Active Learning

### 4.1 Curation 流水线（顺序即优先级）

1. **去劣**：剔 no-op/idle 段、失败且无纠偏价值的 episode；SCIZOR 自监督过滤次优片段。
2. **去重**：embedding 聚类去近重复 + SCIZOR 语义去重。
3. **配比（最大杠杆之一）**：Re-Mix 用 DRO 自动学 domain 权重——比 uniform 好 38%、比人工配比好 32%。**"配比即杠杆"** 是可直接说的观点句。
4. **Balancing**：维护任务×环境×物体 coverage 矩阵；每任务保底条数后预算转向多样性；长尾 bucket 设填充目标（Tesla/Cruise 长尾库存管理思路搬到操作任务）。
5. **归因（前沿）**：DataMIL/datamodels 按下游影响选数据——回答"哪 1% 数据最值钱"。

### 4.2 Active Learning：车界三范式直接迁移

| 范式 | 车界原型 | 家用机器人版 |
|---|---|---|
| 不确定性/分歧触发 | Tesla trigger（检测抖动、ensemble 分歧、shadow-policy 与人类行为分歧） | 机端置信度 + shadow policy 与 teleop 操作分歧 → 自动打包上传 |
| 误差挖掘 miner | Cruise CLM：只把"预测 vs 现实显著偏差"送训练集 | policy 预测轨迹 vs 实际执行/纠偏轨迹偏差挖掘 |
| 检索式 query the fleet | Waymo Content Search / VLMine（VLM 挖长尾） | 对 fleet 日志建 embedding 索引，自然语言检索"透明容器抓取失败"类场景 |

**一句英文观点**：
> "Active learning in robotics isn't a research feature, it's the routing layer of the whole engine: it decides which of the fleet's petabytes ever deserve upload, labeling, or a collection campaign."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/04_data_engine.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md)。作者整理资料；许可和第三方来源范围见阅读指南。
