---
id: afm-mock-debug-reward
kind: guide
situation: 奖励和胜率提高却不代表工具成功。
task: 区分生成、排序和评价的错误。
approach: 扫描 N 并审计顺序、长度与 model-family bias。
result: 独立执行支持改进，示意数据不作总体推断。
---

## 可以这样回答

奖励和胜率提高却不代表工具成功。

将候选生成、奖励排序、judge 测量和任务真值拆开检查。扫描 best-of-N、交换位置、核对高分错例，再决定修 RM 数据、评测协议还是生成策略。
