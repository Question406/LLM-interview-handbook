---
id: dt-rlvr-data
kind: concept
situation: rule-based reward 需要可靠题目与 scorer。
task: 定义 RLVR 真正的数据单元。
approach: 题目、环境、verifier 和难度版本绑定。
result: 独立正确性与有效学习组验证反馈价值。
---

## 可以这样回答

rule-based reward 需要可靠题目与 scorer。

RLVR 的数据是题目加可验证的 scorer。数学答案、代码测试和工具状态能给 rule-based reward；开放摘要和自然度判不了对错，要单独用人类偏好，和 rule-based reward 分开记。每题绑定 scorer 版本，全对或全错的题先调难度，必要时先用 SFT 冷启动。
