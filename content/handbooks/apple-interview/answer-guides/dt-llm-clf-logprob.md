---
id: dt-llm-clf-logprob
kind: concept
situation: 自由解释难稳定转换成过滤分数。
task: 生成可进行 calibration 的二元分类信号。
approach: 限制输出并从候选 token 概率算连续分数。
result: 按语言领域 calibration，误差由独立标签检查。
---

## 可以这样回答

自由解释难稳定转换成过滤分数。

让模型只输出 Yes 或 No，用这两个 token 的 logprob 算一个连续分数，再按语言和数据域在 development set 上分别对 threshold 做 calibration。连续分数能画 calibration curve、按需挪阈值；先写长解释再用正则找词，输出不稳，也没法 calibration。模型分只当开发过滤器，误差靠独立人标和固定评测来查。
