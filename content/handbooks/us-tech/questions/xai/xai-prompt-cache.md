---
id: xai-prompt-cache
section: xai
order: 13
level: A
title: xAI：系统提示缓存，多租户前缀共享
quick: >-
  复用的是已经算好的 KV，不是字符串。Token 序列、权重、LoRA、位置都一致才能命中。Grok 类长系统提示适合跨请求共享；多租户只共享真公共前缀，租户条款和用户 PII
  处分叉。隔离用 cache salt，防的是错命中和时序侧信道，不是 LRU 实现细节。
tags:
  - xAI
  - Prefix Cache
  - Serving
  - Multi-tenant
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Automatic Prefix Caching — vLLM
    url: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
    type: secondary
  - title: SGLang / RadixAttention
    url: https://lmsys.org/blog/2024-01-17-sglang/
    type: secondary
  - title: PagedAttention paper
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: Open Release of Grok-1
    url: https://x.ai/news/grok-os
    type: primary
---

## 题怎么来的

Grok 产品有长人格 / 政策系统提示，API 多租户又会在同一前缀上叠不同开发者指令。推理岗问的是：这段 KV 能不能算一次、给许多人用，错命中和租户串话怎么防。公开机制是 vLLM automatic prefix caching、SGLang RadixAttention，底层页表见 `sys-paged-attn`、通用前缀缓存见 `sys-prefix-cache`。xAI 内部缓存拓扑没公开，我只讲命中条件和多租户合同。`realInterview: false`。和 `xai-lru-cache` 的差别：那题是通用并发 LRU；本题是 **注意力 KV 前缀**，不是业务对象缓存。

## 命中的是 KV 页，系统提示必须字节级同 token

Prefix cache 复用的是已算好的 K/V 块。Key 至少包括：token id 序列（不是 UTF-8 原文）、模型版本、LoRA、位置编码配置。System prompt 改一个空格、chat template 换一行，从第一个不同 token 断开。把一段 KV 接到另一条长度不同的请求后面，RoPE 起点错了，数值是错的。错命中比 miss 更危险：输出 silently 错。

Grok-1 公开上下文是 8192；后来代际博文声称更长窗口。系统提示越长，prefill 占比越高，前缀命中越值钱。APC 只削 prefill，不削 decode。长 Think 回复（见 Grok-3 公开的 test-time compute）会让缓存收益看起来变小——那是 decode 墙，不是缓存坏了。

实现两条公开索引：

- **块哈希。** vLLM 对固定长度 token 块做链式 hash。公共前缀命中后从分叉块开始 prefill。部分块对不齐就 miss。
- **前缀树。** RadixAttention 按 token 前缀树挂物理页，适合多轮、工具模板头相同、后面分叉。

PagedAttention 的引用计数让共享便宜：多条 block table 指向同一物理块。没有分页，共享意味着 memcpy 一份连续 KV，系统提示一长就划不来。逐出策略是 KV 的 LRU / 引用计数，不要和 `xai-lru-cache` 手写 map+链表搅成一个桶；那是 coding 题，这是 serving 内存。

## 多租户：共享真前缀，分叉即隔离

我会把提示拆三段，不要整段当「一个 system」：

1. **平台公共前缀。** 模型人格、安全政策、工具语法说明。全租户相同，应当共享 KV。这是缓存命中的主力。
2. **租户策略。** 开发者 system 指令、允许的工具列表、品牌语气。只在 **该租户内** 共享。跨租户共享等于把 A 的条款泄漏进 B 的时序和偶然错命中。
3. **用户轮次。** 对话历史、检索块、PII。默认不跨用户共享。多轮同一会话走树的一条枝，会话结束可逐出。

隔离手段公开可讲：vLLM 的 `cache_salt` 折进首块 hash，只有带同一 salt 的请求能复用。用途有二：租户隔离；削弱「用延迟探测某段前缀是否已在缓存里」的侧信道。不要把 salt 设成全局常数又声称多租户安全。

工具调用会在前缀后插入 `tool` 消息。模板必须稳定，否则每轮工具结果都让公共前缀之后整段 miss。Function calling 的 schema 若按请求乱序排列，前缀哈希跟着抖，见 `xai-tool-use`。能固定顺序就固定。

错法：按字符串 hash 缓存「用户 A 的检索结果给用户 B」——那是 ACL 事故，不是前缀缓存。权限故事和微软 Copilot 同一句，只是这里没有 Graph：谁的上下文就谁的 KV，公共段除外。

限流在入口保护 GPU 队列，缓存命中会改变 **有效 prefill 成本**。计费若按 token，要决定命中的前缀算不算钱。公开 API 各家口径不同；xAI 怎么计费以当时文档为准，面试不要编折扣比例。队列公平仍走 `xai-rate-limiter`，缓存命中不是让大象租户免费占满 KV 池。

## 追问

- **为什么必须 token 一致？** KV 是离散 token 上的函数。Tokenizer、特殊符号、模板空白都会改 id。字符串相等不是命中条件。
- **租户想共享同一个 RAG 仓库前缀？** 只有仓库对两家都可见且 ACL 相同才能共享。否则检索块进公共缓存就是串租户。宁可多算 prefill。
- **和 MoE decode 的关系？** 缓存省的是公共前缀的注意力 KV；专家权重每步仍要按新 token 路由。命中不会让专家 GEMM 变齐，见 `xai-moe-decode`。
- **系统提示每周改一版怎么办？** 版本进 cache key。灰度两份前缀就两份 KV，内存翻倍要算进去。切 100% 后再丢旧根节点。
