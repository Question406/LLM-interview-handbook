---
id: sys-prefix-cache-isolation
section: systems
order: 25
level: A
title: 共享 Prefix Cache 如何省钱但不串数据？
quick: "公共前缀可以共享 KV，但 cache key 要带上 model、adapter、tokenizer、RoPE、system context 和 tenant / security context，确保激活和权限都一致。私有段用 namespace 或每请求 salt 隔离，版本变更时主动失效，同时监控命中速度是否泄露了其他用户的信息。"
tags:
  - Prefix Cache
  - Multi-tenant
  - Security
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: vLLM Automatic Prefix Caching
    url: https://docs.vllm.ai/en/v0.18.1/design/prefix_caching/
    type: primary
---

共享 Prefix cache 时，我会让公共系统提示复用已经计算好的 K/V，把用户文档和私有检索结果留在各自的安全边界内。这样可以省掉重复的 prefill，也就是处理输入并建立缓存的计算，降低首个 token 的等待时间（TTFT）和成本。比如同一条产品 system prompt 可以共享，但某个租户的 CRM 内容不能给另一个租户复用；即使 token id 一样，LoRA 或 RoPE 不同也会算出不同的 KV。

## 先保证命中的 KV 确实可复用

命中意味着「用别人算过的激活当自己的历史」。key 至少要编码所有会改变这些激活的东西：

- 模型版本 / 量化方案 / dtype
- adapter / LoRA id（base 相同、adapter 不同，KV 完全不能复用）
- tokenizer 与 special token 映射
- 位置编码（RoPE 基、YaRN 因子、`max_position_embeddings`）
- system prompt、工具 字段和类型规范（schema）、检索到的私有文档
- **tenant / security context**（用户、工作区、权限集）

少编一项，就会在「看起来 token 一样」时串数据。强化学习（RL） 里还要加 `policy_version`：同步过的新权不能接着用旧 KV，见 `infra-rl-weight-sync`。vLLM Automatic Prefix Caching 按 token 块做哈希；生产上必须在哈希外包一层业务 namespace，不能假设引擎的 block hash 已经含租户。Tokenizer 升级、加 special token、改 chat template，都会让同一段自然语言对应不同 token id 或不同位置，旧缓存必须整池失效。只改 system 输入提示里的一个日期而不换 key，命中的是过期政策。Adapter 热加载更危险：base 权相同、LoRA 不同，block hash 若只看 token，会把 A 租户的 KV 喂给 B 租户的 adapter，输出可能看起来正常，其实串了激活。

跨安全边界默认 **不共享**。做法：

- 每租户一个 cache namespace；敏感会话再加 **per-request salt**，彻底禁止跨请求复用。
- 模型、prompt 模板、权限策略变更时显式失效，不要等 LRU 自然挤掉。
- 共享前缀只放真正公共的系统提示；用户文档、CRM 字段、内部检索结果进私有段，永远不要当公共 prefix。

「省钱」发生在公共段的命中率：同一条产品 system prompt 被成千上万请求复用，prefill 从整段变成几个新 token。私有段命中率低是预期，不要为了 hit rate 把租户键拿掉。

## 再检查命中是否泄露信息

Cache 读写不应暴露「别人是不是刚问过同样的话」。命中导致 TTFT 明显变短，攻击者可以用时序判断某前缀是否在缓存里。多租户下这是经典侧信道。缓解：对安全敏感路径关闭共享、加 salt、或把命中延迟填充到与未命中同量级（贵，只用于高敏）。监控错误复用率、跨 tenant 探测、版本失效率，不能只报 hit rate 和 TTFT 节省。

上线时，公共 system prompt 和稳定工具 schema 的命中率按模型版本分别统计，同时看 TTFT 节省、错误复用、版本失效和跨 tenant 探测。后三项检查不过，就还不能确认节省成本的方案是安全的。金融、医疗、内部代码这类高敏感场景默认加 salt，代价是多做一些 prefill。RL 中同一输入提示的 $n$ 条回答可以共享 prompt KV，但跨用户、跨策略版本仍要隔离。

## 追问

**token 相同为什么还不能共享？**
KV 是模型状态，不是文本。adapter、RoPE、tokenizer、权限上下文、policy version 任一不同，激活就不同，或会把他人上下文续进当前解码。引擎的 block hash 默认不含租户，必须外包 namespace。
**salt 会不会把省钱打没？**
高敏会话本就不该共享。钱省在公共 system prefix 和稳定工具 schema；salt 打在用户私有段。用总 hit rate 当 KPI 会诱使拿掉租户键。
**和 prompt cache 落盘是一回事吗？**
磁盘缓存多一次序列化，隔离规则相同：key 仍要带模型与租户，失效策略更要硬。版本变更必须主动失效，不能等 LRU。
**RL 采样轨迹（rollout） 能不能开 prefix cache？**
同一输入提示 的 $n$ 条可以共享 prompt KV，这是合法的组内复用。跨用户、跨 `policy_version` 不行，否则旧权的激活会续进新权。
**命中会不会泄露信息？**
会。TTFT 差一个数量级就能判断某前缀是否在缓存里。高敏行业默认 salt，或把命中延迟垫到与未命中同量级。
**改 chat template 要不要清缓存？**
要。同一自然语言会变成不同 token 或不同位置，旧 KV 不能用。只改 system 里一个日期而不换 key，命中的是过期政策。
**公共前缀多长才值得共享？**
足够长、足够稳、真正全租户一样。三五个 token 的问候语省不下 prefill；整段产品 system prompt 才是主战场。私有检索结果再长也不能进公共池。
**怎么兼顾省钱和隔离？**
公共稳定前缀进带模型版本的共享 namespace；用户、租户、盐、检索进私有段。key 漏一项就会在 token 看起来一样时串数据。命中时序是侧信道。
