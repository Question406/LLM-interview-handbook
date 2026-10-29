---
id: dt-llama-extract
kind: concept
situation: 行级重复既有模板也有有用内容。
task: 避免抽取与 deduplication 误伤好文本。
approach: 按 URL、文档、行分别审计，保留结构。
result: 数据类型 evaluation slices 支持阈值，不照搬论文参数。
---

## 可以这样回答

行级重复既有模板也有有用内容。

最容易 false rejection 好文本的是行级 deduplication：它删掉导航这类重复模板，也会删掉反复出现的好句，所以要按内容类型抽查。URL 级保留最新版本，文档级 near-duplicates 的范围用下游实验选；抽取阶段数学、代码和 multilingual 分开处理，保留数学和代码结构以及图片 alt 文本。「每 30M 篇中超过 6 次」是 Llama 自己的阈值，换数据要重新验证。
