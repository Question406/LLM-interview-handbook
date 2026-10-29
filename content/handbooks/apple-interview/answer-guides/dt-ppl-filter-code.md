---
id: dt-ppl-filter-code
kind: coding
situation: perplexity 的正常范围随语言和领域改变。
task: 用可进行 calibration 的分数筛明显异常文本。
approach: 按分组设阈值并抽查，不全局只留低 ppl。
result: 比较误删和下游覆盖，保留有用难文本。
---

## 可以这样回答

perplexity 的正常范围随语言和领域改变。

用小语言模型算文档的平均 cross-entropy 或 perplexity，可以当质量的间接信号，但它只说明文本像不像参考 corpus。阈值要按语言和数据域取分位数，代码、公式和论坛要各设阈值，维基的阈值套不上。synthetic data 要用独立 verifier，筛得好不好靠下游对照判断。

测试时，我会比较误删和下游覆盖，保留有用难文本。
