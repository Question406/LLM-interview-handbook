---
id: dt-eval-no-gold
kind: concept
situation: 没有 gold labels 且专家预算有限。
task: 建立可扩展但有 calibration 依据的评价。
approach: 由专家明确 rubric，并说明 ambiguous cases 如何判断，自动检查可验证部分。
result: 独立专家抽查支持 judge，未知不强行打分。
---

## 可以这样回答

没有 gold labels 且专家预算有限。

先按任务能不能自动判分来分配专家时间。能执行、有标准答案的做成自动评测，人只抽查；专家写评分标准、标 edge cases，再用少量样本 对 model scores 做 calibration。未经 calibration 的 LLM judge 只能辅助开发，生产日志也不能直接当 evaluation set。
