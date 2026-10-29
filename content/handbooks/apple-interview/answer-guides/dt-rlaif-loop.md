---
id: dt-rlaif-loop
kind: concept
situation: 策略会适应 judge 的偏好与漏洞。
task: 防止模型给自己循环打高分。
approach: 冻结版本，规则与独立 human evaluation 持续校验。
result: 真实质量同步提高，不只看自评奖励。
---

## 可以这样回答

策略会适应 judge 的偏好与漏洞。

固定 judge 的版本，再用 human evaluation 和规则独立检查结果。策略会越来越会模仿 judge 偏爱的长文和套话，judge 要是每轮换成 current policy，就等于让模型给自己打分，最后 judge 给高分、human evaluation 却不涨。能直接验证的任务优先用 rule-based reward，human evaluation 分歧明显的题留给人来判断。
