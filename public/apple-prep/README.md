# AFM 实战附件

全部数据是教学构造，没有用户真实日志；题目与评分不代表 Apple 原题或内部标准。

- tool_metrics.csv + tool_errors.jsonl：诊断1，总分与任务桶退化。
- reward_sweep.csv + judge_swaps.csv + reward_candidates.jsonl：诊断2，奖励优化与评审偏差。
- analyze_cases.py：把以上 CSV 放在同一目录，运行 `python3 analyze_cases.py`，只依赖标准库。输出描述统计，不提供因果归因或配对显著性。
- self_iteration.py：需要 PyTorch，运行 `python3 self_iteration.py`。CPU算术学生候选→独立精确验证→训练→开发集停止→一次最终测试；不是LLM或截图模型的实测结果。
- personal_evidence_template.md：个人经历待填写模板，未知数字写未测；不得将练习故事写成个人履历。

完整题面、参考答案、追问及自练评分位于 Apple 面试题本的“全流程模拟与个人材料”章节。
