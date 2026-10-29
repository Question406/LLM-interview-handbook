---
id: amazon-nova
section: amazon
order: 11
level: A
title: Amazon：Nova / Titan 当 Bedrock 模型族，怎么评、怎么路由？
quick: >-
  生成侧按能力和延迟选择 Nova Micro / Lite / Pro / Premier，检索嵌入侧单独评 Titan。Bedrock
  智能提示路由只在同族内预测质量差，小模型不够时 fallback。换档仍用原应用评测集，并单独报告后悔率、升级率和 p99。
tags:
  - Amazon
  - Nova
  - Titan
  - Bedrock
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Amazon Nova
    url: 'https://aws.amazon.com/ai/generative-ai/nova/'
    type: primary
  - title: Intelligent prompt routing in Amazon Bedrock
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html'
    type: primary
  - title: >-
      Use Amazon Bedrock Intelligent Prompt Routing for cost and latency
      benefits
    url: >-
      https://aws.amazon.com/blogs/machine-learning/use-amazon-bedrock-intelligent-prompt-routing-for-cost-and-latency-benefits/
    type: primary
  - title: Customize Amazon Nova models with Amazon Bedrock fine-tuning
    url: >-
      https://aws.amazon.com/blogs/machine-learning/customize-amazon-nova-models-with-amazon-bedrock-fine-tuning/
    type: primary
---

## 可以这样回答

先把生成和嵌入分开选，再考虑路由。Titan 是 Amazon 较早的托管 FM，覆盖文本、嵌入和图像；Nova 是后续生成模型族，按能力、延迟和价位分档。例如简单 FAQ 可以用小模型，长政策对照或多跳工具任务再考虑大模型，不能用一张混合排行榜同时决定聊天与检索模型。

生成侧，Nova Micro 是低延迟文本模型，Lite 偏低成本多模态，Pro 折中质量和速度，Premier 提供更强能力，也常用作 distillation 教师。输入模态、SFT / RFT 支持范围以用户指南为准。检索与 RAG 可用 Titan Text Embeddings V2，评价看 MTEB 的检索部分和领域数据，见 `amazon-titan-embed`。聊天 Arena 分数不适合给 embedding 发版。

## 技术备查

先把生成和嵌入分开选，再考虑路由。Titan 是 Amazon 较早的托管 FM，覆盖文本、嵌入和图像；Nova 是后续生成模型族，按能力、延迟和价位分档。例如简单 FAQ 可以用小模型，长政策对照或多跳工具任务再考虑大模型，不能用一张混合排行榜同时决定聊天与检索模型。

## 默认档位确定后，再增加路由

生成侧，Nova Micro 是低延迟文本模型，Lite 偏低成本多模态，Pro 折中质量和速度，Premier 提供更强能力，也常用作 distillation 教师。输入模态、SFT / RFT 支持范围以用户指南为准。检索与 RAG 可用 Titan Text Embeddings V2，评价看 MTEB 的检索部分和领域数据，见 `amazon-titan-embed`。聊天 Arena 分数不适合给 embedding 发版。

旧 Titan 文本生成端点要按客户依赖管理，新应用默认考虑 Nova 族；嵌入索引有独立生命周期。换 embedding 必须全库重编，见 `amazon-bedrock-rag`。

Bedrock Intelligent Prompt Routing 在同族内工作，例如 Nova Lite ↔ Pro，Claude Haiku ↔ Sonnet。它预测小模型相对大模型的质量差，超过设定阈值就 fallback。公开博客用 ARQGC 描述相对随机路由的质量与成本。Nova、Claude、Llama 跨族选择则需要自建业务路由器和应用评测，不能直接比较三家的 MMLU 差值。

## 路由也要单独验收

换 Nova 档位或打开路由时，应用评测集保持不动。沿用 `amazon-titan-eval` 的检索、证据支持、任务和系统四层，系统包括 TTFT 和端到端 p99，见 `amazon-p99-stream`。

额外记录后悔率：路由到小模型的请求中，用大模型或人复核，小模型明显更差的比例。再看升级率，也就是多少请求最后打到 Pro / Premier；如果始终 100% 升级，成本并没有省下来。两项都按短分类、抽槽、简单 FAQ、多跳工具、长政策对照切片，思路与 `amazon-kendra-hybrid` 的 query 切片相同。

安全策略在换档后仍对输入和输出生效，见 `amazon-guardrails`。小模型价格低并不说明更安全。延迟也按最终模型分别报分位数，小模型与大模型的混合分布可能拉长 p99。只靠 prompt 长度路由会漏掉短而难的问题，也会把长模板误判为难题。

公开材料中 Premier 可作教师，Micro / Lite / Pro 可做 SFT，训练和评测仍需隔离。Seller 政策助手的金标是条款 id，允许不同的正确措辞。Titan 的 MTEB 与 Nova 的 Arena 分分别解释对应能力，不能拼成「Amazon 最强模型」一条分数。

具体落地先定任务与 SLO，再选默认档位，最后用路由优化成本。知识库、工具和护栏由应用管理，换 Titan Text 到 Nova 时保持契约。成本用 token 用量和升级率衡量；离线可全用 Pro 测上限，线上再用后悔率确认路由仍达标。训练是否使用 Trainium 只讲公开材料，栈差异见 `amazon-trainium`。

## 追问

**为什么不全用 Premier？**
受时延和配额约束，许多抽取与分类流量用 Micro 就能完成。Highest Standards 要求任务正确。

**路由错了怎么发现？**
用影子流量异步把同一请求发给 fallback，比较质量差。线上预注册改写率、升级工单和 Guardrail 干预指标。

**Titan 还需要保留吗？**
生成侧看旧 model id 的客户依赖，嵌入侧 V2 仍是 RAG 路径之一，分别管理。

**什么时候自建路由器？**
需要 marketplace、ASIN、工具需求等业务特征时可以自建。Bedrock 的同族路由更省维护，两者都用同一应用集验收。
