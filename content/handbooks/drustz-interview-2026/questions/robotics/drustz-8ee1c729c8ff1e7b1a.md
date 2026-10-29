---
id: drustz-8ee1c729c8ff1e7b1a
section: robotics
order: 52
level: A
title: >-
  06 — System Design Playbooks：四道 Robotics ML 高频题 · Playbook C — Policy
  Evaluation 系统（sim + real + human 金字塔 & 统计功效）
quick: >-
  作者文档章节 · 06 — System Design Playbooks：四道 Robotics ML 高频题 · Playbook C — Policy
  Evaluation 系统（sim + real + human 金字塔 & 统计功效）
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
## Playbook C — Policy Evaluation 系统（sim + real + human 金字塔 & 统计功效）

这是四题里最"考数字"的一道，也最容易和你练过的 LLM eval pipeline 混淆——**区别只有一个但足够颠覆设计：real eval 太贵，贵到统计功效成为一等公民约束**。LLM eval 里你从不担心跑不够样本；这里每个 trial 是 2–5 分钟的物理动作加人工 reset。

### 可能的题干

> "Design an evaluation system that decides whether a new policy checkpoint is safe and better enough to ship to the fleet. You have simulators, a handful of real robots for eval, and human reviewers. How do you make this decision rigorous?"

### Clarifying questions

- "Are we evaluating a single-task policy or a generalist VLA? A generalist needs per-task × per-scene stratification — aggregate metrics hide single-task regressions."
- "How well does sim correlate with real today? Has anyone calibrated sim scores vs. real scores?"
- "How many dedicated eval robots and standardized scene cells do I have? Is reset manual or automated? Real-robot throughput is the bottleneck of the whole system."
- "Is the gate 'significantly better' or 'not significantly worse' — superiority vs. non-inferiority? That changes the statistical test."
- "Is safety evaluated separately? I'd argue the safety suite should be a 100% pass hard gate, outside the statistics."

### 数量级估算 — 统计功效（本题核心考点，背下来）

两比例 z 检验，α=0.05 双侧、power=0.8，检测差异所需**每组** trial 数：

| 基线 → 目标 | 每组 n |
|---|---|
| 50% → 55% | **~1,565** |
| 80% → 85% | **~905** |
| 90% → 95% | **~434** |
| 50% → 60% | ~387 |
| 80% → 90% | ~199 |

配套 CI 直觉（90% 成功率附近）：

| trials | 95% CI 宽度 |
|---|---|
| 50 | ±8pp |
| 70 | ±7pp |
| 200 | ±4pp |
| ~1,000 | ±2pp |

（NVIDIA 评估博客的例子：70 rollouts → 15.4pp 宽 CI；1030 rollouts → ±2pp。TRI 明确指出多数学术 benchmark 的 10–50 rollouts 根本不足以支撑"我的 policy 更好"——他们的例子：50 次里 25 成功 vs 29 成功，50% vs 58%，检验不显著。）

真机throughput算术：一个 eval cell 每 trial 2–5 分钟 + reset → **100–200 trials/机/天** → 检测 80%→85% 需要 ~1,810 total trials ≈ **10 台 eval 机器人跑一整天**。当场推出结论：

**"So a 5-point improvement is physically undetectable on real robots as the primary instrument. The design consequence: sim carries the statistical power, real robots carry calibration and catastrophic-regression checks."**

### 高层架构：评估金字塔（下宽上窄，成本↑保真度↑）

```text
L4  fleet 金丝雀/A/B (周级) ── 最终真值, 主指标=干预率 (联动 B 题)
L3  human review (持续) ──── 抽样视频评审, 抓"成功但行为怪异"
L2  真机 eval farm (天级) ── 数百–千 trials, 标准化 cell, 校准 sim + 验收 top candidate
L1  大规模 sim (小时级) ──── 数万 episodes, 域随机化 + 失败场景回放库
L0  离线指标 (分钟级) ────── action MSE/NLL, 只做 sanity check
```



- **L0**：与真实成功率相关性弱，只用于训练监控——等价于你熟的 "loss ≠ eval"，一句带过。
- **L1 sim**：绝对分不可信，但**相对排序 + 回归检测**在calibration后可信。sim 是唯一能满足统计功效的层。
- **L3 human**：rubric 化打分抓成功率盲区（粗暴、低效、吓人的动作）；可 VLM-as-judge 预筛再人审——这半套你也熟。
- **L4**：联动 B 题金丝雀。

**降 trial 需求三板斧（深挖弹药）**：
1. **配对设计**：两个 policy 在相同初始条件/场景种子下各跑一次，McNemar/paired test消除场景难度方差——sim 天然可控种子，真机用摆位模板；
2. **Sequential testing**：TRI+Princeton 的 **STEP** 框架（RSS 2025）边跑边检验、差距大提前停，配 Barnard exact test（小样本二项比较推荐）；后续工作声称再省 ~32% trials；
3. **分层 + 校正**：按任务分层报告，多任务比较用 Bonferroni/FDR，防"20 个任务总有一个假阳性回归"。

### 深挖组件 1：regression gate 的统计设计

- gate 设为 **non-inferiority test**：H0 = 新模型比旧模型差超过 margin δ（如 3pp），要求以 95% 置信拒绝。
- 分层落地：sim 上做严格 non-inferiority（n 够大）；真机只做"无灾难性回归"粗检（如 200 trials 检测 ≥10pp 掉落）+ 安全套件 100% 硬门（不进统计）。
- **calibration回路**：定期用同批模型的 sim 分 vs 真机分拟合相关性，监控 sim gate 的预测有效性本身——sim 漂移了 gate 就静默失效，这是本系统最阴险的失败模式。

### 深挖组件 2：eval 场景库的策展

gate 质量 = 场景覆盖质量。闭环："fleet 失败数据自动挖掘 hard case → real2sim 重建为 sim 场景 → 进入回归套件"→ **线上失败永不复发**（联动 A 题的失败触发采集）。场景库要版本化：eval 套件本身变了，历史分数不可比 → 套件升级时新旧模型都重跑基线。

### 核心 Tradeoff

**统计严谨 vs 迭代速度/成本**。完全严谨的真机评估物理上不可达。答案不是放弃严谨，而是**把功效花在对的层级**：sim 承担大样本统计，真机承担calibration和 spot-check，金丝雀承担最终判决；配对 + sequential 榨取每 trial 的信息量。第二重：单一聚合成功率 vs 分层指标——聚合掩盖回归，分层遭遇多重比较 → 明确主指标 + 护栏指标层级。

> **设计哲学**："When trials cost minutes of physical motion, statistical power is an architectural constraint — spend it where trials are cheap, and spend real robots only on calibrating that proxy."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/06_system_design_playbooks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/06_system_design_playbooks.md)。作者整理资料；许可和第三方来源范围见阅读指南。
