---
id: drustz-04775f818f3bf48bee
section: mlsd
order: 100
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 16. 候选人的对位素材：哪段经历用在哪一节
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 16. 候选人的对位素材：哪段经历用在哪一节
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
## 16. 候选人的对位素材：哪段经历用在哪一节

| 我的真实经历 | 用在哪一节 | 怎么说（一句话版） |
|---|---|---|
| **Anthropic take-home：ROUGE AUROC 0.569 vs claim 级 grounding grader 0.844，CI 不重叠** | §3.2 为什么不能用 ROUGE｜§4.3 改造成可验证 | "我实测过 ROUGE 在这类判断上等于掷硬币，所以我的第一步不是换相似度指标，而是把目标拆成可验证的 claim。" |
| **137 对扰动测试套件，按扰动类型分层报检出率** | §5.3 Step 3 judge 的扰动测试 | "只看总一致率不够——judge 可能在两个答案都不错时跟人一致，却完全看不见事实错误。我会注入已知缺陷按类型分层报检出率。" |
| **两个 refuted prior 如实写进报告** | §3.1 元指标｜面试尾声的价值观陈述 | "评测团队的产品是可信的结论，不是好看的数字。我在那份报告里如实写了两个被推翻的先验假设。" |
| **LRM-as-judge 一致性问题：同一标准在不同题目上判得不一致** | §5.1 rubric 自洽性行 | "我在生产里踩过这个坑：同一条 rubric 在不同题上判得不一致。解法是把 rubric 拆成互相独立的二元 checklist，硬门在前、表达在后。" |
| **数据合成 pipeline：question/answer rewriting、不可验证题转可验证（QA 转换）** | §4.3 改造成可验证题｜§6.3 动态生成题 | "把不可验证题转成可验证题是我做过的事，同一套手法可以直接用来造评测题。" |
| **质量特征：自包含 / 无矛盾 / 假设给足** | §6.3 动态生成题的质量门 | "动态生成题必须过质量门，否则防污染变成引入噪声——分数掉了你分不清是模型不会还是题出错。" |
| **16 条探测 → 丢掉全对/全错 → 128 条，12% 算力用于筛选（≈DAPO dynamic sampling）** | §10.4 两阶段sampling与区分度筛题｜§7.1 难度分层 | "全对或全错的样本没有梯度信号，评测里对应的是没有区分度的题。同一套两阶段探测能在扫描上百个切片时省一大半。" |
| **batch inference框架：共享 GPU 池被抢占、pause/resume、TCP 式自适应并发** | §10.5 评测的工程现实 | "评测本身是大规模batch inference。跑 6 小时在第 5 小时被抢占就全白跑，团队就会开始绕过评测——评测的可靠性决定它会不会被执行。" |
| **手动检查 trace 发现格式化推理 / 失控推理 / 错误推理 / reward hacking** | §9.2 定性评审｜§12 失败模式 #11 | "这些在任何聚合指标上都看不见。所以我会在发布流程里固定安排读原始输出的环节，并且给它拦截权。" |
| **Meta：Reels / Feed 推荐建模，大规模在线实验** | §9.4 A/B 技术坑 | "在线实验的指标设计、cohort join、延迟指标我在 Meta 做推荐时是熟的。" |
| **Meta：内部数据分析 agent（多 agent sampling表格 → sandbox 写代码 → 综合假设供下一轮实验）** | §10 sampling策略｜§12 失败模式 | "我做过用sampling + 代码执行去生成可验证结论的系统，这套'先小样本探测再定方向'的思路和评测sampling是一致的。" |
| **Decagon 备战项目：手写 reverse-KL on-policy distillation、过程奖励 vs 结果奖励对照** | §10.6 judge distillation｜§5.2 judge 当 reward 的风险 | "我手写过 on-policy distillation，所以对'小 judge distillation后分布偏移'有直觉；过程 vs 结果奖励的对照实验对应到 judge 就是判过程还是判结果。" |
| **UW HCI 博士：construct validity、subgroup burden** | §2 构念错配｜§11.2 over-refusal的公平性 | "HCI 训练让我先问'这个指标测的是不是我们真正关心的东西'，以及'总体均值是否掩盖了某个用户群的负担'。" |

### 必须诚实标注的边界

| 边界 | 怎么说 |
|---|---|
| **没有大规模在线 serving / oncall 经验** | "线上实验方法论我在 Meta 做推荐时是熟的，但 LLM 对话产品的 serving 与 oncall 我没做过。像延迟抖动如何影响会话完成率这类，我只能给设计和验证方案，不能给经验数字。" |
| **没有金融 / 交易背景** | 直接说没有，并把话题拉回自己有的：可验证信号设计、数据管道、评测方法论。 |
| **没运营过大规模人工标注团队** | "我设计过标注 rubric 和一致性检查，但没有管理过几百人的标注运营。质量控制的具体手段（attention check、标注员分层、抽检比例）我知道结构，落地细节需要和运营团队一起定。" |
| **没做过 CBRN / 生物类 uplift 评测** | "我能把它做成可复现、可回归的流水线，但'什么算 uplift、专家对照组怎么设'需要领域专家定阈值。" |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
