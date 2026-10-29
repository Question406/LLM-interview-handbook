---
id: dt-verifier-counterfactual
section: panel
order: 33
level: S
title: Panel 情景：verifier 通过率 98%，合成推理数据为什么仍然伤模型？
quick: >-
  通过率取决于 verifier 测了什么，不能替代数据有效性。检查答案 leakage、测试覆盖、过程正确性和重复模板，并用 counterfactual
  样本审计 verifier；再用等预算 ablation study 区分过滤质量与任务难度。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 情景练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
---

## 题目描述

原创情景题。你生成了 100 万条代码或 mathematical reasoning 数据，98% 通过 verifier。训练后，公开题型涨 8 个百分点，独立的新模板集却掉 3 个百分点。训练预算只能再做三组短实验。

请提出有区分力的假设、verifier 审计方法和三组训练对照。不能只说“模型 overfitting 了”。数字均为练习设定。

## 解题思路与参考答案

先检查推理长度、训练与评测模板、token 预算、baseline 是否一致。高通过率至少有几种解释：题很简单；生成器看见答案；代码只适配公开测试；数学答案正确但过程不成立；大量样本只是同一模板替换数字。它们需要不同的数据修复。

### 先审计再训练

按题型、难度、生成器版本和重复 cluster sampling。代码增加 hidden tests、edge-case inputs 和检查副作用；数学对可执行步骤做独立检查，对无法形式验证的过程做专家抽查。构造故意错误的候选：删除关键步骤、交换数字、硬编码示例答案、返回正确结果但破坏其他状态。观察 verifier 能否拒绝它们，并报告错误 acceptance rate 而不只报告通过率。

counterfactual 样本是 verifier 的攻击测试，不能保证覆盖所有错误。若 verifier 自己依赖同一 teacher，应追加不同机制的证据，如 executor、符号系统或人工审查。

### 三组短实验

对照 A 使用原始通过集；B 使用严格验证并去掉 near-duplicates 后的子集；C 使用与 B 相同验证标准、但提高中等难度和新模板覆盖的数据。三组从相同 checkpoint 开始，匹配总训练 token、更新步数和基础数据比例。B 的独立样本不足时重复训练会改变重复次数，应记录并另做可行的等独立样本对照，不能声称控制了所有因素。

A 对 B 主要检验 data quality checks，B 对 C 主要检验覆盖和难度，但严格过滤也会改变分布，需要报告保留率和各桶变化。test set 按模板家族或生成程序划分，不能只随机切行。

## 面试追问

**所有过程都要正确才能用吗？** 取决于监督目标。若过程不可验证，可以只监督经独立验证的答案，或剔除过程；不能把未知真假的过程当 gold standard。

**选最难的数据是不是更好？** 不一定。student 完全解不出的题可能没有有效学习信号；需要测难度和学习收益，保留可学的中间区间并验证迁移。

**什么时候停止合成？** verifier 审计失败、覆盖不再扩张或单位预算的独立测试收益消失时，先修验证与任务生成，不继续堆数量。
