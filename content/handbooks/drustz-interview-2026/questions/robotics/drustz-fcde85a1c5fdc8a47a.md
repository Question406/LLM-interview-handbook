---
id: drustz-fcde85a1c5fdc8a47a
section: robotics
order: 29
level: A
title: 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · TL;DR — 只有 20 分钟就看这段
quick: >-
  作者文档章节 · 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · TL;DR — 只有 20
  分钟就看这段
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
## TL;DR — 只有 20 分钟就看这段

1. **一句话世界观**：家用机器人 fleet = AV fleet 的近亲。用户打断 / teleop 接管 / 任务失败 ≈ disengagement；整个数据引擎就是把每次失败变成训练数据 + 永久回归测试的闭环。
2. **飞轮七步**：deploy → 机端 trigger 监控 → 事件式采集上传 → curation（去重/配比/过滤）→ 训练 → eval（回归集 + world-model/replay）→ 再 deploy。北极星是**飞轮周期**（failure 被观测到修复上线的天数）。
3. **Tesla 贡献的词**：shadow mode、trigger campaign（~221 个手工触发器）、机端先筛不回传原始流、离线 auto-label（4D 重建 + 后见之明）、每个 bug 变 eval clip（"Operation Vacation"）。
4. **Cruise 贡献的词**：CLM（自监督标签"等几秒就出现"+ active learning miner 只收显著偏差场景）、event triage funnel（去重聚类 → severity×frequency 排序 → 根因归类 → counterfactual replay 判定 necessary vs unnecessary takeover）、Road-to-Sim（每个路测事件永久变回归场景）。
5. **1X 贡献的词**：产品先于自主性（NEO teleop 进家，$20k/$499月）、operator = trainer（"farm-to-table" 数据）、Redwood 板载推理（隐私+延迟）、world model 解 eval throughput瓶颈、"social contract" 明码隐私换数据。
6. **PI 贡献的教义**：pre-train 大而杂（次优数据教恢复），post-train 小而精（教流畅）；π0.5：泛化随**环境数**呈幂律，~100 环境近上限，web 数据救 OOD 物体；π*0.6/RECAP：demos → 专家纠偏（接管即数据）→ 自主 rollout RL，采集成本结构从纯 teleop 转向机器人自产经验。
7. **Scaling law 结论（预算怎么花）**：泛化随环境数/物体数幂律增长，单环境 demo 数过阈值边际趋零 → **钱买多样性，不买同环境条数**。
8. **Teleop 生产线数字**：leader-follower 20–40 demos/h，VR 10–20；全摊 &#36;28–60/操作员小时，成品数据 ~&#36;118–136/h（2025-26 第三方市场口径，未证实——口头说 "on the order of &#36;100+ an hour"），每条成功 demo &#36;1–10；三层 QA（自动打分 → gold-set calibration → 人工终审）。
9. **Failure-driven 三板斧**：接管即金标数据（DAgger 谱系）；失败 taxonomy → 定向采集 campaign；miner 挖相似场景 + 每个失败固化为回归 eval。
10. **隐私必背案例**：iRobot 如厕照经 Scale AI 外包标注员外泄——**威胁模型必须覆盖整条数据供应链，不只是设备端**；正面模板是 1X（逐次同意、no-go zones、边缘脱敏、自有操作员）。
11. **指标四件套**：采集产能（demos/h/operator、&#36;/demo、QA 良率）、coverage（任务×环境×物体矩阵、独立环境数）、飞轮速度（cycle time、eval throughput）、边际贡献（每 +N 小时的成功率增益；部署侧 intervention rate = 家用版 miles per disengagement）。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/04_data_engine.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md)。作者整理资料；许可和第三方来源范围见阅读指南。
