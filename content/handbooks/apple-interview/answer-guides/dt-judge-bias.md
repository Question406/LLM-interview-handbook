---
id: dt-judge-bias
kind: concept
situation: judge 可能偏爱长度、位置或同家族风格。
task: 界定自动评价能承担什么角色。
approach: 交换候选顺序、控制内容差异，并用 independent human evaluation 做 judge calibration。
result: 按 evaluation slice 一致性支持使用，执行真值不被替代。
---

## 可以这样回答

我会把 judge 先当一个需要做 calibration 的评审器。它可能很擅长快速检查普通回答，但在长度、顺序或者熟悉的文风上偏掉。

我会抽一批题给人标，再让 judge 评同一批候选。交换顺序，看结论会不会变；挑一些长而错、短而对的例子，看它有没有被表达方式带走。数学、代码和工具状态能直接检查的部分，我会保留执行检查。

对得比较稳定以后，可以用它加快开发迭代。重要发布结论仍需要独立证据，特别是换了模型或任务以后，要重新看它还准不准。
