---
id: dt-rejection-sample-code
kind: coding
situation: 多个候选中只有部分可靠。
task: 按题目定义筛出合格样本。
approach: 逐候选运行 verifier，明确数量和无通过结果。
result: 检查顺序、上限、全部失败与验证成本。
---

## 可以这样回答

多个候选中只有部分可靠。

同一道题采 $k$ 条回答，用独立 oracle 判对错，只留对的；生成器和 verifier 要分开。代码要处理全错、全对和过程假三种情况。$k$ 由当前 pass@$1$ 决定；没有 oracle 就别写 `if judge(y): keep`。

测试时，我会检查顺序、上限、全部失败与验证成本。
