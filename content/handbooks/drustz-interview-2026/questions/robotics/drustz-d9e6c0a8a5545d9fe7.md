---
id: drustz-d9e6c0a8a5545d9fe7
section: robotics
order: 7
level: A
title: 01 — The Bot Company 公司情报（Company Brief） · 4. 技术路线信号
quick: 作者文档章节 · 01 — The Bot Company 公司情报（Company Brief） · 4. 技术路线信号
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/01_company_brief.md
    type: primary
---
## 4. 技术路线信号

### 4a. 有证据的（可以在面试中直接引用）

| 信号 | 证据 |
|---|---|
| 端到端学习，抛弃经典 CV/3D 重建/运动规划栈 | Cheeky Pint："You don't need a robot that's repeatable, you need a robot that's adaptable, powered by neural networks" |
| **拒绝入户 teleoperation**（隐私 + 不可扩展）；end-to-end nets on near-raw sensor/motor signals | No Priors/Sacra 口径 |
| **Fleet learning + OTA**：in-home 部署数据回灌整个车队 | 访谈口径；Cruise/Tesla 思路移植 |
| LLM 做高层自然语言指令理解与行为指挥 | Cheeky Pint；The Rundown |
| **三层栈**：统一多模态基座（text/image/video/**kinematics**，含 pretraining/post-training/RL）+ 视频生成世界模型（neural simulator，multi-billion param）+ sim-to-real 全身控制（IsaacLab/MuJoCo、domain randomization） | ✅ 三份 ML JD 原文 |
| 数据基建目标：PB 级、数千机器，"from acquisition to improving autonomous capabilities" | ✅ Data Infra JD 原文 |
| Edge inference 优化是一等公民 | ✅ Multimodal FM JD："optimize performance for edge inference" |
| 非人形：轮式/履带底盘 + 机械臂；~6 英尺原型 | Reuters sources + Airbnb 目击；3D Vision JD 提 "wheel odometry" |
| 传感器栈含相机、IMU、轮式里程计、LiDAR；SLAM、NeRF/Gaussian Splatting 在招 | ✅ 3D Vision JD |
| 自研执行器 + 力控：FOC/PMSM/BLDC，固件与 ML 协作做 "force-sensitive, compliant control" | ✅ Firmware JD |
| 先做低风险「一千件小事」（容错 90–99%），回避洗碗/洗衣 | Cheeky Pint/Sacra |
| <100 人、95% 工程师、全员 IC、全员 onsite、离机器人 10 英尺内 | 访谈 + JD 模板 |

### 4b. 推测的（面试中要么不说，要么明确说是自己的推断）

| 推测 | 依据与置信度 |
|---|---|
| 上市前存在大规模线下人工数据采集（演示/操作 operator 队伍） | ⚠️ 中高置信：Airbnb 30+ 人轮班 + "hundreds" 合同工 + 「不做入户 teleop」只约束了用户家场景。具体是遥操作演示还是现场标注**未公开** |
| "MLO" 岗 = 内部未公开岗，职责 ≈ Multimodal FM 的 post-training 部分 + data engine | ⚠️ 推测：公开 JD 无此名；泛 ML 旧 JD 原文不可考 |
| 硬件规格：4-DOF 臂、<1kg 载荷、10L 收纳箱、可换末端执行器、sub-&#36;10K、Matter/HomeKit 集成 | ⚠️ 低置信：仅 Sacra 重构，无一手来源，**当作没有** |
| 正在为量产做准备 | ⚠️ 中置信：Mechanical JD（注塑/压铸/MIM、volume manufacturing）+ 曾招 Head of Supply Chain |
| 有消费级 App | ⚠️ 中置信：2025-11 曾招 iOS/Full-Stack |
| 专利以壳公司名义申请或未过 18 个月公开期 | ⚠️ 纯推测：assignee 检索 0 条 |

**竞品格局**（✅ Sacra/The Rundown 汇总）：1X NEO（&#36;20K 或 &#36;499/月，2026 底交付）、Figure、Tesla Optimus、Sunday Robotics（&#36;200M B 轮，Skill Capture Gloves 收了 1000 万条人类轨迹，2026 底 beta）、中国厂商（Galbot &#36;350M、Unitree &#36;13.5K 人形；电机/执行器成本优势 2–3 倍）。差异化记忆点：Botco 赌「非人形 + 专用形态 + 低风险任务捆绑」，vs 人形阵营赌通用形态。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/01_company_brief.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/01_company_brief.md)。作者整理资料；许可和第三方来源范围见阅读指南。
