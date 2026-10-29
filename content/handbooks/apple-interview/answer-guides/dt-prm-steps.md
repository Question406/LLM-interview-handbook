---
id: dt-prm-steps
kind: concept
situation: 过程标签贵且可能被优化者利用。
task: 判断何时值得增加逐步监督。
approach: 可执行任务先用规则，过程缺口再标。
result: 成本与独立任务收益支持 PRM，不假定更细更好。
---

## 可以这样回答

过程标签贵且可能被优化者利用。

先问这道题能不能直接验证：能执行验证的先用 rule-based reward，只有最终答案检查发现不了的过程错误，才值得做人工或神经 PRM。逐步监督更省样本，但人工标注贵，要先统一步骤怎么划分并保留独立的结果检查，过程编造的 trajectories 不进 CE 正例。DeepSeek 不用神经 PRM，是因为它在大规模 RL 里会被 hack，重训又贵。
