---
id: sys-prefix-cache-isolation
section: systems
order: 25
level: A
title: 共享 Prefix Cache 如何省钱但不串数据？
quick: cache key 必须覆盖 model、adapter、tokenizer、RoPE、system context 以及 tenant / security context；用每请求 salt 或 namespace 阻止跨安全边界复用，显式失效并把 cache hit 当作潜在侧信道监控。
tags:
  - Prefix Cache
  - Multi-tenant
  - Security
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: vLLM Automatic Prefix Caching
    url: https://docs.vllm.ai/en/v0.18.1/design/prefix_caching/
    type: primary
---

prefix cache 可以复用相同 token 前缀的 KV，显著减少 prefill 成本；但“前缀 token 相同”不等于“可跨用户共享”。模型/adapter、tokenizer、position encoding、system prompt、检索结果和 tenant 权限任一不同都可能改变语义或泄露上下文。

缓存 namespace/key 需要携带安全上下文，敏感会话用 request salt 彻底隔离；模型或 prompt 版本变更必须失效。缓存读写本身不应暴露他人是否命中，否则 timing 也可能成为侧信道。

验收包括 hit rate、TTFT 节省、错误复用率、版本失效率和跨 tenant 安全测试。成本优化不能绕过数据隔离模型。
