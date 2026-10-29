---
id: drustz-1ed750c838f89c5e6e
section: mlsd
order: 140
level: A
title: 17 · Case：设计合成数据生成系统 · 14. 面试前一页速记
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 14. 面试前一页速记
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
## 14. 面试前一页速记

**五种目的**：总量 / 长尾 / 隐私 / 标注成本 / 难度控制。**对"是否匹配真实分布"的要求相反**——补长尾故意偏，隐私替代必须像。

**唯一有效指标**：matched-compute ablation 在**纯真实** held-out 上的下游提升。generator 自评 / judge 均分 / "像真的" 全都不是证据。

**六种范式**：模板 · zero-shot · self-instruct（ROUGE-L>0.7 去重）· evol-instruct（in-depth + in-breadth + 淘汰失败进化）· 从真实数据反推（backtranslation / rephrase，**首选**）· distillation + rejection sampling。

**多样性来自 seed，不来自 prompt。**（Cosmopedia 教训）

**三级漏斗**：L0 规则（~0 成本）→ L1 verifier（硬错误）→ L2 模型 judge（语义）→ L3 人工分层抽检（**calibration，不是过滤**）。抽检要抽通过的**和**被拒的。

**质量特征拆成二元判定**：自包含 / 无矛盾 / 假设充分 / 答案唯一可判定 / 与 seed 一致。**别打 1–10 分。**

**judge 是需要回归测试的模型组件**：固定人工锚点集 + κ 一致性 + 版本号。

**难度是（题, 模型）的函数**：16 条探测 → 丢全对全错 → 128 条正式；~12% 算力；= DAPO dynamic sampling。RL 要 0<p<1，SFT 要 p→1，eval 要冻结。

**去重三层 + 骨架normalization**：exact → n-gram → embedding 聚类；数字/实体替占位符后再比。**必须对 seed 和所有 eval 集去重。**

**坍塌**：早期尾部先消失（指标可能还在涨）→ 晚期方差塌缩。**replace 会坍塌，accumulate 不会**（保留真实数据）。四防线：真实锚定 / 代际比例上限 / 冻结reference model监控分布 / 外部真实锚定集。有 verifier 的可验证域风险低。

**分布偏移**：C2ST 判别器 AUC（并看 top feature）· TSTR vs TRTR · precision/recall 分解 · MAUVE。**"越像越好"是错的，取决于目的。**

**隐私**：合成 ≠ 匿名。canary exposure 测记忆；准标识符组合重识别 NER 抓不到；DP-SGD + **后处理免疫性**（sampling不额外耗预算）。

**不该做的时候**：真实数据便宜 / 分布极难建模 / 无 verifier 无人评 / 造 eval 集 / teacher 不具备该能力 / 已自产自销两三代。

**成本**：分母是**通过闸门的条数**。分层生成 + 批处理（~50% off）+ prompt caching（读 ~0.1×，写 1.25×/2×，rubric 前缀固定天然契合）。

**必背句 1**：合成数据是信息的重新分配，不是信息的创造——问"新信息从哪进来"。
**必背句 2**：judge 不是 ground truth，是需要被calibration和回归测试的模型组件。
**必背句 3**：我不看每千 token 单价，我看每条进库样本的成本。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
