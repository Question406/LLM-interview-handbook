---
id: drustz-f967bd1a6949e26ac9
section: mlsd
order: 178
level: A
title: 19 · Case：设计 agent 能力 benchmark · 16. 候选人的对位素材
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 16. 候选人的对位素材
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
## 16. 候选人的对位素材

### 16.1 素材 → 用在哪一段 → 怎么说

| 我的真实经历 | 放在哪节 | 一句话怎么带出来 |
|---|---|---|
| **过程奖励 vs 结果奖励对照实验**（153 条退款轨迹，final_only 全平局；加效率项后 skip_step 0.800 > compliant 0.750） | §4.2 | "这件事我量化过——同一批轨迹上，只看结果时合规和三类违规完全平局；一旦加上效率项，跳步反而赢。" **这是全篇最有力的一手数据，务必讲。** |
| **137 对扰动测试套件，按扰动类型分层报检出率**（Anthropic take-home） | §4.3 反事实探针 | "成对任务的行为差分才是能力证据——我在一个 take-home 里就是这么建的 grader 测试集，而且是分层报检出率，因为总检出率会掩盖对某一类完全无感。" |
| **证伪 ROUGE：AUROC 0.569 vs 自建 grader 0.844，CI 不重叠** | §2.3、追问 7 与 11 | "一个看起来天经地义的自动指标可能和你关心的量几乎无关，而且这是两天内能证伪的。所以我造 verifier 的第一件事是拿人工标注给它算 AUROC。" |
| **两个 refuted prior 如实写进报告** | §6.2 覆盖缺口、§8.3 不承诺零污染 | "我倾向于把证伪的假设和已知缺口写在报告第一页而不是附录——上次 take-home 里我把两个被推翻的先验如实写进去了。" |
| **自适应难度阈值：16 条探测 → 丢弃全对全错 → 128 条正式，12% 算力**（Reflection） | §6.3、§10.2 自适应 $k$ | "我在 RL 数据筛选里用的是两阶段探测调度，同样的东西可以做成 benchmark 的自适应 $k$。但有个关键差异：RL 里 $p{=}0$ 的题该丢，benchmark 里不能丢。" **这个"关键差异"是加分点，说明不是照搬。** |
| **QA 转换：不可验证题 → 可验证题**（Reflection 数据合成 pipeline） | §6.2 可验证性阶梯 | "把任务往可验证阶梯上推是我做过的具体工作，但要说清它不是无损的，所以要留 L5 子集做对齐。" |
| **质量特征：自包含 / 无矛盾信息 / 假设给足** | §6.1 任务验收 | 直接映射成 agent 任务的三条验收：初始状态完整、环境无矛盾记录、任务描述不缺 agent 无法推断的前提。 |
| **pause/resume batch inference框架、动态申领资源、TCP 式自适应并发**（Reflection） | §10.3 | "agent eval 的负载形态和 RL rollout 几乎一样——大量并行、长尾、会被抢占。我为后者自建过调度，可以直接复用。" |
| **LRM-as-judge 横向不一致**（同一标准在不同题目上判得不一致） | §11 第 11 条、追问 11 | "judge 的问题往往不是整体准确率低，是在不同子群上松紧不一，全局 agreement 看不出来——所以calibration要分组做。" |
| **手动检查 trace 抓到格式化推理 / 失控推理 / 错误推理 / reward hacking** | 追问 6 | "新的作弊方式只能靠读轨迹发现。我手动看 trace 时抓到过四类异常，聚合指标上完全看不见。" |
| **Decagon 项目里踩的四个坑**（指标好到和上界一样其实是记忆；微调后比不微调更差；自造偏好标签用独立指标验出是噪声；MPS 静默 bug 让 87% 输出不可用） | §2.1 可诊断、§11 | "我有一个直接的教训：指标好看到和理论上界一位不差时，第一反应应该是怀疑而不是高兴——那次是任务退化成了记忆。还有一次是我自己写的指标被钻空子，IF 分数从 0.10 涨到 0.80 但结论完全反了。" **"指标本身也会被 hack，尤其是你自己写的那个"这句很适合放在 §11 收尾。** |
| **reverse-KL on-policy distillation 手写实现** | 一般不用；被问到"benchmark 结果怎么反哺训练"时可以带一句 | 只在追问训练闭环时提，不主动展开。 |
| **Meta：Instagram Reels / FB Feed 推荐建模** | §2.1 与线上相关性 | "离线指标和线上指标背离这件事在推荐系统里是常识，我有过这个直觉训练。" 但要说清那是 2022–2023 的推荐场景，不是 agent。 |
| **Meta：内部数据分析 agent**（多 agent sampling表格 → sandbox 写代码分析 → 综合假设供下一轮线上实验） | §5.3 沙箱、§6.1 真实任务采集 | "我做过一个在 sandbox 里写代码做数据分析的多 agent 系统，所以对'环境里能拿到什么、副作用怎么隔离'有第一手感觉。" |

### 16.2 诚实边界与话术

| 边界 | 怎么说 |
|---|---|
| **没造过对外发布的 agent benchmark** | "我没有从零建过一个对外发布的 agent benchmark。我做过的是相邻的两件事：为 RL 造可验证任务并做可解率分层，以及为一个具体任务从零建 grader 并用人工标注验证它。这道题我会按这两段经验的方法论来答，涉及公开发榜特有的问题（提交频率限制、防反推）我只有阅读层面的理解。" |
| **没有 LLM 产品的线上 serving / oncall 经验** | "大规模在线实验本身我在 Meta 做推荐时做过——指标设计、延迟指标 join、cohort 分析。但 LLM/agent 产品的线上 serving 和 oncall 我没做过，所以离线到线上的相关性验证这一段我给的是设计，不是经验。真做的话我会先找有 oncall 经验的同事calibration指标口径和最小可检测效应量。" |
| **没有金融 / 交易领域经验** | 如果题目落在交易 agent 上：**不要编**。"这个领域我没有背景，所以我不会假装知道哪些约束是硬的。我会先花时间和领域专家一起把'硬约束清单'列出来——因为这道题里过程约束的定义完全依赖领域知识，列错了整个 benchmark 就是错的。" 这个回答本身是加分的，因为它准确指出了领域知识在本题中的作用位置。 |
| **推荐系统经验的时效性** | "我在 Meta 做的是 2022–2023 的推荐建模，那个时代的 agent 和现在的 tool-calling agent 不是一回事。我从那里带出来的是离线/线上指标背离的直觉，不是 agent 的经验。" |
| **公开 benchmark 的数字** | 永远说量级不说小数点，永远带版本（Verified vs 原版 vs Pro）和 scaffold 限定。"这些数字我是读来的不是跑出来的，量级大致是……但 agent benchmark 的分数强依赖 harness。" |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
