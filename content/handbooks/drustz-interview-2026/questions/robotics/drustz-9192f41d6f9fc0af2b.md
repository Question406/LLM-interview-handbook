---
id: drustz-9192f41d6f9fc0af2b
section: robotics
order: 43
level: A
title: >-
  05 — Debug Playbook：「The bot is not working」排查手册 · 4. 模型变笨 vs 硬件坏了 vs 环境变了 —
  数据区分法
quick: >-
  作者文档章节 · 05 — Debug Playbook：「The bot is not working」排查手册 · 4. 模型变笨 vs 硬件坏了 vs
  环境变了 — 数据区分法
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md
    type: primary
---
## 4. 模型变笨 vs 硬件坏了 vs 环境变了 — 数据区分法

Senior 区分度最高的一节。核心工具：**cohort 切片 + 时序对齐 + 传感器健康基线 + 反事实回放**。

### 4.1 Cohort 切片矩阵

把 success rate（或干预率/任务时长）按这些维度交叉切：

```text
机器人 ID × 模型版本 × 固件版本 × 站点 × 时间段（日内/日间）× 任务类型
```



### 4.2 判别决策表（背下来）

| 证据模式 | 指向 | 下一步验证 |
|---|---|---|
| 只有 1 台掉，同版本同站点其它正常 | **硬件/个体** | 该机传感器健康 vs 自身历史基线；swap test |
| 升到新版本的都掉、未升级的正常，拐点与 rollout 对齐 | **模型/部署回归** | log replay 新旧模型 diff；回滚一台验证 |
| 某站点所有机器（跨版本）同时掉，其它站点正常 | **环境变了** | 调故障片段图像人工看；输入 OOD 分数 vs 训练分布 |
| 渐变下滑、无拐点、单机 | **漂移类**（标定/脏污/磨损/内存泄漏） | 与 uptime/日历时间做相关；"重启就好"→ 泄漏/热/时序 |
| 每天固定时段掉 | 日光/温度/网络高峰/排班 | 按 hour-of-day 切片；与环境时序叠加 |

### 4.3 具体例子（面试现场可以直接讲的 walkthrough）

假设 dashboard 显示 fleet 平均 success rate 一周内从 92% 掉到 84%（数字为示意）：

1. **按模型版本切**：v2.3 机器 91%，v2.4 机器 79% → 强烈指向新模型。但慢着——
2. **按站点切**：发现掉分的 v2.4 机器几乎都在 Site B，Site A 的 v2.4 机器只微降 → 混淆了！v2.4 恰好先发给了 Site B。
3. **反事实回放（最干净的一刀）**：把 Site B 失败时段的录制输入喂给旧模型 v2.3 离线跑——
   - 旧模型也失败 → 是**环境/输入**问题（去看图像：也许 Site B 换了地面/灯光）；
   - 旧模型能成功 → 是**模型回归**（v2.4 在 Site B 这类分布上退步了）。
4. **交叉证据**：Site B 的输入 embedding OOD 分数从上周三开始抬升，且抬升**先于** success rate 下降 → 环境指纹坐实。

英文版核心句（背）：

> "The cleanest cut is **counterfactual replay**: feed the failing period's recorded inputs to the old model offline. If the old model also fails, it's the environment or the inputs; if the old model succeeds, it's a model regression. And the cleanest prevention is a **control group**: canary rollouts make the 'environment vs model' debate disappear, because you always have a same-time, same-place comparison cohort."

### 4.4 让区分变容易的三个前置投资（主动提，展示系统思维）

1. **Per-device 健康基线**：每台机维护图像亮度/清晰度、IMU bias、编码器噪声、电机电流-速度曲线、推理延迟 p99 的历史基线，偏离 N σ 报警 → "硬件坏了"在 success rate 掉之前就被抓到。
2. **输入分布监控**：对 policy 输入做 embedding，监控 OOD score / 与训练分布距离 → "环境变了"的早期指纹。
3. **变更事件流**：OTA、配置、flag、地图更新全部进同一条 event timeline，任何指标图都能一键叠加变更竖线 → changepoint 与部署事件重合是最强信号。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/05_debug_playbook.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md)。作者整理资料；许可和第三方来源范围见阅读指南。
