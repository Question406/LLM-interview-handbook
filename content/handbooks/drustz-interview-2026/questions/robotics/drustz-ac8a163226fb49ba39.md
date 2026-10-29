---
id: drustz-ac8a163226fb49ba39
section: robotics
order: 30
level: A
title: 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 1. 数据飞轮全景
quick: 作者文档章节 · 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 1. 数据飞轮全景
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
## 1. 数据飞轮全景

### 1.1 ASCII 图

```text
                ┌────────────────────────────────────────────────────────┐
                │                      FLEET (homes)                     │
                └────────────────────────────────────────────────────────┘
                     │  on-robot triggers:                        ▲
                     │  低置信度 / 用户打断 / teleop 接管 /         │ OTA 部署
                     │  任务失败 / shadow-policy 分歧 /             │ 新 policy +
                     │  异常力矩、碰撞、超时                        │ 新 trigger 配置
                     ▼                                            │
   ┌──────────────────────────┐                    ┌──────────────────────────┐
   │ ② 监控 / TRIGGER          │                    │ ⑥ EVAL                   │
   │ 机端算力先筛，事件式最小化 │                    │ 回归集(每个历史失败一条)  │
   │ 上传，隐私脱敏在边缘完成   │                    │ + replay / world-model   │
   └──────────────────────────┘                    │ + 真机 rollout 抽检       │
                     │                              └──────────────────────────┘
                     ▼                                            ▲
   ┌──────────────────────────┐                    ┌──────────────────────────┐
   │ ③ 采集 COLLECT            │                    │ ⑤ 训练 TRAIN             │
   │ fleet 触发片段 +          │                    │ pre-train: 大而杂        │
   │ teleop 定向 campaign +    │───────────────────▶│ post-train: 小而精       │
   │ 接管/纠偏轨迹 + 人类视频   │   ④ CURATE         │ (+ RL on rollouts)       │
   └──────────────────────────┘   去重/去劣/配比/    └──────────────────────────┘
                                  auto-label/QA/
                                  coverage 管理
        ┌──────────────────────────────────────────────────────────┐
        │ TRIAGE FUNNEL（横切②③）: 事件去重聚类 → severity×frequency │
        │ 排序 → 根因归类(perception/planning/…) → counterfactual    │
        │ replay 判定 → 路由 owning team → 数据修 or 代码修           │
        │ → 该事件永久进入回归 eval 集                                │
        └──────────────────────────────────────────────────────────┘
```



### 1.2 每一步的关键设计点

| 步骤 | 关键决策 | 行业范式 |
|---|---|---|
| ① Deploy | OTA 同时下发 policy 和 trigger 配置；新 policy 可先跑 shadow mode（只推理不执行） | Tesla shadow mode |
| ② 监控/触发 | 机端算力先筛，**只上传有信息量的片段**——带宽 + 隐私双约束下的必然架构；家用场景隐私压力比车更大，on-device 筛选更刚性 | Tesla ~221 个手工 trigger |
| ③ 采集 | 四路来源分层：fleet 触发片段（免费、真分布）、teleop campaign（贵、有动作真值）、接管/纠偏（金标失败数据）、egocentric 人类视频（便宜海量、无动作真值） | Optimus 转 vision-only rig；Figure Go-Big |
| ④ 管护 | 去重去劣、混合配比、coverage 矩阵管理、auto-label 占比持续提升 | Re-Mix、SCIZOR、Tesla auto-label |
| ⑤ 训练 | pre-train 杂数据教恢复，post-train 精数据教流畅；成熟期加自主 rollout RL | PI 教义、π*0.6 RECAP |
| ⑥ Eval | 每个历史失败一条回归测试（失败一次，永远测试）；world-model / replay eval 解决真机throughput瓶颈 | Cruise Road-to-Sim、1X World Model |

**面试时的框架句（英文）**：
> "I think of the data engine as one loop with one north-star metric: cycle time from 'a failure is observed in a home' to 'a fix is deployed and that failure is a permanent regression test.' Every architectural choice — on-device triggers, event-based upload, auto-labeling, world-model eval — exists to shrink that cycle time under privacy and cost constraints."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/04_data_engine.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md)。作者整理资料；许可和第三方来源范围见阅读指南。
