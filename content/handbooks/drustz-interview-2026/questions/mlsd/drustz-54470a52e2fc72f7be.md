---
id: drustz-54470a52e2fc72f7be
section: mlsd
order: 142
level: A
title: 17 · Case：设计合成数据生成系统 · 16. 候选人的对位素材（哪段经历放在哪一节讲）
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 16. 候选人的对位素材（哪段经历放在哪一节讲）
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
## 16. 候选人的对位素材（哪段经历放在哪一节讲）

| 章节 | 用哪段经历 | 怎么开口 |
|---|---|---|
| §3.2 生成范式混用 | **Reflection：math/STEM 多阶段 LLM 流水线**（question rewriting / answer rewriting / QA 转换） | 「我现在的主责就是为 RL 合成和筛选 math/STEM 数据。我们不是一次生成，是一条多阶段流水线……其中价值最高的一步是把不可验证的题转成可验证的。」 |
| §4.2 质量特征 | **Reflection：自包含 / 矛盾信息 / 假设充分** 三个特征 | 「我们打的不是一个总分，是一组二元判定——因为……」 |
| §4.3 judge 一致性 | **LRM-as-judge 在不同题目上判得不一致** | 「这个我实际踩过：同一条标准，judge 在几何题上判得严、在应用题上判得松。」 |
| §5 难度控制 ⭐ | **16 条探测 → 丢全对全错 → 128 条正式；~12% 算力；对齐 DAPO dynamic sampling** | 本篇最强的差异化素材，**一定要讲**，并且把 12% 的算术当场算出来 |
| §7.5 坍塌 | **诚实边界**：只做过单代/两代，见过单代内模式坍塌 | 「跨多代自训练的长期实验我没跑过。我见过的是单代内的模式坍塌——生成几万条之后主题高度集中。」 |
| §9.3 隐私 / grounding 闸门 | **Anthropic take-home（医疗，可公开讲）**：ROUGE AUROC 0.569 vs claim 级 grounding grader 0.844，confidence interval不重叠；137 对分层扰动测试套件；两个 refuted prior 如实写进报告 | 「我做过一个医疗领域的评测项目，证明了常用的表面相似度指标在这个任务上约等于掷硬币……那套 claim 级 grounder 可以直接改造成合成数据的 L2 闸门。」 |
| §11.4 基础设施 | **共享 GPU 池被抢占 → 自建 pause/resume + TCP 式自适应并发** | 「合成数据这类任务throughput敏感、延迟不敏感、可中断，天然适合抢占式资源，但要自己解决续跑问题。我们的并发控制借了 TCP 拥塞控制的思路：成功加性增，失败窗口内乘性减。」 |
| §12 #1 天花板评测 | **Decagon 备战项目**：KB 近邻文章都含全部术语，强制区分度来自语义而非术语泄漏；四个实测踩到的坑 | 「我自己造过一个客服评测语料，第一版所有基线都接近满分——问题不在方法，在数据太好做。」 |
| §12 训练细节坑 | **同项目**：训练/推理 prompt 不一致、左 padding、复读输入要把兜底率当指标 | 追问"实现层面遇到过什么坑"时用 |
| §5 / §7 交叉 | **手动检查 trace 发现的学习行为异常**：格式化推理、失控推理、错误推理、reward hacking | 「筛数据不能只看指标，我会定期人工翻 trace。我翻出来过四类异常……」——这段极能证明"真的看过数据" |
| 通用背景 | **UW HCI 博士 → 实验设计、construct validity、subgroup slice 敏感度** | 见 [12](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) §2 的 90 秒定位 |
| **不要碰** | 金融/交易；大规模在线 serving 的 oncall；受监管数据的合规签字 | 「这是我的边界。我知道要问什么问题、要建什么测试，但没有生产责任的经验。」 |

**素材使用原则**（承接 [README §诚实性约束](?book=drustz-interview-2026&section=mlsd&question=drustz-3603ee66dfcfae4462)）：Reflection 和 take-home 的部分说"我做过"；本篇其余的系统设计说"我会先……我会用实验验证……"。**不要把设计方案说成历史结果。**

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
