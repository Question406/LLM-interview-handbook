---
id: drustz-784ccd54bc8fd6963f
section: mlsd
order: 174
level: A
title: 19 · Case：设计 agent 能力 benchmark · 12. 现有 benchmark 的设计取舍：我从每个借一条
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 12. 现有 benchmark 的设计取舍：我从每个借一条
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
## 12. 现有 benchmark 的设计取舍：我从每个借一条

主表（分数、失败模式、引用姿势）见 [agentic2 · 04_benchmarks](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/agentic2/04_benchmarks.md)，这里只讲**自建时借什么设计决策**。

| Benchmark | 关键设计选择 | 换来了 | 牺牲了 | 我借这一条 |
|---|---|---|---|---|
| **SWE-bench Verified** | 用真实 issue + 仓库已有单元测试当 verifier；人工从 2294 筛到 500 | 零标注成本的客观 verifier | 只验测试不验代码质量；仓库全在预训练集里 | **fail-to-pass + pass-to-pass 的双向结构**——既验修复也验不回归。这是"过程约束"最廉价的一种形态 |
| **SWE-bench Pro** | copyleft 公共集 + held-out 商业集 | 法律层面的防污染 | grader 仍有 ~1/3 试次误判 | **private held-out 集**这个结构本身 |
| **τ-bench** | LLM 模拟用户 + DB 终态比对 +  $\mathrm{pass}^k$  | 可自动化的多轮评测；暴露方差 | simulator 是噪声源且可被诱导 |  $\mathrm{pass}^k$  的报法 + 终态比对；但我会给 simulator 固定剧本和 seed（§5.4） |
| ** $τ^{2}$ -bench** | dual-control：用户侧也持有工具，agent 要指导人操作 | 测协作而非代管 | 更难复现 | "**agent 指导人执行**"这一整类任务——真实客服/IT 支持里这类占比很高 |
| **WebArena** | 自托管冻结站点 | 完全可复现、零真实副作用 | 与现代 web 脱节；evaluator 有假阴性；被 URL 捷径 exploit 过 | 自托管这个决定；但要**为已知捷径写显式的过程断言**（检测到直构 URL 即判 violation） |
| **OSWorld** | 每任务定制 execution-based 评分脚本 | 精确 | 脚本自己会坏（原版 ~10% 任务坏的） | **verifier 要有自己的测试**（§5.5）——这是我最看重的一条教训 |
| **Terminal-Bench 2.0** | harness 公开 + 轨迹公开可查 | 可审计 | 任务分布偏 infra 不偏产品代码 | 把 harness 当自变量做 ablation；**全量轨迹存档**（没有轨迹就没法做失败分类） |
| **GAIA** | exact match 短答案 | 判分零成本 | 限死题型；已饱和 | 短答案层作为**便宜的 smoke 层**，不作主集 |
| **AgentDojo** | utility + ASR 双指标 | 防"砍功能换安全"的假防御 | 静态攻击集过时快 | 双指标同 dashboard + 预留 **adaptive 红队接口**（静态注入集只是回归测试） |

> **高分句**：我引用这些 benchmark 不是为了借分数，是为了借失败模式。它们的修订史就是一部"eval 怎么坏掉"的教科书，而我造的第一版可以直接跳过它们踩过的三个坑：坏题、坏 verifier、被环境泄漏。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
