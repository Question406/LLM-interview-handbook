---
id: dt-length-hack-data
kind: concept
situation: RM 可能把详细误当成正确。
task: 补能区分质量和冗长的数据。
approach: 加入短而正确、长而必要与长而错误的对照。
result: 独立内容评价提高，不能只让答案变短。
---

## 可以这样回答

RM 可能把详细误当成正确。

问题出在 preference data 里长回答总是赢，只调优化参数压不住。数据侧构造信息相同、长度不同的回答对，协议写明同等忠实且完整时选短的；human evaluation 和 RM 结果按长度分层分析，BoN 候选中保留简短的 SFT 回答。平均长度增加不代表能力提高。
