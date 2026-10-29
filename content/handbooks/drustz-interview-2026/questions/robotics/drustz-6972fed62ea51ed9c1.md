---
id: drustz-6972fed62ea51ed9c1
section: robotics
order: 50
level: A
title: >-
  06 — System Design Playbooks：四道 Robotics ML 高频题 · Playbook A — 家用机器人 Fleet（1
  万台）数据采集 + Telemetry Pipeline
quick: >-
  作者文档章节 · 06 — System Design Playbooks：四道 Robotics ML 高频题 · Playbook A — 家用机器人
  Fleet（1 万台）数据采集 + Telemetry Pipeline
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/06_system_design_playbooks.md
    type: primary
---
## Playbook A — 家用机器人 Fleet（1 万台）数据采集 + Telemetry Pipeline

### 可能的题干

> "Design the data collection and telemetry pipeline for a fleet of 10,000 home robots. We want to use fleet data to improve our policies, while also monitoring fleet health. Assume each robot has multiple cameras and runs a learned policy on-device."

### Clarifying questions（开场 5 分钟）

- "What's the priority: training data (episode-level, with action labels) or ops telemetry (metric-level)? They have very different SLAs — training data can be hours late, safety alerts need minutes."
- "What's the privacy model? These robots see faces, kids, screens inside homes. What did users opt into? Does GDPR/CCPA apply?"
- "What uplink can I assume? Home broadband upload is 10–30 Mbps and we can't hog the user's bandwidth — so realistically overnight/idle uploads only."
- "How much edge compute is left over after running the policy — can I run scoring/filtering models on-device?"
- "How many active hours per robot per day? I'll assume 2–4."

### 数量级估算（现场算给面试官看）

| 项 | 估算 | 推出的设计决策 |
|---|---|---|
| 单台原始视频 | 5 cam × 1080p30 H.265 ≈ 5 Mbps/路 → 25 Mbps ≈ 3 MB/s ≈ 11 GB/h；4h 活跃 → **~45 GB/天/台** | 不可能全传 |
| 本体感知 | ~30 关节 × (pos+vel+torque) × 500 Hz × 4B ≈ 200–500 KB/s → 压缩后 <2 GB/天 | 价值密度极高、体积可忽略 → **全量保留** |
| Fleet 全量 | 10k × 45 GB ≈ **450 TB/天** | 本题 hook："neither feasible nor necessary" |
| 触发式采集后 | 上传 2–5% 时间片 → 1–2 GB/天/台 → **10–20 TB/天 fleet → ~5 PB/年** | 热存 30 天 + 冷归档分层 |
| 标注throughput | 1 万条 30s clip/天，人工 60–100 条/人/时 → 15–25 人 | 或 auto-label + 人工抽检 10% |

面试时的说法：**"450 terabytes a day is neither feasible nor necessary. The interesting design question is not how to move the data — it's deciding on-device what NOT to upload."**

### 高层架构

```text
[机器人] 环形缓冲区 (本地 NVMe 滚动 2-4h 全量录制)
   ├─ 触发引擎 (规则 + 模型, 可 OTA 更新) ──→ 事件切片 [-30s, +30s]
   ├─ on-device 预处理: 人脸/屏幕模糊, PII 过滤, H.265 压缩, novelty 打分
   ├─ telemetry agent: 指标 (1Hz 聚合) + 日志 → MQTT/gRPC 实时上报
   └─ 上传器: 夜间 Wi-Fi, 断点续传, 优先级队列 (安全事件 > 干预 > 常规)
[云端] API Gateway → Kafka →
   ├─ 实时流: 安全告警, fleet 健康 dashboard (时序库)
   └─ 批流: S3 + episode 元数据 (Postgres/数据湖)
        → embedding 索引 (视频帧 + 语言描述 → 向量库)
        → 去重/质量过滤 → 标注队列 (优先级) → dataset manifest
```



云端部分你全都熟（Kafka → S3 → manifest，跟 RL data pipeline 一个骨架），一句带过。**边缘侧才是这题的分数所在。**

**触发事件清单（要能一口气列出七类）**：
1. **人工干预/接管**——teleop correction 即带标签训练样本，最高价值数据（1X 的 teleop 数据飞轮模式）；
2. **任务失败**（重试、超时、放弃）；
3. **policy 不确定性高**（action 分布熵、ensemble 分歧、VLM confidence 低）；
4. **安全事件**（碰撞、力矩超限、急停、人闯入工作区）；
5. **新颖度**（场景 embedding 与已采集分布距离大）；
6. **云端下发 campaign**（Tesla shadow mode / AWS IoT FleetWise 模式："采集所有『开冰箱门失败』的片段"——条件下发全 fleet，边缘匹配后上传）；
7. **随机uniform sampling**（小比例，对冲触发器自身的分布偏差）。

### 深挖组件 1：触发引擎 + 环形缓冲区

- **为什么必须环形缓冲**：失败发生时你需要失败*之前*的上下文。本地滚动保留 2–4h 全量，触发时切 [-30s, +30s] 窗口标记保留。
- **触发器可 OTA**：云端发现某类失败率升高 → 下发新 trigger 规则，不用等固件发版。
- **trigger 风暴防护**：监控每类 trigger 的 fire rate，每类每天限额——否则一个写坏的 trigger 会打爆上传队列和标注队列。
- 类比帮记忆：这就是 robotics 版的 "log sampling with head-based + tail-based rules"，但sampling决策必须在边缘做，因为回传本身就是成本大头。

### 深挖组件 2：场景索引与检索

数据工程师要能查 **"all clips where the robot dropped a glass in a kitchen"**。方案三件套：
- 结构化元数据（任务 ID、房间类型、结果、干预标志）→ SQL 过滤；
- V-L embedding（CLIP/VLM 编码关键帧入向量库）→ 语义搜索；
- VLM 自动生成的文字描述 → 全文检索 + 后续 auto-label 的种子。

检索 = 结构化过滤 ∩ 语义搜索。这一层直接决定数据飞轮的转速——"we collected it but can't find it" 等于没采。

### Privacy 设计要点（家庭场景，必讲）

- 模糊/PII 过滤**必须在设备端上传前**完成，云端只见处理后数据；
- 分级 opt-in：仅 telemetry / 匿名化片段 / 完整视频；
- 卧室/卫生间地理围栏禁采；
- 用户可查看/删除自家数据，且 deletion 要能沿 **episode → dataset → model 的 lineage** 穿透到训练集（联动 B 题的 manifest 设计）；
- 加分项：主动提 1X NEO 当前的隐私争议（数据跨境、blanket consent、儿童数据无特别保护），说明你跟得上行业。

### 核心 Tradeoff

**数据覆盖度 vs 带宽/隐私成本**。触发式采集省 95%+ 带宽，但 **your triggers define your data distribution**——你只看得到你已知道要找的失败（selection bias）。缓解：小比例均匀random sampling + campaign 机制 + 用便宜的全量 telemetry 指标发现盲区再定向采集。第二重：隐私模糊损失了人机交互研究需要的信息 → 按数据用途分级处理，不一刀切。

> **设计哲学**："On a bandwidth-starved fleet, the upload policy IS the data strategy — every trigger you write is a bet on what your model needs to learn next."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/06_system_design_playbooks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/06_system_design_playbooks.md)。作者整理资料；许可和第三方来源范围见阅读指南。
