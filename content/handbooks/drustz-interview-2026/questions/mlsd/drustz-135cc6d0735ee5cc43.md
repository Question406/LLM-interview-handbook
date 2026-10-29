---
id: drustz-135cc6d0735ee5cc43
section: mlsd
order: 99
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 15. 常见追问 + 应答要点
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 15. 常见追问 + 应答要点
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
## 15. 常见追问 + 应答要点

**Q1「只给你一周和 5000 美元，先建什么？」**
① 从生产日志聚类抽 300 条覆盖头部意图的 prompt（没日志就用公开分布并标注这个 gap）；② 人工双标 200 条判决建 judge 黄金集，先把 judge calibration住；③ 双向交换 + 跨家族 judge 跑这 300 条做 baseline；④ 建 50 条 canary。**先要一把calibration过的尺子，再去量东西**——顺序反了后面全部返工。

**Q2「judge 和人类不一致，信谁？」**
先看是不是**系统性方向**：judge 稳定偏好某一方 → 是偏差，信人类并修 judge；若是分散不一致且人类之间也不一致 → 说明任务本身有歧义，该修的是 rubric。**不一致的样本本身是最值钱的数据**，全部进人工裁决池并回流改 rubric。

**Q3「怎么证明你的离线评测能预测线上表现？」**
把它当成一个可验证的假设：收集过去 N 次发布的（离线分变化，线上主指标变化）配对数据，算相关性。相关性低就说明离线集不代表生产分布，要用日志聚类补题。**没有这个复盘的评测系统，本质上没人知道它有没有用。**

**Q4「模型升级了 judge 也升级了，分数涨 3 点，怎么解释？」**
解释不了，这一轮评测作废。正确流程：新 judge 与旧 judge 在同一批数据上双跑建立换算关系，再单独评估模型。这就是为什么每条结果要带四个版本字段、一次只变一个。

**Q5「Arena 排名上升但留存没变，怎么办？」**
两件事都可能是对的。Arena 的 prompt 分布不是你的产品分布，且它的偏好受长度与 markdown 驱动（所以才有 style control）。做法：按能力域把 Arena 分和自家日志切片分并排看，找出"Arena 涨但日志切片没涨"的域——那些通常就是被表面特征拉动的。留存是慢指标，用长期 holdback 量。

**Q6「多轮怎么评？」**
三档：① 真实日志回放（最真但只能测前缀，一旦模型行为改变后续轮就不可比）；② persona-conditioned user simulator（可扩展，但 simulator 本身要用真实日志验证其行为分布）；③ 人工多轮（金标准，最贵）。多轮的核心指标是**跨轮指令保持**和**上下文一致性**，不是单轮质量的平均。一致性用  $\mathrm{pass}^k$  思路报（见 [14 §8](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca)）。

**Q7「创意写作这种没有正确答案的，怎么评？」**
拆成三部分：**可验证约束**（字数、体裁、必须包含的元素、禁用词）→ 代码判；**相对偏好**（A/B 对比）→ judge + 人工，必须做长度和格式控制否则测的是排版；**多样性**（同一 prompt sampling N 次的 self-BLEU / embedding 距离）→ 自动算。绝不用单一分数。

**Q8「为什么不直接用 reward model 当 judge？」**
可以但不能只用。RM 输出的是标量、无解释、且它就是被优化的目标——用被优化的东西做验收是 Goodhart 的教科书情形。RM 适合训练中的快速筛选和 best-of-n；发布 gate 要用**独立冻结**的 judge + 人工。这与 [04 §7](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45) 的 verifier 独立性是同一条原则。

**Q9「竞品发布了，24 小时内要给出对比结论。」**
降级方案，且要**明确标注可信度等级**：从冻结集里抽 300 条流量加权样本 → 双向交换 + 两个不同家族 judge → 只报"是否有 >5pp 的明显差距"这种粗结论 + confidence interval → 附 20 条人工快速抽检。**明确写"该结论不能作为发布依据"**。诚实标注结论强度比给一个精确假数字更专业。

**Q10「怎么防止团队为了过 gate 而调 prompt？」**
① 关键 gate 用 private holdout，团队看不到题；② 查询次数记账，一个版本只能跑一次；③ 主指标之外设不可交易的 guardrail；④ 定期换血：eval 集按季度补充新题、退役被刷穿的题；⑤ 制度上把"eval 归属"和"模型归属"分开。这本质上是 Goodhart 的组织解法，不是技术解法。

**Q11「非英语怎么评？」**
不能假设英语上验证过的 judge 能迁移。每种目标语言要有**独立的人工双标集**和独立的 κ；低资源语言 judge 质量差到不可用时，只能靠小规模母语者人工 + 可验证任务（翻译回译、事实一致性）兜底。报告里要明确标注"哪些语言的结论是 judge 给的、哪些是人给的"。

**Q12「eval 集多久换一次？」**
分层：canary 永不换只增；冻结回归集半年到一年一个大版本且双跑重叠期；private holdout 每次模型代际更新时补充（因为时间切片会失效）；public smoke test 随时换。判断该换的信号是：**区分度消失**（所有候选模型分数挤在一起）或**与线上相关性下降**（Q3 的复盘数据）。

**Q13「样本量怎么定？」**
从"要检出多大的差异"倒推。胜率 50% 附近，独立比较 SE=$\sqrt{0.25/n}$，n=1000 → 95% CI ±3.1pp，连 2pp 都分不出；配对后有效方差按 $(1-\rho)$ 缩小，$\rho=0.7$ 时约需三分之一样本。**在报告里明确写出"本配置的可检出下限是 X pp"**，比事后解释更专业。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
