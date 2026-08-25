---
id: amazon-nova
section: amazon
order: 11
level: A
title: Amazon：Nova / Titan 当 Bedrock 模型族，怎么评、怎么路由？
quick: >-
  Titan 是早一代 Amazon FM（文本、嵌入、图像）；Nova 是新一代生成族（Micro / Lite / Pro /
  Premier）。路由只在同一族里用智能提示路由，用质量差阈值决定走小模型还是 fallback。评的是应用契约加路由后悔率，不是把
  MMLU 当上线门禁。嵌入仍常走 Titan，不要和聊天模型混成一个排行榜。
tags:
  - Amazon
  - Nova
  - Titan
  - Bedrock
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Amazon Nova
    url: https://aws.amazon.com/ai/generative-ai/nova/
    type: primary
  - title: Intelligent prompt routing in Amazon Bedrock
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html
    type: primary
  - title: Use Amazon Bedrock Intelligent Prompt Routing for cost and latency benefits
    url: https://aws.amazon.com/blogs/machine-learning/use-amazon-bedrock-intelligent-prompt-routing-for-cost-and-latency-benefits/
    type: primary
  - title: Customize Amazon Nova models with Amazon Bedrock fine-tuning
    url: https://aws.amazon.com/blogs/machine-learning/customize-amazon-nova-models-with-amazon-bedrock-fine-tuning/
    type: primary
---

Bedrock 应用岗和 AGI org 都会把「用哪颗 Amazon 模型」问成系统设计。公开叙事：Titan 是 Amazon 第一代托管 FM；Nova 是后续生成模型族，按能力 / 时延 / 价位分档。Intelligent Prompt Routing 文档写明：在 **同一模型族** 里预测质量，再决定走小的还是 fallback 大的。不是某次逐字真题。应用评测底座见 `amazon-titan-eval`——本题补族内路由和换代，不把 BLEU 再讲一遍。

## 族怎么切，别把 Titan 和 Nova 焊成一个模型

我会先在白板上分两行：

- **生成。** Nova Micro（低时延文本）、Lite（便宜多模态）、Pro（质量 / 速度折中）、Premier（最强，也常当蒸馏教师）。输入模态和是否支持 SFT / RFT 以当时用户指南为准，面试要说「以文档为准」，不要背死一张过期表。
- **嵌入。** 检索和 RAG 仍大量用 Titan Text Embeddings V2（可变维、长上下文）。这是另一条模型卡，评 MTEB / 领域检索，见 `amazon-titan-embed`。不要用聊天 Arena 分数给 embedding 发版。

Titan 文本生成还在账上出现时，把它当遗留端点：新应用默认 Nova 族，旧索引别偷偷换 embedding。换 embedding = 全库重编，见 `amazon-bedrock-rag`。

路由：Bedrock 的智能提示路由在族内工作，例如 Nova Lite ↔ Pro，或 Claude Haiku ↔ Sonnet。路由器预测「这笔请求用小模型会不会差太多」；差过你设的质量阈值，就走 fallback。公开博客用 ARQGC 这类指标描述「相对随机路由的质量 / 成本」。跨族硬拼（Nova vs Claude vs Llama）不是这个功能；那是你自己的业务路由器，要用应用评测集，不能把三个厂的 MMLU 相减。

## 评测：底座不动，路由单独成一张表

换 Nova 档位或打开路由时，**应用评测集不要跟着改**。否则你分不清是模型好了还是题换了。门禁沿用 `amazon-titan-eval` 四层：检索、接地、任务、系统（TTFT / E2E p99，见 `amazon-p99-stream`）。在此之上加路由层：

- **后悔率。** 路由到小模型后，用大模型（或人）当裁判，小模型明显更差的比例。这是「省了钱但伤了客户」的直接量。
- **升级率。** 多少请求实际打到 Pro / Premier。一直 100% 打大模型，路由器等于没干活。
- **切片。** 短分类、抽槽、简单 FAQ 应走 Micro / Lite；多跳工具、长政策对照走 Pro / Premier。切片和 `amazon-kendra-hybrid` 的标识符 vs 语义是同一思想：简单查询不要浪费大模型。
- **安全。** Guardrails 挂在路由之后仍要对输入 / 输出都跑，见 `amazon-guardrails`。小模型不是更安全，只是更便宜。

蒸馏 / 微调：公开材料里 Premier 可当教师，Micro / Lite / Pro 可 SFT。评测集要和训练隔离。Seller 政策助手这种，金标仍是条款 id，不是金句。

错法：把 Titan Embeddings 的 MTEB 分和 Nova Pro 的 Arena 分画在一张图上「选 Amazon 最强模型」。另一错法：路由用 prompt 长度当唯一特征——短问题也可以很难，长 prompt 也可以是粘贴的模板。第三：开了路由就不报 p99。小模型快、大模型慢，混合分布会把尾巴拉开，必须按落地模型分位报。

## 我会怎么收设计题

先钉任务和 SLO，再选默认档位，最后才加路由器。路由器是优化，不是架构。知识库、工具、护栏绑在应用上，不绑死某一个 model id，方便把 Titan Text 换成 Nova 而不改契约。成本用 token 用量和升级率讲，不要报美元价签。离线评测可以全打 Pro 当上限，线上再开路由，用后悔率证明没掉出契约。训练这些模型是不是 Trainium，公开层不要编，栈差异见 `amazon-trainium`。

## 追问

- **为什么不全部上 Premier？** 时延和配额。大量可抽取 / 可分类流量用 Micro，Insist on the Highest Standards 指任务正确，不是每张工单都用最大模型。
- **路由错了怎么发现？** 影子：同一请求异步打 fallback，比质量差；线上用改写率、升级工单、Guardrail 干预。预注册，不要上线后才找指标。
- **Titan 还要不要？** 生成侧看是否仍有客户绑旧 model id；嵌入侧 V2 仍是 RAG 主路径之一。两套生命周期分开。
- **和自建分类器路由？** 可以。Bedrock 路由省事、同族；自建可以吃业务特征（marketplace、是否含 ASIN、是否要工具）。两者都要用同一应用评测集验收。
