---
id: drustz-6b37ae0ab91f7cb605
section: mlsd
order: 159
level: A
title: 18 · Case：设计大规模分布式推理系统 · 13. 候选人的对位素材：哪段经历放在哪里
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 13. 候选人的对位素材：哪段经历放在哪里
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md
    type: primary
---
## 13. 候选人的对位素材：哪段经历放在哪里

| 章节 | 引用哪段真实经历 | 怎么说 |
|---|---|---|
| **§0 场景分叉** | 整个 mid-training 数据合成工作 | "我做的是离线批量侧——为 RL 合成和筛选 math/STEM 数据，目标函数是每百万 token 的成本和最终入库样本数，不是 p99。" |
| **§1 澄清问题 6（共享/可抢占）** | 共享 GPU 池、被其他团队抢占是常态 | 这个问题是**你的主场入口**，问完就能自然转到 §4 |
| **§2 goodput 定义** | 质量特征筛选（自包含性 / 矛盾信息 / 假设是否给足）会淘汰掉一部分产出 | "所以我的分母是**最终进入数据集的样本数**，不是生成的 token 数" |
| **§3 在线（全节）** | ⚠️ **没有** | 用 §3 开头的诚实边界话术，明确标注，然后主动把话题引向离线 |
| **§4.2 探测筛选 ⭐⭐⭐** | 16 条探测 → 全对全错丢弃 → 128 条正式；约 12% 算力用于筛选；与 DAPO dynamic sampling 同思想 | **最强的一段**。要能现场算出 12.5% 盈亏平衡点，以及 16 条全对时 95% 下界 0.83 这个诚实的局限 |
| **§4.3 AIMD ⭐⭐⭐** | 自建 pause/resume 框架、动态申领/让出资源、TCP 式自适应并发 | 重点讲"**区分容量类失败与样本类失败**"这个踩过的坑——这是真做过才会有的细节 |
| **§4.5 流水线背压** | 多阶段 LLM 流水线：question rewriting → answer rewriting → QA 转换（不可验证转可验证） | 讲"每阶段独立 job + 数据集做边界"的理由是**重跑成本**，以及各阶段 token 成本差一个量级 |
| **§6 抢占恢复 ⭐⭐⭐** | pause/resume 框架 | 检查点粒度公式 + id 幂等 + "resume 只能验 id 覆盖率不能验输出" |
| **§7 多租户** | 共享池的实际竞争经验 | 讲"机会性层能不能用取决于检查点粒度"这条因果链 |
| **§9-6 静默截断** | 手动检查 trace 发现学习行为异常（格式化推理、失控推理、错误推理、reward hacking） | 迁移过来：**我的习惯是手动读原始 trace，不是只看聚合指标**——静默截断这类问题只有读 trace 才能发现 |
| **§9-12 judge 不一致** | LRM-as-judge 在不同题目上对同一标准判得不一致 | 这是一手观察，讲"judge 的一致性本身要当监控指标"很有说服力 |
| **§2 / §9 "指标在骗你"** | Anthropic take-home：证明 ROUGE 在预测不安全回复上 AUROC 只有 0.569（≈掷硬币），自建 claim 级 grounding grader 达 0.844，confidence interval不重叠；137 对扰动测试套件分层报检出率；两个 refuted prior 如实写进报告 | 迁移成方法论：**"我的默认动作是先验证指标本身是不是在测它声称在测的东西"**——nvidia-smi 利用率、平均延迟、raw throughput 都属于这一类 |
| **成本/取舍的严谨性** | Decagon 备战项目：手写 reverse-KL on-policy distillation、过程奖励 vs 结果奖励对照实验、四个实测踩到的坑 | 用来证明"我会做对照实验而不是背结论"，可放在量化那节 |
| **Meta 经历** | Instagram Reels / Facebook Feed 推荐建模；内部数据分析 agent（多 agent sampling表格 → sandbox 写代码分析 → 综合假设供下轮线上实验） | 推荐系统那段可以支撑"大规模在线系统的指标直觉"，但**不要说成 LLM serving 经验**；数据分析 agent 那段可以支撑"多阶段流水线设计" |
| **不能碰的** | 金融/交易、在线 serving oncall、MoE serving 优化、多模态 | 直接说没做过，然后给出"我会怎么验证"的路径 |

### 三句可以直接背的诚实边界话术

1. **在线 serving**：「在线这侧我是从引擎实现和论文层面理解的，容量和成本我能现场推；但我没背过在线 pager。要听真实事故复盘的话，我能讲的是离线批量侧的——共享池抢占导致 job 反复重启、以及我们怎么用自适应并发把它稳住。」
2. **具体引擎版本细节**：「vLLM/SGLang 的具体版本行为我不敢打包票，这类东西迭代太快。我确定的是机制层面的取舍——比如 KV 抢占是重算还是 swap、chunked prefill 解决什么问题。落地前我会先跑一遍基准测出来，而不是引用一个可能过期的数字。」
3. **MoE / 多模态**：「我没做过 MoE 的 serving 优化，也没有多模态经验。MoE 我知道它更 memory-bound、需要 EP 和 all-to-all、以及专家负载不均是主要问题，但我没有一手的调优经验，这块我会先做基准而不是先给方案。」

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
