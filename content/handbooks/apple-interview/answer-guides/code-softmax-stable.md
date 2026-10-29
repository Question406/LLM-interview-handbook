---
id: code-softmax-stable
kind: coding
situation: 大 logit 或全 mask 行会产生数值问题。
task: 实现稳定且 edge-case behavior 明确的 softmax。
approach: 先减最大值，再单独处理无有效元素的行。
result: 与参考分布对比，检查极值和全 mask 不出 NaN。
---

## 可以这样回答

大 logit 或全 mask 行会产生数值问题。

沿计算轴先减最大值再 $\exp$ 和 normalization，分布不变，指数落在 $(0,1]$ 不会上溢。整行都被 mask 成 $-\infty$ 时会出 NaN，要把这一行的概率置 0。

测试还要满足这个条件：与参考分布对比，检查极值和全 mask 不出 NaN。
