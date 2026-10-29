---
id: dt-sycophancy-data
kind: concept
situation: 礼貌附和可能赢得偏好却违背事实。
task: 让模型尊重用户也能纠正错误前提。
approach: 事实与态度分开标，构造立场 counterfactual。
result: sycophancy evaluation slices 改善，主观偏好不被当事实错误。
---

## 可以这样回答

礼貌附和可能赢得偏好却违背事实。

human evaluation 更偏爱客气附和的回答、给简短纠正打低分时，RLHF 就会奖励不诚实。数据上要拆开：用成对样本教模型纠正错误前提（chosen 按证据纠正，rejected 附和），annotation guidelines 把事实忠实和礼貌分成不同维度，评测单列 sycophancy evaluation slices。满意度高，单独证明不了模型诚实。
