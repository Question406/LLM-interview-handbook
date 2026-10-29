---
id: afm-mock-screen-b
section: mock
order: 20
level: A
title: 45 分钟模拟 B：preference data 清洗、RM 训练与 bias 审计
quick: >-
  先确认偏好、tie 和 confidence weight 的含义，再训练 RM，最后检查长度、位置与 source
  bias。模型跑通后仍要用独立执行结果判断选择质量。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - 全流程模拟
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: 'HelpSteer2-Preference: Complementing Ratings with Preferences'
    url: 'https://arxiv.org/abs/2410.01257'
    type: primary
  - title: Length-Controlled AlpacaEval
    url: 'https://arxiv.org/abs/2404.04475'
    type: primary
---

原创模拟，所有数字与评分为教学约定。此卷与模拟 A 分开计时，不要求 45 分钟同时写完全部扩展。

## 候选人任务与时间
0–5 分钟：解释 a/b/q 的语义、软 tie 及训练/验证按 prompt 家族切分；5–28 分钟：闭卷完成 `afm-rm-train-pipeline-code`；28–35 分钟：跑手算与 edge-case tests；35–42 分钟：分析下面 counterfactual；42–45 分钟总结。

给 RM 的两个特征为“证据支持度”和“回答长度”。训练中正确回答几乎都较长，验证中新模型学会长篇客套。RM 的 pairwise accuracy 很高，固定候选上的执行成功率下降。请提出三种竞争假设，要求最少两项能区分假设的实验。

## 面试官参考与追问
预期先查 data leakage、长短混杂、验证样本是否来自 old policy。将候选冻结，人工核对证据，制作内容等价长短对照；独立报告 nearest neighbors hard examples 排序、Brier、top-1 成功和长度。模型权重检查只能提示相关性，不能独立证明偏差原因。

第18分钟若尚未训练通，提示先全 batch SGD；只扣需要提示的工程维度。第30分钟加入全 tie validation set，检查严格准确率应为 None。第38分钟问“多加几个 judge 投票是否解决”，预期说明相关错误与独立评价。额外编程可用 `afm-rm-soft-target-code` 和 `afm-rm-bias-audit-code`，不要占用本卷核心实现时间。

## 评分与复盘
五项各0–4分：标签语义、训练隔离、优化/指标、偏差诊断、沟通与测试。0未做，1明显错误，2提示后完成，3独立完成，4有可验证证据并说明限制。总分14且无验证 leakage 作为自练通过线。把“q 当样本权重”“验证参与 standardization”“用 RM 自己证明质量”记录为必须重练的问题，而非简单扣分后跳过。

复盘填写：首次跑通时间__；首个错误__；有效反例__；需要提示__；下一次只改进的两点__。题目未完成时照实记录，不因看过参考答案补写为独立完成。
