---
id: dt-boilerplate-code
kind: coding
situation: 网页正文混入导航和页脚。
task: 保留信息主体并减少处理成本。
approach: 先用文本/链接密度规则，难域再上复杂抽取。
result: 正文召回和模板残留都要 sampling 检查。
---

## 可以这样回答

网页正文混入导航和页脚。

先用块级的文本密度和链接密度把导航、页脚这类模板块滤掉，这一步最便宜。按域统计抽取失败率，静态抽取失败的域再开 headless 渲染，仍失败才上 LLM 抽取。每页都调 large model 成本高，抽取带来的变化也难追踪；用了 LLM 要记模型版本，抽出的正文照样过质量检查和 evaluation contamination 检查。

测试还要满足这个条件：正文召回和模板残留都要 sampling 检查。
