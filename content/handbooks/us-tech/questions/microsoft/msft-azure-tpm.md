---
id: msft-azure-tpm
section: microsoft
order: 5
level: A
title: Microsoft：Azure OpenAI TPM/RPM 限流，产品层排队和降级
quick: >-
  TPM 管每分钟 token，RPM 管每分钟请求，429 是配额墙不是模型坏了。产品层要有队列、退避、缓存，以及降到小模型或抽取式答案。别把限流当成「再调一次
  temperature」。
tags:
  - Microsoft
  - Azure OpenAI
  - Rate Limit
  - Product
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Azure OpenAI in Azure AI Foundry Models
    url: https://learn.microsoft.com/en-us/azure/ai-services/openai/
    type: primary
  - title: Azure OpenAI quotas and limits
    url: https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
    type: primary
  - title: Manage Azure OpenAI quota
    url: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/quota
    type: primary
---

Azure / Copilot 产品岗会把限流问成系统设计，不是「429 怎么 retry」。公开文档里配额按 **Tokens-per-Minute（TPM）** 分到每个部署，RPM 按模型比例跟着 TPM 走，不是两个独立旋钮。评委要听：计数口径、排队、降级，以及什么时候该买预留吞吐而不是在应用里死等。

## 先分清 TPM、RPM 和 429

订阅在某一 region、某一模型上有一份配额。创建部署时把 TPM 切给这个 deployment，推理就按这个上限准入。RPM 通常按容量单元成比例（老聊天模型常见大约每 1000 TPM 配 6 RPM，推理模型比例不同，别背死数字）。文档还写：服务会在 **1 秒或 10 秒** 的短窗上看速率，所以即使「这一分钟平均没超」，尖峰仍会 429。

计入 TPM 的是 **prompt + completion**，不是只算输出。把整份仓库塞进上下文，账单和限流一起炸，这和 `msft-copilot-ground`、`msft-long-context` 是同一条预算。流式请求照样占 token，不会因为 chunk 多就另算一套魔法配额。

429 的产品含义：

- **Standard（按量）：** 共享池，可能被动态削；看 `Retry-After` / `retry-after-ms`，指数退避，但退避不是无限队列。
- **Provisioned（PTU）：** 买的是预留容量。打满就是硬顶，文档建议按 header 等满再试，而不是瞎 jitter。溢出可以 spillover 到 Standard，那是明确的降级，不是偷偷多用预留。

错法：把 429 当「模型抽风」去换 prompt。先看是 TPM 还是 RPM：短 prompt 高 QPS 先撞 RPM；长文档摘要先撞 TPM。

## 产品层：排队、削峰、降级，不要让用户直接撞墙

我会在网关做三件事，而不是让每个客户端自己 `while True: retry`。

**排队和准入。** 按租户 / 用户令牌桶，桶的大小对齐部署 TPM，不要对齐「我们希望的 QPS」。超限的请求进有界队列，队列有最大等待（比如 2 秒）和最大深度。队列满了立刻失败并返回可重试信号，比让线程堵在 OpenAI SDK 里要干净。优先级：交互式聊天高于批量嵌入，批量走离峰或单独部署。

**削峰。** 重复问题缓存（语义缓存要小心权限，见 Copilot ACL）。系统提示和检索块能共享就前缀缓存。能抽成分类 / 正则 / 小模型的，不要每条都打 4o。Phi / mini 部署是这条线上的减压阀，见 `msft-phi-slm`。

**降级阶梯，要写进产品合同，不要临场编：**

1. 同模型，缩短上下文（少召回几块、摘要检索结果）。
2. 换更小 / 更便宜的部署（mini、本地区域）。
3. 非生成路径：模板 + 检索摘录，只展示引用，不写长答案。
4. 明确失败：「当前用量高，请稍后」，带预计等待。沉默重试到超时是更差的 UX。

监控要拆：429 率、队列等待 p95、降级触发率、缓存命中、prompt/completion 各自的 TPM。只看平均延迟会把限流尖峰洗掉。配额要按 region 和模型分开报，East US 的 GPT 配额满了，不一定能把流量盲切到另一个区——数据驻留和网络 RTT 都是约束。

PTU 适合基线可预测的生产流量（Copilot 工作时间）；突发和实验走 Standard。面试别说「全部 PTU 就没有 429」——workload shape（超长 prompt、低缓存命中）仍能打满预留。

## 追问

- **TPM 和 RPM 哪个先撞？** 短请求高并发先 RPM；长上下文少请求先 TPM。用真实 prompt/completion 尺寸估，不要用「每分钟用户数 × 1」。
- **为什么重试会让 429 更糟？** 无 jitter 的同步重试会叠成惊群。要尊重 `Retry-After`，客户端合并，服务端排队。
- **多部署负载均衡？** 可以，但配额是 region+模型总和。两个部署各一半 TPM，不是两份配额。跨区要考虑合规。
- **和模型质量 A/B？** 限流降级会污染质量实验。流量标记「是否降级」，分析时拆开，否则你会以为新 prompt 变差了。
