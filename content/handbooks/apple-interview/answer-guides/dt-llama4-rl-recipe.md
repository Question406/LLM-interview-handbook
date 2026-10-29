---
id: dt-llama4-rl-recipe
kind: design
situation: 公开 RL 配方含多类数据和阶段选择。
task: 解释数据承担的能力和行为角色。
approach: 区分公开事实与可迁移假设，按任务验证配方。
result: 不把别家比例当 Apple 内部实践或万能最优。
---

## 可以这样回答

公开 RL 配方含多类数据和阶段选择。

Llama 4 走轻量 SFT → 在线 RL → 轻量 DPO，理由是 SFT 太多会限制后续在线探索。数据侧先砍掉过易样本，再按 current policy 的 pass@$k$ 动态筛题、丢弃零优势组，batch 里混合能力与提示模板。过滤随 policy update 反复做，每训一轮就用新策略重筛。
