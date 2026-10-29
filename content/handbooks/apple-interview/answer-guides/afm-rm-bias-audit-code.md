---
{
  "id": "afm-rm-bias-audit-code",
  "kind": "coding",
  "situation": "同一对 A/B 回答分别按 AB、BA 展示；judge 返回 first、second 或 tie。",
  "task": "还原候选身份，返回四类计数、A 的平均分与 first-position selection rate。",
  "approach": "先按展示顺序映射回 A/B，再分类；两个概率指标分别使用 2n 与非 tie 展示数作为分母。",
  "result": "完整三行示例应得到 stable_a=1、stable_tie=1、inconsistent=1、swap_score=2/3、first_rate=3/4。"
}
---

## 可以这样回答

我会先做身份映射。AB 里的 first 是 A，BA 里的 first 是 B，所以两次都选 first 属于不一致，不能算 A 稳定获胜。

每条记录还原后分别进入 stable_a、stable_b、stable_tie 或 inconsistent，四个计数之和必须等于 n。只有一次 tie 的记录也算 inconsistent。

最后分别计算两个指标。Swap score 把 A/B/tie 记为 1/0/0.5，对全部 2n 次展示取平均。First rate 只看非 tie 展示中 first 的占比。全部 tie 时，前者是 0.5，后者返回 None。这个审计描述顺序敏感性，没有独立真标签时不能据此宣布回答质量或 causal bias。
