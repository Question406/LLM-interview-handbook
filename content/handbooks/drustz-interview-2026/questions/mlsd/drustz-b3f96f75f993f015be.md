---
id: drustz-b3f96f75f993f015be
section: mlsd
order: 170
level: A
title: 19 · Case：设计 agent 能力 benchmark · 8. 污染：agent benchmark 一样会被预训练吃掉
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 8. 污染：agent benchmark 一样会被预训练吃掉
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
## 8. 污染：agent benchmark 一样会被预训练吃掉

### 8.1 三种形态（第二种最难处理）

| 形态 | 具体 | 能否靠改写题目消除 |
|---|---|---|
| **任务/答案记忆** | 题干和 gold patch 就在训练集里（SWE-bench 的仓库、GAIA 验证集的题与答案都公开可下载——而大家报的 GAIA 分数多半就是验证集） | 部分可以 |
| **环境记忆** | 模型见过这个 repo / 这个网站的结构，不需要探索就知道文件在哪、表在哪 | **不能**。这是 agent benchmark 特有的、最难缓解的一类 |
| **运行时泄漏** | agent 在环境里当场搜到答案：联网、`.git`、测试文件、注释里的 TODO | 能，靠环境卫生（§5.3）——这是工程问题不是数据问题 |

### 8.2 检测手段

| 手段 | 做法 | 能查出什么 | 局限 |
|---|---|---|---|
| **时间切分** | 只用模型 cutoff 之后创建的任务 | 记忆型污染（最有力） | 需要持续的新任务来源 |
| **public / private 配对集** | 同分布造两份，一份从不公开 | 总体虚高幅度（一个数字就能说服人） | 造两份的成本 |
| **扰动敏感性** | 改变量名、数值、实体名，看分数掉多少 | 表层记忆 | 掉分也可能是任务变难了，要有对照 |
| **canary 串** | 公开集里埋唯一字符串，之后 probe 模型 | 证明被训过 | 只能证明有，不能量化影响 |
| **前缀补全** | 给题干让模型续写 gold 解 | 强记忆 | 只对 L1/L2 类任务有效 |

### 8.3 设计层面的防御（比事后检测重要）

1. **程序生成 + 参数随机化**：每次评测重新生成实例——这是全合成层最大的价值，也是唯一能长期免疫的路线。
2. **公开 dev / 私有 test**：dev 集给大家迭代，test 集只在发布时跑，**且只返回聚合分不返回逐题结果**（防止通过反复提交反推题目）。
3. **时间滚动**：每季度用新时间窗的任务替换 30%，并保留一小段重叠期用于新旧集的分数calibration（否则换题后的分数不可比）。
4. **许可壁垒**：SWE-bench Pro 只用 copyleft 仓库让它在法律上更难进训练集——聪明，但只是延缓。

**诚实边界（要主动说）**：不能承诺零污染。能承诺的是给出**污染上界的估计**和**一个不受污染的对照集**。这个立场和 [07 §8.3](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) 一致。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
