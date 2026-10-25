---
id: msft-azure-tpm
section: microsoft
order: 5
level: A
title: Microsoft：Azure OpenAI TPM/RPM 限流，产品层排队和降级
quick: "TPM 限制输入与输出 token，RPM 限制请求数，短时间尖峰也可能触发 429。调用方按真实 token 需求做租户准入与有界队列，尊重 Retry-After，再按约定缩上下文、换小模型或返回检索摘录。稳定基线可考虑 PTU，突发仍需降级。"
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

先判断请求撞的是 TPM 还是 RPM，再做有界排队、退避和降级。短 prompt 高 QPS 通常先撞请求数，长文档即使请求少也可能撞 token 配额；429 表示容量准入受限，调整 temperature 解决不了这个问题。

## 配额如何分配与计数

Azure 文档按订阅、region 和模型提供配额，再把 TPM 分给 deployment。RPM 通常按模型容量单元比例跟着 TPM 分配，两者不能独立调；老聊天模型常见每 1000 TPM 约 6 RPM，推理模型比例不同。服务还按 1 秒或 10 秒短窗检查，整分钟平均不超也可能在尖峰返回 429。

TPM 包含 prompt + completion，流式也照常占用。全仓库输入同时放大费用和配额压力，见 `msft-copilot-ground`、`msft-long-context`。

Standard 用共享池，可能动态收紧，按 `Retry-After` / `retry-after-ms` 退避，重试要有上限。Provisioned（PTU）提供预留容量，打满也会限制，文档建议按 header 等待；溢出到 Standard 是需显式设计的 spillover。预留也受超长 prompt、低缓存命中等 workload shape 影响。

## 网关把排队和降级统一起来

按租户 / 用户使用令牌桶，大小对齐部署 TPM，超额进入有界队列。比如最长等待 2 秒，同时限制深度，队列满就返回可重试失败。交互聊天优先于批量 embedding，批量走离峰或独立部署。让客户端无穷 `while True: retry` 会形成惊群，加剧 429。

重复问题可缓存，语义缓存要遵守 Copilot ACL。系统提示和检索块用前缀缓存；分类、正则或小模型能做的就减少 4o 调用，Phi / mini 可承担这类任务，见 `msft-phi-slm`。

降级提前写进产品约定：先缩上下文或摘要检索结果，再换 mini / 本地区域的小部署；仍不可用时走模板加检索摘录，只显示引用；最后明确告知用量高、预计等待和重试方式。避免静默重试直到超时。

监控拆开 429 率、队列等待 p95、降级率、缓存命中和 prompt/completion TPM，并按 region、模型分组。East US 满额后不能盲目跨区，数据驻留与网络 RTT 都可能限制切换。两个部署各分一半 TPM，也不等于增加了 region+模型总配额。

工作时间等可预测基线适合考虑 PTU，突发与实验用 Standard。质量 A/B 还需标记降级流量并分开分析，否则限流导致的小模型替换会被误解成新 prompt 质量下降。

## 追问

**估算配额用每分钟用户数就够了吗？**
不够。要结合真实请求数与 prompt/completion 长度，分别算 TPM 和 RPM。

**怎样避免重试惊群？**
尊重 `Retry-After`，Standard 配合指数退避与 jitter，统一服务端排队并合并客户端重试；PTU 按服务 header 指示等待。

**可以多部署负载均衡吗？**
可以分配流量，但共享 region+模型总配额，跨区还要检查驻留要求。

相关：[[anthropic-rate-limit]]、[[p3a-xai-rate-limiter-design]]、[[design-chat-serving]]
