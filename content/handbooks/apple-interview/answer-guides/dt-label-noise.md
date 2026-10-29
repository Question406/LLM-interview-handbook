---
id: dt-label-noise
kind: concept
situation: 更多标签可能只是放大错误标准。
task: 定位错标与合法分歧。
approach: 先查协议和一致性，再用模型提疑交人复核。
result: re-annotation sampling 改善一致性与独立评测。
---

## 可以这样回答

更多标签可能只是放大错误标准。

先查 annotation guidelines 和人际一致性 $\kappa$，再用模型找可疑标签、交给人复核。Confident Learning 能估计 label noise，找出来的样本由人确认后再改，别让模型自动翻转全部标签。training set 和 evaluation set 都要查，错标多的时候，加样本只会放大问题。
