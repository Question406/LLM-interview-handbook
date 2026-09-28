---
id: amazon-bedrock-rag
section: amazon
order: 1
level: A
title: Amazon：Seller Support 上 500 万份政策 PDF，p95 2 秒的 RAG 怎么做？
quick: >-
  先定索引和更新：文档日更，切块要保住表格和条款结构。检索用向量 + 过滤（市场、类目、生效日期）。生成必须带引用。p95
  拆成检索和生成两段预算；过期条款用元数据作废，不要等向量近似消失。
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

公开整理里这道题以 Bedrock Knowledge Bases + Seller Support 的形式出现：S3 上约 500 万 PDF，p95 低于 2 秒，政策每天更新，还要避免过期条款。和 AWS / AGI 应用岗的口味一致。按 Leadership Principles 收：要有指标、所有权、失败模式，不要只画一个向量库。

## 切块和索引

政策 PDF 有表、有条款编号。按固定 token 切会把「仅适用于危险品」切丢。先按标题 / 条款边界切，表格尽量整表进一块，再在块上做 embedding。元数据：marketplace、商品类目、语言、生效日期、作废日期、源 URI。

500 万文档不是 500 万块。一块文档可能 10–50 块，索引是千万级。OpenSearch Serverless / 自建向量库都可以，面试要说：**过滤在 ANN 之前或用 hybrid**（先 metadata 缩小再向量）。只靠余弦、把 marketplace 混在一起，会检出别国政策。

日更：增量解析新 PDF，按文档 id 删除旧块再写入。向量不会「过期」，必须用元数据作废。当天生效的条款，索引延迟要有 SLO，比如 15 分钟内可检索，并在回答里展示文档时间戳。

## p95 2 秒怎么拆

预算示例：检索 300–500ms，生成 1.2s，余量给重试和安全过滤。生成侧用小模型或 Bedrock 低延迟档，提示只塞 top-k 短块，不要塞整份 PDF。p95 是尾部，要看队列和冷启动，而不是平均值。

引用：每个句子对齐到块 id。对不上就删句或改口「政策里没写」。幻觉比慢更贵，Seller 账号会被停。这和 `apple-siri-grounded` 同一类契约，只是通道是工单不是语音。

评测：离线用标注的（问题，条款金标）算 recall@k 和 grounded 准确率；线上用客服改写率和政策升级工单。A/B 时旧条款被引用就算事故，不是「相关性还行」。

## 追问

- **为什么不只上 Bedrock Knowledge Bases 默认配置？** 默认切块和同步节奏很可能保不住表格和 15 分钟生效。托管服务是底座，条款结构和元数据是你的责任。
- **多语言？** 嵌入模型和检索语言要对齐；也可以按 marketplace 分索引。混在一个英文索引里会漏。
- **和 AGI org 的差别？** Bedrock 岗偏平台和 SLO；AGI / Nova 岗会把同一场景转成训练数据和偏好。同一题，答的深度不同。
