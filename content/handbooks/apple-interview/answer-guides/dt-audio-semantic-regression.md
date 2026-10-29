---
id: dt-audio-semantic-regression
kind: design
situation: 字错率变低但操作更容易出错。
task: 定位关键语义与下游决策损失。
approach: 按实体、否定、数字和权限 evaluation slices replay。
result: 任务成功与关键语义错误优先于总体 WER。
---

## 可以这样回答

字错率变低但操作更容易出错。

字词错误率不区分错误的任务代价。把音频、转录、意图参数和执行状态分段替换，检查否定词、数字与实体，再用有语义对照的授权音频与合成扰动验证。
