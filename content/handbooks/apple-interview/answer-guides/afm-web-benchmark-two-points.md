---
id: afm-web-benchmark-two-points
kind: concept
situation: 新模型在 500 道题上从 70% 提升到 72%。
task: 判断增益是否可靠，定位改变来自哪些任务。
approach: 分析同题 paired outcomes、重复 sampling 与数据独立性，再做定向验证。
result: 报告 effect size 和 uncertainty，不能只凭总分做发布决策。
---

## 可以这样回答

我不会只根据 70% 到 72% 就说模型变强了。500 道题提高两个点只代表多答对了十题；我还需要看两模型在哪些题上发生变化。

如果新模型只把十道错题改对，其余都相同，这和它答对了五十道旧错题、又答错四十道旧对题，是两种证据。净收益相同，但第二种的行为变化和不确定性都更大。

我会先检查是否同样的 prompt、decoding 和预算，再做 paired comparison。如果很多题来自同一个模板，就按 template family 而不是单题估计 uncertainty。生成有随机性时，还要看重复运行是否稳定，并按任务类型检查 regression。

如果差异还不清楚，我会增加独立任务或重复实验，而不是继续围绕这 500 题调参。只有独立验证支持目标能力改善，而且关键任务没有明显退化，我才会建议推进发布。
