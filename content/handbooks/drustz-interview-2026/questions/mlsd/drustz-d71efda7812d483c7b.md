---
id: drustz-d71efda7812d483c7b
section: mlsd
order: 133
level: A
title: 17 · Case：设计合成数据生成系统 · 7. 模型坍塌（model collapse）⭐⭐⭐
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 7. 模型坍塌（model collapse）⭐⭐⭐
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
## 7. 模型坍塌（model collapse）⭐⭐⭐

### 7.1 现象与机制

反复用自己（或同代模型）生成的数据训练下一代，会发生**代际退化**。Shumailov 等人 2024 年发表在 Nature 的工作把它命名为 model collapse，并区分了两个阶段：

- **早期坍塌**：分布的**尾部先消失**。模型仍然"看起来正常"，但罕见事件、少数群体、长尾表达被逐代抹去。**这是最危险的阶段——指标可能还在涨。**
- **晚期坍塌**：方差持续收缩，输出趋于同质、趋向少数几个模式，与原始分布几乎无关。

三个误差来源：**统计近似误差**（有限sampling必然丢尾部）、**函数表达力误差**（模型族表达不了真实分布）、**函数近似/优化误差**（训练本身的偏差）。三者逐代累积。

同期 Alemohammad 等人的 "Self-Consuming Generative Models Go MAD" 给出同样结论的生成模型版本：自噬循环里如果每代没有足够的**新鲜真实数据**，质量或多样性之一会逐代下降。

### 7.2 最重要的反直觉结论：replace vs accumulate

Gerstgrasser 等人 2024 的工作指出：坍塌的前提是**用合成数据替换（replace）真实数据**。如果每代是**累积（accumulate）**——真实数据保留、合成数据往上加——测试误差存在一个与代数无关的**有限上界**，坍塌不再发生。

**这条在面试里价值极高**，因为它把"模型坍塌"从一个吓人的名词变成一个**具体的工程约束**：

> 别丢真实数据。每一代训练集都必须包含全部（或固定比例的）原始真实数据，合成数据只做增量。

同时要诚实指出这不是完全定论：Dohmatob 等人的 "Strong Model Collapse" 一系的结果表明，在某些设定下**即便只掺入很小比例的合成数据也会造成可测量的退化**，且更大的模型未必更稳健。所以正确的表述是：**累积策略显著缓解坍塌，但"多少合成数据是安全的"必须由你自己的 ablation 回答，不能引用一个通用比例。**

### 7.3 四条防线（每条配一个监控指标）

| 防线 | 做法 | 监控指标 |
|---|---|---|
| **1. 真实数据锚定** | 每代训练集必须含固定比例的原始真实数据；accumulate 而不是 replace | 真实数据在训练 token 中的占比（设下限告警） |
| **2. 代际比例上限** | 给每条数据打"代际标签"（gen-0 = 真实，gen-1 = 用 gen-0 模型生成，…），限制 gen ≥ 2 数据的总占比 | 各代际的 token 占比曲线 |
| **3. 分布监控** | 每代对比：长度分布、vocabulary覆盖、perplexity 分布（用一个**冻结的**reference model算）、embedding 聚类熵、罕见 token 频率 | 尾部质量占比是最灵敏的早期信号 |
| **4. 外部验证锚** | 用一个**永不参与生成、永不更新**的真实 held-out 集 + 定期人评做终审 | 该集上的指标 + 人评一致率 |

**第 3 条里"用冻结的reference model算 perplexity"这个细节很重要**：如果用当代模型自己算，坍塌的模型会觉得自己的输出perplexity很低——自证清白。

### 7.4 什么情况下坍塌风险高 / 低

| 风险 | 情形 |
|---|---|
| **低** | 有强 verifier 的可验证域（数学答案、代码测试）。因为筛选把错误挡住了，信息实际上是从 verifier 注入的，不是从模型自身循环出来的 |
| **低** | 单次一代生成，不迭代 |
| **中** | 用一个更强的外部 teacher distillation（是知识转移，不是自噬），但会继承 teacher 的偏差 |
| **高** | 用自己上一代模型生成、且替换掉真实数据 |
| **高** | 开放式生成任务（创作、对话）+ 只有 judge 没有 verifier |

**高分句**：模型坍塌的本质是**信息没有新增，只是被反复resampling**。所以判断一个合成数据 pipeline 会不会坍塌，只要问一句：**这条 pipeline 里，新信息从哪里进来？** 如果答案是 verifier、真实语料、或人，就相对安全；如果答案只有"模型自己"，那就是在做分布的复印件的复印件。

### 7.5 诚实边界

> 我没有跑过跨多代自训练的长期实验——我做的是单代或两代的生成+筛选，坍塌是我按文献和分布监控在防，不是我亲自复现过的现象。我见过的是**单代内的模式坍塌**（生成几万条之后主题高度集中），那个我有直接的处理经验。

这么说比假装做过多代实验强得多，而且后半句给了真实素材。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
