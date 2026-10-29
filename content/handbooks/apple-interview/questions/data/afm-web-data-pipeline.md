---
{
  "id": "afm-web-data-pipeline",
  "section": "data",
  "order": 702,
  "level": "S",
  "title": "Data Pipeline：怎样从杂乱语料构建可追溯、可扩展的训练数据？",
  "quick": "先建立可追溯的小规模流程，再以稳定 record ID 扩展处理。 能复现 data mix，并证明质量收益不是仅来自更多训练 tokens。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "data"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "Exponent / Aced — Designing a Data Processing Pipeline",
      "url": "https://www.tryexponent.com/courses/ml-system-design/mlsd-data-pipeline",
      "type": "reference"
    }
  ]
}
---

## 来源与范围

参考 [Exponent / Aced — Designing a Data Processing Pipeline](https://www.tryexponent.com/courses/ml-system-design/mlsd-data-pipeline) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
设计从新获取的技术文档到训练 manifest 的 data pipeline。讨论质量、规模、重试、lineage 和收益验证。来源是面试课程；技术文档场景是手册扩展。

## 技术备查
处理顺序需要根据成本与数据类型调整。先做便宜的格式及权限检查，再对保留数据做较昂贵的语义质量打分。Immutable raw、规范化 record 和 training manifest 分开保存；manifest 记录内容 hash、处理版本、过滤原因和 split。

Cross-document deduplication 要定义单位：精确重复、近重复段落与同任务改写可能需要不 on-policy。Evaluation decontamination 不能只查最终 SFT，其他训练阶段也需要检查。

## 面试追问
**过滤越严格越好吗？** 不一定。抽查 rejected pool，并按语言、来源、格式比较 retention 与质量，防止丢掉有价值的 long-tail。

**如何支持删除请求？** 用 provenance 查找所有派生记录并停止后续使用；已有模型是否需要额外处置，应结合具体治理要求评估，不能声称从 manifest 删除就等于模型遗忘。
