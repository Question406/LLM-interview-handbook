---
id: drustz-a702eafc08222f41ee
section: mlsd
order: 164
level: A
title: 19 · Case：设计 agent 能力 benchmark · 2. 指标先于方案：benchmark 自己怎么算成功 ⭐⭐⭐
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 2. 指标先于方案：benchmark 自己怎么算成功 ⭐⭐⭐
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
## 2. 指标先于方案：benchmark 自己怎么算成功 ⭐⭐⭐

这一节是本题和普通 eval 题的分水岭。**benchmark 的指标不是 accuracy，是"这台仪器好不好用"的元指标。**

### 2.1 七个元指标

| 元指标 | 定义 | 怎么量 | 不合格的样子 |
|---|---|---|---|
| **区分度** | 能分开真实能力不同的两个系统 | 取已知强弱对（大 vs 小模型、给工具 vs 不给工具、当前版本 vs 上季度版本），看分差 | 所有被测对象都 95% 或都 5% |
| **噪声下界 (test–retest)** | 同一系统重跑两次的分差 | 同一 checkpoint、同一配置跑两轮，看 $\lvert\Delta\rvert$ 的分布 | 噪声带宽 > 你要检测的效应量，此时整个 benchmark 不可用 |
| **可复现** | 半年后 / 另一台机器上能否重跑出同一个数 | 冻结镜像重跑历史版本 | 依赖漂移、时间漂移（§9） |
| **与线上相关性** | 离线名次能否预测线上结果 | 已上线的 N 个版本：离线分 vs 线上指标的秩相关 $\rho$ | $\rho$ 接近 0 时这个 benchmark 是装饰品 |
| **抗污染** | 训练集里含它时分数虚高多少 | public 与私有配对集的分差（§8） | 差 20pt 却仍在拿 public 分做决策 |
| **成本** | 一次完整评测的 &#36; 与 wall-clock | 直接测 | 一次跑 5 天 → 没人会在做决策前跑它 |
| **可诊断** | 失败能不能定位到原因 | 失败分类的分布，以及 infra failure 是否被单独计 | 只有一个总分 |

**先测噪声，再定题量。** 顺序反了的话，你会造出一台看起来很精密、但读数抖动比信号还大的仪器。

### 2.2 样本量算术（这个数字要能当场算）

未配对比较两个系统，每题跑一次，成功率 $p$，题量 $n$：

$$\mathrm{SE}(\Delta p) \approx \sqrt{\frac{2p(1-p)}{n}}$$

$p=0.5$、$n=500$ → SE ≈ 3.2pt → 80% power 下能可靠检测的差异约 $2.8 \times \mathrm{SE} \approx 9$pt。

配对设计（同一批任务上比两个系统，用 McNemar 或配对 bootstrap）：有效方差只由**不一致对**贡献。不一致率 $d=0.2$、$n=500$ → SE $\approx \sqrt{0.2/500} = 2.0$pt → 可检测约 5pt。

**如果每题只跑一次，agent 的 run-to-run 方差会整个进到 SE 里**，上面两个数字还要恶化。

> **高分句**：一个 500 题、每题跑一次的 agent benchmark，分辨不了 2 个点的差距——公开榜单上前三名彼此在噪声之内是常态。所以我的报告里主指标永远带 bootstrap confidence interval，模型对比永远用paired test而不是排名。

### 2.3 明确不能用的指标

| 不能用 | 为什么 |
|---|---|
| **单一总分** | 掩盖分层。总分 72% 里可能"写操作类任务只有 30%"，而写操作正是唯一会造成真实损失的那类。 |
| **pass@1 当发布 gate** | 它测的是单次的平均能力，不测一致性，因而不测可部署性。$p=0.7$ 的系统连续 8 次全对只剩 5.7%（§7）。 |
| **轨迹与人类示范的相似度** | 路径不唯一。这个指标会惩罚比人更聪明的解法（一次批量查询代替三次单查），奖励模仿。 |
| **LLM judge 的平均分做主 gate** | judge 偏差会被 agent 直接优化掉。主流 agent benchmark 刻意回避 judge 当主判分，这点值得主动说。 |
| **与人类偏好的相关性** | 在 agent 场景它奖励的是"总结写得漂亮"，而不是"数据库里那笔退款金额对不对"。 |

这里可以引一个我自己做过的实证（Anthropic take-home，医疗域，可公开讲）：**ROUGE 在"预测医生标注的不安全回复"这个任务上 AUROC 只有 0.569，基本等于掷硬币；换成自建的 claim 级 grounding grader 是 0.844，两个confidence interval不重叠。** 这件事的迁移含义是——**一个看起来天经地义的自动指标，可能和你真正关心的量几乎无关，而且这件事是可以在两天内证伪的**。造 agent benchmark 时第一件该做的事，就是拿人工标注给自己的自动 verifier 算一次 AUROC / 检出率，而不是默认它对。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
