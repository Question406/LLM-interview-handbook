---
id: drustz-4befc093c2f828d478
section: mlsd
order: 138
level: A
title: 17 · Case：设计合成数据生成系统 · 12. 常见失败模式（这个系统最容易在哪坏掉）
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 12. 常见失败模式（这个系统最容易在哪坏掉）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 12. 常见失败模式（这个系统最容易在哪坏掉）

| # | 失败模式 | 症状 | 根因 | 防御 |
|---|---|---|---|---|
| 1 | **在天花板上评测** | 所有方法都 0.98+，看不出差异 | 合成的评测数据太简单，或标签泄漏进了输入 | 造数据时**刻意设计区分度**（下面详述） |
| 2 | **模式坍塌** | 生成 5 万条，去重后剩 8 千 | seed 太少 / 只靠温度求多样性 | §6.2，扩 seed 和条件维度 |
| 3 | **judge 静默漂移** | 通过率没变，下游却退化 | judge 模型版本或 prompt 变了 | judge 锚点集当回归测试（§4.3） |
| 4 | **verifier 放水** | L1 通过率突然从 55% 涨到 90% | verifier 代码 bug（比如异常被吞了当通过） | 通过率突变告警 + verifier 自己的单元测试 |
| 5 | **eval 污染** | 离线 benchmark 猛涨，线上没变化 | generator 记得 benchmark 题目 | 语义近重复检测，不能只做 exact match（[07 §八](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)） |
| 6 | **静默丢掉一整类** | 某能力莫名退化 | 难度筛选或 verifier bug 让某类题被系统性丢弃 | 按类别统计丢弃率（§5.4） |
| 7 | **generator artifact 被学到** | 模型在合成风格上很强，真实输入上不行 | 合成数据有可识别指纹 | C2ST 判别器 + 看 top feature（§8.1） |
| 8 | **难度标签过期** | 训到中期梯度信号骤降 | 用离线固定的难度标签 | 在线探测 + 阈值随 policy 漂移（§5.1） |
| 9 | **代际自噬** | 逐代变平庸、长尾消失 | replace 而不是 accumulate | §7.3 四条防线 |
| 10 | **成本失控** | 账单是预算的 3 倍 | 只算了生成没算筛选；通过率远低于预期 | 先跑 1000 条测通过率，再外推预算 |

**关于 #1，我在自建的 Decagon 备战项目里实测踩到过**（[data/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/data/README.md)、[data/generate.py](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/data/generate.py)）：我造知识库文章时，如果只让 gold 文章包含全部主题术语，BM25 会直接把它送到 top-1、recall 顶到 1.0，后续所有方法就都测不出差异了。**修法是让同主题的多篇近邻文章都含全部术语，只有语义 focus 不同——强制区分度来自语义而非术语泄漏。**

这个坑对**造 eval 数据**是通用教训：**如果你造的评测集上所有基线都拿满分，问题不在方法，在数据。造数据的时候就要把"什么让这道题难"设计进去。** 那个项目里踩到的另外几个坑（训练/推理 prompt 不一致、decoder-only 批量生成必须左 padding、模型复读输入要把兜底率当指标报出来）在 [02_playbook.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/02_playbook.md) 里。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
