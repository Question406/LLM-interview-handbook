---
{
  "id": "afm-web-dpo-beta",
  "section": "alignment",
  "order": 704,
  "level": "S",
  "title": "DPO：β 控制什么，为什么不能只用“大或小”解释训练行为？",
  "quick": "先看相对 log-prob margin，再区分理论 regularization 与实际 gradient scale。 能给出检查 KL、preference 和任务质量的 tuning 实验。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "alignment"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "OpenSkill — Preference Alignment: RLHF, DPO & GRPO",
      "url": "https://app.openskill.ai/interviews/llm.preference-alignment-and-rlhf",
      "type": "reference"
    },
    {
      "title": "Direct Preference Optimization",
      "url": "https://arxiv.org/abs/2305.18290",
      "type": "primary"
    }
  ]
}
---

## 来源与范围

参考 [OpenSkill — Preference Alignment: RLHF, DPO & GRPO](https://app.openskill.ai/interviews/llm.preference-alignment-and-rlhf) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
解释 DPO 的 β、reference policy 与相对 margin；讨论极小或极大 β，以及如何用实验选择。来源页面公开了 β 的样题，下面的推导与实验是手册参考答案。

## 技术备查
定义
$$\Delta=\log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)}-\log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}.$$
DPO loss 为 $-\log\sigma(\beta\Delta)$，对 $\Delta$ 的导数为 $-\beta\sigma(-\beta\Delta)$。当 $\Delta=0$ 时是 $-\beta/2$。这是局部 gradient 分析，不代表最终模型的 KL 单调关系。

## 面试追问
**DPO 是否完全不需要 reward？** 通常不需要显式训练和运行一个 reward model，但依然依赖可信 preference signal，并隐含 reward 参数化。

**DPO 与 PPO 怎么选？** 当已有可靠离线 pairs、追求训练简洁时可先试 DPO；有可交互环境且希望持续采集当前 policy 数据时，可考虑 online RL。选择仍取决于 verifier、成本、稳定性与目标，而不是固定赢家。
