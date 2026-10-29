---
id: drustz-94cf9e3aa48c1dfc1e
section: mlsd
order: 96
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 12. 常见失败模式：这套系统最容易在哪坏掉 ⭐⭐⭐
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 12. 常见失败模式：这套系统最容易在哪坏掉 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md
    type: primary
---
## 12. 常见失败模式：这套系统最容易在哪坏掉 ⭐⭐⭐

| # | 失败模式 | 具体长什么样 | 早期信号 / 对策 |
|---|---|---|---|
| 1 | **judge 静默升级** | 昨天 62%、今天 65%，模型没动 | 100 条 gold anchor 夹带；anchor 漂移 >3pp 作废本次结果 |
| 2 | **judge 与被测模型同族** | 自家新模型莫名其妙全面领先 | 换一个不同家族 judge 复跑；差异大就以跨家族结果为准 |
| 3 | **prompt 模板微改导致分数跳变** | "Assistant A/B" 改成 "Response 1/2"，胜率动 3–5 点 | 模板 hash 进结果记录；模板变更走和模型变更一样的评审 |
| 4 | **冻结集被训练吃掉** | 回归集分数一路走高，线上无感 | 回归集 hash 进数据管道 blocklist；private holdout 与之对照 |
| 5 | **平均分掩盖切片退化** | 总分 +1.2pp，某语言 -6pp | 强制 min-slice 报告；guardrail 切片非劣性检验 |
| 6 | **benchmark 自身标签错误** | 刷到 95% 但 6.5% 的题本身是错的 | 高分区间要人工抽检错题；接近天花板时换更难的集 |
| 7 | **标注员用 LLM 代劳** | 人评与 judge 一致率异常高（>90%）、标注速度异常快 | 埋 attention check；看标注时长分布；保留少量必须写理由的题 |
| 8 | **不确定性sampling污染总体估计** | 报出来的质量比线上体感低很多 | 两个池子严格分开（§10.1） |
| 9 | **只测单轮** | 单轮分很好，用户抱怨"聊几轮就忘了要求" | 加多轮切片；至少一组人工多轮 |
| 10 | **judge 同时是 reward** | RL 分数飙升，人工评测不动甚至下降 | reward judge 与 eval judge 必须是不同模型/不同 prompt；eval judge 冻结 |
| 11 | **"指标没定义过"的失败模式** | 格式化推理、失控推理、reward hacking——所有指标都正常 | **固定安排读原始 trace**，并给它拦截权（§9.2） |
| 12 | **评测太慢被绕过** | 团队开始"这次小改动就不跑 gate 了" | 分档：秒级 smoke / 小时级完整 / 天级人工；抢占可恢复（§10.5） |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
