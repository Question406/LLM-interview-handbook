---
id: drustz-0cad2a33eaccee7a59
section: mlsd
order: 131
level: A
title: 17 · Case：设计合成数据生成系统 · 5. 难度控制与梯度信号：合成数据最被低估的一节 ⭐⭐⭐
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 5. 难度控制与梯度信号：合成数据最被低估的一节 ⭐⭐⭐
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
## 5. 难度控制与梯度信号：合成数据最被低估的一节 ⭐⭐⭐

这一节是我最有真实素材、也最能拉开差距的地方。

### 5.1 核心洞察：难度不是题目的属性，是（题目, 模型）的函数

一道题"难不难"取决于当前 policy 的可解率。所以：

- **离线标注的难度标签会过期**。你标的"难题"训了两周之后对新 checkpoint 可能是送分题。
- **难度筛选必须在线做，且阈值要随模型漂移**。

### 5.2 我实际做的：自适应难度阈值 + 小批量探测

```text
对每道候选题：
  1) 先用当前 policy 跑 16 条 rollout（小批量探测，用较短的 max_tokens）
  2) 估计可解率 p̂
     - p̂ == 1（全对）→ 丢弃：没有梯度信号，纯烧算力
     - p̂ == 0（全错）→ 丢弃：要么太难、要么题/verifier 有问题
     - 0 < p̂ < 1     → 保留
  3) 保留的题再跑 128 条正式 rollout
筛选（探测 + judge）总共约占 12% 的算力预算
```



**为什么 12% 是可以接受的**：设探测  $k_p$ =16、正式  $k_f$ =128、保留率 r。若探测与正式的单条成本相同，探测开销占比 =  $k_p$  / ( $k_p$  +  $k_f$ ·r)，r≈0.6 时约 17%。实际做到 ~12% 是因为探测阶段用了更短的 max_tokens 并对明显全错的题提前终止。**面试里能把这个算术当场算出来，比报一个数字有说服力得多。**

**这个思想和 DAPO 的 dynamic sampling 是一致的**——oversampling prompt，然后把准确率为 1 或 0 的 prompt 过滤掉，保证 batch 里全是有有效梯度的样本。能主动指出"我们独立做到的东西和 DAPO 是同一个思想"，既诚实又显得读过文献。

### 5.3 不同用途的难度目标（这张表能直接答追问）

| 用途 | 期望可解率 | 理由 |
|---|---|---|
| **RL / GRPO 类** | 0 < p < 1，最好在 0.2–0.8 | p=0 或 1 时组内 advantage 全为 0，梯度为 0。这是硬约束不是偏好 |
| **SFT 示范数据** | 高（p 接近 1 的题里选正确 trace） | SFT 要的是干净示范，不是挑战 |
| **Curriculum 早期** | 0.6–0.9 | 先建立格式和基本能力 |
| **Curriculum 后期** | 0.1–0.4 | 逼近能力边界 |
| **Eval 集** | 覆盖全谱且**固定不变** | eval 的难度不能随模型调，否则不可比 |

### 5.4 难度筛选的副作用（主动讲，是加分项）

1. **系统性丢掉一整类题**。如果某类题 verifier 有 bug 导致永远判错，它们会全部落在 p̂=0 被丢弃——你会**静默地**失去这一整类能力。**防御**：对被丢弃的样本按类别统计，某个类别丢弃率异常高就人工看。
2. **难度筛选会和数据分布筛选耦合**。保留下来的题在主题上可能严重偏斜（比如全是某一类代数题）。**防御**：难度筛选之后再做一次分层抽样，保证 taxonomy 覆盖（§6.4）。
3. **探测本身有方差**。16 条 rollout 估计 p 的标准误在 p=0.5 时约 0.125。所以"全对/全错"这个判据其实是在做一个**保守**的丢弃：真实 p=0.05 的题有 (0.95)^16 ≈ 44% 的概率被 16 条探测判成全错。这是可接受的（我们不缺题），但如果题很贵就要加大  $k_p$  或做序贯检验。**能把这个概率算出来，是真的做过这件事的标志。**

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
