---
{
  "id": "afm-web-synthetic-loop",
  "section": "synthetic",
  "order": 708,
  "level": "S",
  "title": "Synthetic Data：只有几百条 seed，怎样生成并筛出有用的训练样本？",
  "quick": "先按任务家族隔离真实评估，再做 generation、verification、deduplication 和训练对照。 在独立真实任务上优于等预算 baseline，且 long-tail 不退化。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "synthetic"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "Sahi Padhai — Training Data and Synthetic Data",
      "url": "https://sahipadhai.cc/course/ai-engineer-interview/training-data-and-synthetic-data",
      "type": "reference"
    }
  ]
}
---

## 来源与范围

参考 [Sahi Padhai — Training Data and Synthetic Data](https://sahipadhai.cc/course/ai-engineer-interview/training-data-and-synthetic-data) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
给定几百条经过审核的 seed，设计 teacher-driven synthetic data pipeline，并说明如何用于下一轮 self-improvement。来源章节包含生成、过滤和真实 held-out evaluation；tool-use 场景是手册扩展。

## 技术备查
保存 seed family、generator、prompt、sampling、环境及 verifier 版本。按来源家族切分后再生成，不能生成完只做随机行切分。

质量 funnel：生成候选 → 合法任务 → 可执行 → 终局正确 → 过程合格 → 去近重复 → data mix。分别记录各层 retention，并审核被过滤的 rare task types。

## 面试追问
**Teacher 错了但 verifier 没发现？** 对 verifier 做 adversarial tests 和人工抽样，加入独立检查；不得把自动通过等同形式化正确。

**下一轮只生成模型失败题吗？** 失败任务有价值，但应保留代表性任务和 regression coverage，避免 curriculum 变成少数噪声样本的重复放大。
