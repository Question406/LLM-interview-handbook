---
id: dt-tinker-agent-rl
kind: design
situation: 训练代码接口体现数据与环境契约。
task: 把公开 cookbook 解释成可运行流程。
approach: 跟踪 rollout、奖励、版本与 update schedule。
result: 复现接口语义，明确离线数据与在线 sampling 区别。
---

## 可以这样回答

训练代码接口体现数据与环境契约。

合同是可安装的 Env 加可复现的奖励：Env 走 reset / step 接口，同一道题起一组环境，组内算 GRPO 优势。有测试的 Harbor 任务以测试结果为奖励，没有测试的文档任务先看状态 diff、再按 rubric 逐条评分。解析失败、工具次数上限和清理规则都写进合同，LLM 法官只评测试覆盖不到的项。
