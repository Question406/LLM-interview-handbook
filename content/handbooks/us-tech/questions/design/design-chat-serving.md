---
id: design-chat-serving
section: design
order: 11
level: S
title: 设计：ChatGPT 类对话服务（排队、优先级、前缀缓存、限流）
quick: >-
  我会先定交互 p95 首 token 延迟、容量和公平性目标，再按优先级排队，用 continuous batching 提高 GPU
  throughput。稳定系统提示和会话历史通过前缀 KV 复用，入口按用户和 token 桶限流，KV 水位过高时拒绝或降级。
tags:
  - OpenAI
  - NVIDIA
  - vLLM
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: >-
      Efficient Memory Management for Large Language Model Serving with
      PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
  - title: >-
      Orca — A Distributed Serving System for Transformer-Based Generative
      Models
    url: 'https://www.usenix.org/conference/osdi22/presentation/yu'
    type: primary
  - title: Automatic Prefix Caching — vLLM
    url: 'https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html'
    type: secondary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

为 ChatGPT 类产品设计多用户对话推理服务。请求长度和生成长度差异很大，既有实时流式聊天，也可能有后台批量任务和不同服务等级。

### 需要满足的功能

- 接收包含历史消息、模型和生成参数的请求，返回 token 流或完整结果。
- 支持用户/API key 配额、并发上限、排队、取消与超时。
- 在共享模型资源时兼顾实时请求公平性、长请求和批任务。

### 约束与交付物

分别定义首 token 延迟、生成间隔、端到端耗时与 throughput 目标，说明上下文上限、资源不足和模型实例故障时的语义。缓存或共享计算不能造成跨用户数据泄漏。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

一个用户发送长上下文请求时，其他用户的短聊天不应无限期等待；用户中途取消生成后，应停止继续占用不再需要的推理资源。

## 解题思路与参考答案

我会先按首 token 延迟和公平性定 SLO，再把限流、准入、排队接到 continuous batching 引擎上。比如一条长批处理不能把正在聊天的用户堵住，取消请求也要及时释放 KV 页。vLLM / Orca 的分页 KV 和 iteration 级调度可以作为基础。

这是一道归纳的设计题，覆盖 OpenAI 推理、Anthropic 限流和 NVIDIA 推理栈相关方向。continuous batching 见 `openai-continuous-batching`；prefill/decode 拆分见 `openai-prefill-decode`；KV 页见 `sys-paged-attn`；工具对话的约束见 `design-chat-tools`。

## 请求进门：限流和队列

我会先问：是否流式、首 token SLO、上下文上限、是否共享系统提示、付费档 vs 免费档（不谈单价）、是否允许离线批。然后把入口写成：

- 鉴权 + 配额。 每用户 / 每 API key 的 RPM、TPM、并发。令牌桶：突发可借，长期速率封顶。Anthropic 式的按档限流见 `anthropic-rate-limit`；内存实现见 `xai-rate-limiter`。超限返回明确 retry，不要默默排队到超时。
- 准入。 KV 水位高于阈值就拒绝或降级，不要接进来再 OOM。分页 KV 让水位可算：每条请求预估 `pages ≈ prompt_tokens + max_new`，见 `sys-paged-attn`、`nvidia-paged-kv`。
- 队列。 交互、续写（已有前缀）、批处理三条。交互保 p95 首 token；续写优先命中前缀缓存；批处理填空泡。加权公平：免费档不饿死，但交互不被长批处理堵住。队头阻塞来自请求级 batch，必须 iteration 级调度，见 `openai-continuous-batching`。

优先级不是「谁付钱谁插队」一句话。同优先级 FIFO；交互 > 批；已占用大量 KV 的长生成可降优先级防止占满。饥饿用 aging。取消要能从队列和 running batch 摘掉并释放页。

## 复用缓存并控制生成延迟

多用户同一条系统提示、同一会话多轮，输入 prefill 重复算是主浪费。缓存键是 token id 序列 + 权重版本 + LoRA + 位置语义，不是字符串。模板改一个字、模型热更新，必须从分叉 token 断开。细节见 `sys-prefix-cache`。

会话续写：历史 KV 可钉在会话亲和的 replica 上，换机就要重 prefill 或迁移页。亲和提高命中，降低调度弹性。我会写：短会话哈希到 replica；过长或热点系统提示放全局前缀池，引用计数共享物理块。

安全：前缀缓存按租户隔离键。不能因为系统提示相同就把租户 A 的历史页暴露给 B。包含 prompt 中 PII 的缓存页随会话 TTL 淘汰。

首 token 被 prefill 绑住，decode 绑住 slot。混在同一池，长 prefill 会戳穿交互 p95。拆池或分优先级：prefill 有并发上限；decode 连续批。更大流量可以把 prefill 和 decode 拆到不同机器，见 `sys-prefill-decode-disagg`。NVIDIA 侧看 kernel 占用和 KV bandwidth，不是只看 FLOPs。流式先把已生成 token 推出去；引用校验仍按句，不要先输出再删，见 `design-prod-rag`。

用户刷新或取消时，服务端要停止对应的 decode 并释放 KV，否则会留下后台仍在生成的请求，占满水位。重试带 idempotency key，尤其工具调用，见 `design-tool-prod`。

失败：限流不明显导致客户端空转；无准入控制导致 KV 碎裂；前缀键漏了 LoRA id 导致串话；批处理饿死交互；重试没有幂等把工具副作用打两次。

线上：到达率、拒绝率、队列等待、首 token p95、每 token p95、前缀命中率、KV 水位、批处理公平性。命中率高但 p95 差，可能在用过期亲和把负载打到一台。容量规划用「同时活着的 decode slot」而不是 QPS：长回答占 slot 更久。

release criteria：SLO、错误率、KV 泄漏检查、限流误伤。模型或系统提示变更要让前缀缓存失效，并在金丝雀上看命中率跌多少。

## 追问

**为什么不无限排队？**
排队超过 SLO 等于失败还占内存。宁可快失败、让客户端退避。
**付费档怎么优待？**
更大桶、更高并发、单独池。仍要 aging，避免免费档活锁。不把单价写进白板。
**系统提示每天一改？**
前缀池按版本键。旧页按 TTL 丢。灰度两版提示就两份前缀。
**和 检索增强生成（RAG） 服务差别？**
对话多了多轮 KV 和前缀命中；RAG 多了检索 SLA。调度骨架可共用。

## 相关题

- [[anthropic-rate-limit]]：本题入口「鉴权 + 配额」一步的展开，令牌桶和滑动窗口怎么同时限请求数和 token 数。
- [[msft-azure-tpm]]：调用方视角的 TPM/RPM 配额，429 之后怎么排队、退避和降级。
