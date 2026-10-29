---
id: drustz-cf5fb9d2d385b97563
section: mlsd
order: 171
level: A
title: 19 · Case：设计 agent 能力 benchmark · 9. 版本漂移：benchmark 是会腐烂的软件产物
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 9. 版本漂移：benchmark 是会腐烂的软件产物
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md
    type: primary
---
## 9. 版本漂移：benchmark 是会腐烂的软件产物

| 漂移源 | 表现 | 缓解 |
|---|---|---|
| 依赖升级 | 装不上了；测试因为库行为变化而挂 | 镜像 digest + 完全离线 + 定期 re-baseline（用同一个旧 checkpoint 重跑，分数应当不变） |
| 外部服务 | API 改 schema、限流、下线 | 全部录制回放；真实调用只保留在小的保真度calibration集 |
| 站点 / UI 变化 | 选择器失效 | 自托管冻结（WebArena 路线），代价是与现代 web 脱节 |
| 模型接口 | 新模型不支持旧的 function-calling 格式；推理模型多出 thinking 字段 | harness 层抽象；接新模型先跑 sanity 层 |
| **时间语义** | "查最近 7 天的订单"随日历静默改变答案 | 冻结时钟 + 相对时间表述（§5.2） |
| 分数饱和 | 都 95% 了，没有区分度 | 滚动换题、frontier 层扩容 |

两条必须落地的机制：

- **`infra_failure` 必须单独计**，不能算成 agent failure。容器 OOM、429 限流、超时——如果混在一起，你会得出"模型在长任务上更差"的错误结论，而真相是长任务更容易撞超时。报告里要有一行"本次运行 N 题因 infra 原因排除"。
- **re-baseline 制度**：每次改 harness / 升依赖，用一个冻结的旧 checkpoint 重跑全集。分数变化超过噪声带宽就说明这次改动本身移动了标尺，所有历史数字要标注版本。

> **高分句**：这些公开 benchmark 的修订史——SWE-bench→Verified、OSWorld→Verified、 $τ^{2}$ →Verified——本身就是最好的设计文档。每一次修订都在补一个我现在可以提前避开的洞：坏题、坏 verifier、policy 不自洽。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
