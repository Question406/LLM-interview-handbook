---
{
  "id": "afm-web-apple-project-deepdive",
  "kind": "project",
  "situation": "面试官围绕同一个 AI 项目连续追问，泛泛介绍无法支持技术判断。",
  "task": "用真实职责连接 data gap、模型选择、评估证据和上线条件。",
  "approach": "选一个本人能解释的项目，明确已做部分、公开结果与拟议扩展。",
  "result": "回答能经得住追问，缺少线上结果时不虚构发布经历。"
}
---

## 可以这样回答

我会选一个我能解释失败样本和个人贡献的项目，而不是只挑名称最像 AFM 的项目。开场先说具体任务、原有方法的不足，以及我实际负责哪一部分。

对于 data challenges，我会拿一个真实 failure case 说明问题：它为什么发生，我们凭什么认为是数据覆盖或标签问题，而不是模型或 evaluation 的错误。然后再讲我实际做过的处理，以及没有尝试过的替代方案。

Model choice 需要对应约束，比如算力、latency、输入形式和 baseline。评估则说明 split、主要指标、关键 slices 和失败分析。如果项目只做了 research evaluation，我就明确说没有生产上线，不把 benchmark 结果说成用户收益。

如果被问到 production readiness，我会补充“如果产品化，我会怎样验证”：包括独立任务集、真实环境兼容性、privacy review、监控和 rollback。这些是后续设计，而不是已经完成的履历。
