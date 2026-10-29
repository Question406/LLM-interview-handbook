---
{
  "id": "afm-web-photos-search",
  "section": "multimodal",
  "order": 710,
  "level": "S",
  "title": "Multimodal Search：私人照片搜索的数据、评估和 model upgrade 怎么设计？",
  "quick": "分开视觉语义与时间人物信息，使用获授权的数据验证，版本化 embedding。 搜索成功改善，同时不跨用户访问且升级期间结果可用。",
  "companies": [
    "apple"
  ],
  "tags": [
    "Apple",
    "AFM 网站参考题",
    "AFM Web References 2026-10-27",
    "multimodal"
  ],
  "realInterview": false,
  "status": "published",
  "format": "markdown",
  "updatedAt": "2026-10-27",
  "sources": [
    {
      "title": "DataInterview — Design Google Photos search",
      "url": "https://www.datainterview.com/courses/google-machine-learning-engineer/photos-search",
      "type": "reference"
    }
  ]
}
---

## 来源与范围

参考 [DataInterview — Design Google Photos search](https://www.datainterview.com/courses/google-machine-learning-engineer/photos-search) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
设计私人照片的自然语言搜索，说明 image-text training、个人上下文、evaluation、privacy 和 embedding migration。来源为课程案例。免费 preview 可见设计重点，完整 walkthrough 与 exercises 需要订阅。

## 技术备查
数据产品包括 image-text pairs、可控布局或场景的 synthetic query-photo relevance、获授权的个人查询集。Synthetic evaluation 适合检验机制，不能独自代表真实用户分布。

按用户或 photo family 隔离评估，检查 image near-duplicates。报告 Recall@K / ranking、无正确结果时的行为、cross-user isolation 和 end-to-end task success。

## 面试追问
**是不是一定要 ANN？** 单用户 corpus 的规模可能允许 exact search。先估算每用户照片量、向量维度、存储位置与 latency，再决定索引。

**模型升级一定要重算全部吗？** 通常需要处理表示兼容性；可先 dual-read、分批 backfill 或研究兼容表示，但必须验证新旧空间，不能直接混用向量。
