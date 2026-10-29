---
{
  "id": "afm-web-video-feedback",
  "section": "systems",
  "order": 711,
  "level": "S",
  "title": "Recommendation Flywheel：观看行为怎样变成标签，又怎样避免 feedback bias？",
  "quick": "记录 exposure 与上下文，分离显式反馈和行为代理，用独立实验验证变化。 体验与覆盖改善，而不是只强化已有热门内容。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "systems"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "Hello Interview — Video Recommendations",
      "url": "https://www.hellointerview.com/learn/ml-system-design/problem-breakdowns/video-recommendations",
      "type": "reference"
    }
  ]
}
---

## 来源与范围

参考 [Hello Interview — Video Recommendations](https://www.hellointerview.com/learn/ml-system-design/problem-breakdowns/video-recommendations) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
为 video recommendation 设计 data feedback loop，并解释 exposure bias。然后说明哪些原则可迁移到 foundation-model data flywheel，哪些不能。来源有完整 system-design worked example；AFM 迁移部分为手册扩展。

## 技术备查
把 impression、position、interaction 和 outcome 关联。Negative sampling 必须区分已曝光未选择和根本未曝光；watch completion 还受视频长度影响。Offline ranking metrics 和 online experiment 解决不同问题。

可用适当的探索或 propensity-aware 方法研究 exposure bias，但需要已知或可估计的展示概率、support 与方差控制，不能把 reweighting 当作无条件修复。

## 面试追问
**只训练成功 interactions 可以吗？** 容易丢失失败和未满足需求，强化已有 policy 的选择。保留完整曝光与失败证据，再决定训练视图。

**AFM 的同类问题是什么？** 只收集模型愿意回答、用户愿意评价的 prompts，会遗漏 over-refusal 或放弃交互的用户；需要主动构造 evaluation 和有针对性的采集。
