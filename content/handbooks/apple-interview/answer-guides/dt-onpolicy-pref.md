---
id: dt-onpolicy-pref
kind: concept
situation: 旧 preference pairs 覆盖不到 current policy 的新回答。
task: 让监督跟上模型分布变化。
approach: current policy resampling 并独立标注或执行。
result: 新候选质量改善，旧对保留用途与适用版本。
---

## 可以这样回答

旧 preference pairs 覆盖不到 current policy 的新回答。

用当前模型重新 sampling，再重新比较好坏。旧 preference pairs 来自 old policy，模型现在会写的回答没人监督；直接拿 UltraFeedback 这类现成偏好集来训，监督的是别的模型的回答分布。可验证任务在线 sampling、用 rule-based reward 评分，主观偏好定期用 current policy 重采，交给人或 经过 calibration 的 judge 标。
