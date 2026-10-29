---
id: drustz-33ac5fa638e403fe0b
section: robotics
order: 51
level: A
title: >-
  06 — System Design Playbooks：四道 Robotics ML 高频题 · Playbook B — Robot Policy
  Post-Training Pipeline（数据 → 训练 → 部署 → 回滚）
quick: >-
  作者文档章节 · 06 — System Design Playbooks：四道 Robotics ML 高频题 · Playbook B — Robot
  Policy Post-Training Pipeline（数据 → 训练 → 部署 → 回滚）
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
## Playbook B — Robot Policy Post-Training Pipeline（数据 → 训练 → 部署 → 回滚）

### 可能的题干

> "Design the end-to-end pipeline that takes fleet data, post-trains our robot policy, and safely ships the new policy back to 10,000 robots in homes — including how you'd catch a bad release and roll it back."

### Clarifying questions

- "What's the model? A 2–7B VLA running on-device, or cloud brain + distilled edge model? This decides OTA size and training cost."
- "Target release cadence — weekly or monthly? That decides how much eval must be automated."
- "Full fine-tune, LoRA, or action-head only? Delta size: tens of MB vs. several GB."
- "What's the cost of a bad release — a dropped cup or a hurt person? That sets gate strictness and canary size."
- "Any product/ethics constraint on A/B — is it OK for a paying household to get the worse policy?"

### 数量级估算

| 项 | 估算 |
|---|---|
| 数据增量 | fleet ~1 万条有效 episode/天（30s–2min）→ **~5,000 小时/月**演示+纠正数据（π0/GR00T 级 VLA 预训练在 ~1 万小时量级，post-train 每轮全量+增量） |
| 训练算力 | 3B VLA 在 ~10k 小时数据上微调：8–64 张 H100，1–7 天/轮，**数千到数万 GPU-hours，&#36;10k–100k/run** |
| OTA | 3B fp8 ≈ 3 GB 完整镜像；LoRA/delta 几十–几百 MB；10k 台分波次 CDN 下发 |

### 高层架构

```text
episode 存储 (immutable, 带 schema 版本)
 → 数据处理 DAG: 过滤/去重/auto-label/质量分
 → Dataset Manifest (内容寻址快照: episode ID 列表 + 处理代码 hash)
 → 训练 (config + manifest + commit 全入 registry, 可复现)
 → Model Registry: candidate→staging→canary→production→deprecated
 → Eval Gate (三级, 见 Playbook C): sim 套件 → 真机 eval cell → 安全场景 100% 硬门
 → 发布: 签名 → 量化/编译 (TensorRT) → 差分包 → OTA 服务
 → 金丝雀: 1% (内部 dogfood/员工家庭) → 5% → 25% → 100%
     每级最短观察期 + 自动晋级条件
 → 线上监控: 干预率, 分任务成功率, 安全事件率, 延迟/内存 → 异常自动 halt rollout
 → 回滚: 设备端 A/B 双分区 (Android seamless update 模式), 切分区重启, 分钟级
```



前半段（immutable episode + manifest + registry + 可复现训练）你在 LLM pipeline 里全练过，面试时一句 **"the data/training half is standard ML infra — immutable episodes, content-addressed manifests, full lineage in the registry"** 带过，把时间留给部署侧的 robotics delta。

### 深挖组件 1：数据版本化与 lineage（快讲，重点讲 robotics 用途）

数据集 = "manifest = episode ID 列表 + 处理代码版本"的虚拟快照，不复制数据。任何生产模型必须能回答：用了哪些数据、哪个 commit、哪组超参。robotics 特有的两个用途：
- **用户删数请求**沿 lineage 穿透（A 题 privacy 的下游义务）；
- **blast radius 分析**：某批坏标注/坏 teleop 数据污染了哪些模型 → 直接定位需要重训或回滚的版本。

### 深挖组件 2：金丝雀 + A/B 的机器人特殊性（本题分数所在）

与 web A/B 的四个不同，逐条讲：

| Web A/B | Robot fleet | 应对 |
|---|---|---|
| 按 request 分桶 | 按 **household** 分桶（同一家庭内切换 policy 会污染用户行为和环境状态） | randomization unit = household |
| 样本近乎无限 | 1% 金丝雀 = 100 台 × 每天几十个任务，检测 5pp 差异要累积数天（联动 C 题功效表） | 拉长观察期 + 换更灵敏指标 |
| 只能线上比 | 可用 **shadow mode**：新 policy 在设备上并行推理但不执行，比较其 action 与现行 policy/人工纠正的分歧（Tesla 验证 FSD 的核心手段） | 小样本下提前发现行为漂移 |
| 主指标 = 转化率 | 主指标 = **干预率**（比成功率更灵敏、更快累积；成功率作护栏） | 干预率异常 → 自动 halt |

可引用：AgiBot 2026 的 Learning-while-Deploying（fleet RL 的"部署↔共享经验↔改进↔再部署"闭环）是这套东西的学术版参照。

### 核心 Tradeoff

**发布速度 vs 安全置信度**。每级 gate 加严都拖慢迭代（真机 eval 全套数天），但家用场景一次伤害事件可能毁掉产品线。标准答案是**分层**：
- 安全性由本地、不可 OTA 的 safety layer 兜底（碰撞/力/速度限幅独立于 policy 版本、不信任 policy 输出）→ **买来了 policy 层快速迭代的权利**；
- 能力回归靠 sim 大规模 gate + 真机抽查 + 金丝雀慢速放量。

第二重：全模型 OTA（干净、可完整验证）vs LoRA/delta 热更（快、省带宽，但版本组合爆炸）。立场：**设备上只存在完整签名镜像 + A/B 双分区**，宁可多花 CDN 带宽也不要组合爆炸的调试地狱。

> **设计哲学**："A non-OTA safety layer is what buys you the right to ship policies fast — decouple what must never break from what must iterate weekly."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/06_system_design_playbooks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/06_system_design_playbooks.md)。作者整理资料；许可和第三方来源范围见阅读指南。
