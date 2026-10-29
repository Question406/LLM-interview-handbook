---
{
  "id": "afm-web-agent-evals",
  "section": "evaluation",
  "order": 701,
  "level": "S",
  "title": "Agent Evaluation：客服 agent 上线前后怎样评估，并把失败转成训练信号？",
  "quick": "先验证真实终局，再按失败原因构造数据，避免把满意度直接当正确性。 独立任务成功率提高，重复投诉和越权操作不增加。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "evaluation"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "Exponent / Aced — Agent evaluation question",
      "url": "https://www.tryexponent.com/questions/6610/evals-ai-customer-support",
      "type": "reference"
    }
  ]
}
---

## 来源与范围

参考 [Exponent / Aced — Agent evaluation question](https://www.tryexponent.com/questions/6610/evals-ai-customer-support) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
设计一个能查询订单、发起退款或转人工的客服 agent 的 evaluation framework。说明 offline evaluation、上线监控、失败分类和 training data feedback loop。任务与权限是手册练习约定；来源题只要求设计上线前后的评估。

## 技术备查
- Evaluation unit 是完整工单或任务，不是单条消息；同一客户的重复联系需要关联，避免成功率重复计数。
- 保存 task family、环境版本、policy checkpoint、tool result 与终局核验。权限、安全和业务正确性分别判定。
- 按任务家族划分 development 和 held-out sets。用于调参的线上失败不能继续作为最终 blind evaluation。
- 数据干预例子：固定模型和 token budget，只增加退款参数纠错样本，对照普通 replay 数据；同时测 tool accuracy、终局成功、escalation 和 latency。

## 面试追问
**满意度与正确性冲突时怎么办？** 保留为两个维度。错误退款也可能获得好评，满意度不能覆盖独立的业务状态与权限检查。

**把所有失败直接做 preference pairs 可以吗？** 不可以。需要同任务同初态、可比候选以及可信标签；环境故障先隔离。
