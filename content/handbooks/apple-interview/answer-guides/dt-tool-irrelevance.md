---
id: "dt-tool-irrelevance"
kind: "concept"
situation: "总有可用工具的训练会鼓励乱调用。"
task: "学会判断没有合适工具或缺信息。"
approach: "加入语义接近的无关工具与澄清示范。"
result: "相关性判断和真实任务成功同时评。"
---

## 可以这样回答

总有可用工具的训练会鼓励乱调用。

补两类示范：当前工具目录完成不了请求时，正确做法是不调用，说明限制或询问用户；缺少信息时，先调只读查询再执行。SFT 如果总假设有工具可用，模型就学会见 schema 就填，编造名称和参数。BFCL 的 Function Relevance Detection 专门测第一类，负例要用语义相近的无关工具来造。
