---
{
  "id": "afm-web-data-pipeline",
  "kind": "design",
  "situation": "新增数据量很大，但低质量、重复与 contamination 可能抵消收益。",
  "task": "把数据来源、质量判断和训练版本连接起来。",
  "approach": "先建立可追溯的小规模流程，再以稳定 record ID 扩展处理。",
  "result": "能复现 data mix，并证明质量收益不是仅来自更多训练 tokens。"
}
---

## 可以这样回答

我会先问这批数据要补什么能力。如果目标是 tool use，普通网页文本再多也未必解决参数选择问题，所以我不会一开始就把问题理解成 throughput 优化。

以新增技术文档为例，我会保留原始文件、来源许可和版本，然后依次做解析、敏感信息处理、质量检查、deduplication 和 evaluation contamination 检查。每层都保存拒绝原因，并抽查被拒绝的数据，防止过滤器把少数语言或特殊格式一起删掉。

规模变大以后，我会用稳定 record ID 和版本化 manifest 分配工作，让 worker 重试不会重复加入样本。训练读取冻结的 manifest，而不是随时变化的目录；这样发现坏数据时，能找到受影响的数据版本和 checkpoints。

最后，我会固定训练预算比较旧 data mix 和新 data mix，检查目标能力与 regression tasks。清洗后保留了多少数据只是过程指标，独立评估是否变好才决定这条 pipeline 有没有价值。
