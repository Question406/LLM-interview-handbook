---
id: amazon-bedrock-rag
section: amazon
order: 1
level: A
title: Amazon：Seller Support 上 500 万份政策 PDF，p95 2 秒的 RAG 怎么做？
quick: "500 万政策 PDF 的 RAG，我会先按条款和表格切块，再用市场、类目和生效日期过滤检索。日更文档靠元数据明确作废旧版本，生成逐句带引用；p95 2 秒则分别给检索、生成和安全检查留预算。"
tags:
  - Amazon
  - Bedrock
  - RAG
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Amazon AI Engineer Interview Guide (2026)
    url: https://www.datainterview.com/blog/amazon-ai-engineer-interview
    type: secondary
  - title: Amazon AI Engineer Interview Questions (public compilation)
    url: https://github.com/ombharatiya/AI-Engineer-Interview-Questions/blob/main/14-company-interview-questions/amazon.md
    type: secondary
---

我会先保证检索到的是当前市场下有效的条款，再把检索和生成拆开控制延迟。公开整理中的条件是 S3 上约 500 万份政策 PDF、每天更新、p95 低于 2 秒。比如「仅适用于危险品」若在切块时丢了，后面即使向量很相似，回答也会把适用范围说错。

## 切块和索引

先按标题和条款边界切，表格尽量整表保留，再对块做 embedding。每块记录 marketplace、商品类目、语言、生效日期、作废日期和源 URI，后面才能检查适用范围与版本。

500 万文档不是 500 万块。一块文档可能 10–50 块，索引是千万级。OpenSearch Serverless / 自建向量库都可以，检索时在 ANN 前过滤或用 hybrid，先按 metadata 缩小范围再做向量匹配。只靠余弦、把 marketplace 混在一起，会检出别国政策。

日更：增量解析新 PDF，按文档 id 删除旧块再写入。向量不会「过期」，必须用元数据作废。当天生效的条款，索引延迟要有 SLO，比如 15 分钟内可检索，并在回答里展示文档时间戳。

## p95 2 秒怎么拆

预算示例：检索 300–500ms，生成 1.2s，余量给重试和安全过滤。生成侧用小模型或 Bedrock 低延迟档，提示只塞 top-k 短块，不要塞整份 PDF。p95 还要测队列和冷启动带来的尾延迟，平均值不足以证明达标。

生成时每个句子对齐到块 id，对不上就删句或说明「政策里没写」。错误政策可能影响 Seller 账号状态，不能为了赶延迟补一个没有证据的结论。这与 `apple-siri-grounded` 的证据约束相似，输入输出通道换成了客服工单。

离线用标注的（问题，条款金标）测 recall@k 和 grounded 准确率；线上看客服改写率和政策升级工单。A/B 中一旦引用了已作废条款，就单独作为事故检查。

## 追问

**为什么不只上 Bedrock Knowledge Bases 默认配置？**
默认切块和同步节奏很可能保不住表格和 15 分钟生效。托管服务是底座，条款结构和元数据是你的责任。
**多语言？**
嵌入模型和检索语言要对齐；也可以按 marketplace 分索引。混在一个英文索引里会漏。
**和 AGI org 的差别？**
Bedrock 岗偏平台和 SLO；AGI / Nova 岗会把同一场景转成训练数据和偏好。同一题，答的深度不同。

## 相关题

- [[design-chat-tools]]：同样是政策检索带引用，但那张是带工具的客服聊天，多了改订单的确认、工单状态机和升级人工。
