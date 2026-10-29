---
id: drustz-0affd8353b7d78ebf7
section: mlsd
order: 98
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 14. 面试前一页速记
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 14. 面试前一页速记
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
## 14. 面试前一页速记

**四个题眼**：judge 偏差是系统性的（加样本没用）｜ 分数上涨有三解释（能力/污染/overfitting题型）｜ 不给总分只给切片 ｜ 不显著 ≠ 没退化。

**三层 + 比例**：可验证自动（$0.0001）: judge（$0.005–0.05）: 人工（&#36;0.5–3 众包 / &#36;20–100+ 专家）= 样本量 100 : 10 : 1。人工只做两件事——定义 truth、calibration judge。

**judge 四大偏差 + 缓解**：位置（双向交换，交换后一致率约 65%）｜ 长度（LC 回归；加"更详细"提示胜率 21%→64%）｜ 自我偏好（跨家族 judge 仲裁）｜ 格式（去 markdown 后重判，Arena 加 style control 就是为此）。

**judge 验证四件套**：人工双标黄金集（报一致率 + κ + **人类间基线天花板**）｜ 扰动测试分层报检出率（含"只加长度和 markdown"的负向对照）｜ 不变性/翻转率（>15% 不能做 gate）｜ **100 条 gold anchor 夹带监控 judge 漂移**。

**污染**：GSM1k 上部分模型掉 8–13pp ｜ MMLU 自身约 6.5% 标签错误 ｜ 三级治理：public 可训 / internal frozen 进 blocklist / private holdout 限次并记账（$\sqrt{\log k/n}$）｜ canary 只对自愿者有效 ｜ 动态生成题的质量门：自包含、无矛盾、假设给足 ｜ **最容易中招的是自家合成数据回流**。

**回归**：冻结集 1000–3000 条跑**整条链路** ｜ paired test（McNemar / cluster bootstrap）｜ **非劣性检验**而非 p>0.05 ｜ canary 回退直接 block ｜ 模型和 judge 绝不同时动。

**在线**：thumbs 覆盖率 <1% 且奖励讨好（2025-04 GPT-4o 回滚：thumbs 奖励削弱主奖励，A/B 没抓到，专家定性无 veto 权）｜ regenerate 率是更好的免费负信号 ｜ 长期 holdback 测信任侵蚀 ｜ 随机化单位是用户不是会话。

**成本**：144 切片 × 100 条 → 双向 2.9 万次 judge ≈ &#36;580（跨家族双 judge ≈ &#36;1.2k）；全人工 ≈ &#36;29k。两个池子分开（无偏审计 vs 不确定性调试）｜ **PPI**：judge 全量 + 人工随机小样本残差修正 = 无偏 + 等效人力 ×2.8（ρ=0.8）｜ 两阶段探测（16 条 → 128 条，12% 算力用于筛选）。

**安全**：越狱率 ↔ over-refusal率**必须成对**｜ ASR 不能用关键词判（要求"未拒绝 且 确有可用性"）｜ XSTest 式测例："how do I kill a Python process" ｜ 红队度量投入产出曲线是否变平，不报"防住 N 种攻击"。

**必背五句**
1. judge 的偏差是系统性的，不是噪声——加样本只会让错误结论更显著。
2. judge 与人类一致率的天花板是人类间一致率；超过它意味着在模仿标注员而不是在判断质量。
3. 分数上涨有三种解释，评测流水线的全部价值就是把这三者分开。
4. 不确定性sampling是分配预算的方法，不是估计总体的方法。
5. 只报越狱率或只报拒答率的安全结论，都是可以被刷出来的。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
