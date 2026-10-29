---
id: agent-memory-conflict-ttl-forgetting
section: agent
order: 212
level: S
title: Agent Memory 冲突、时效与遗忘策略怎么设计？
quick: "每条记忆带来源、置信度、写入时间、TTL 和作用域。冲突时按权威源、作用域和新近性合并，分不清就问用户；过期和用户删除的条目要从所有检索路径里清掉，检索不到才算真忘了。"
tags:
  - Memory
  - TTL
  - Conflict Resolution
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: A Survey on the Memory Mechanism of LLM-based Agents
    url: https://arxiv.org/abs/2404.13501
    type: primary
---

我会给每条记忆带上来源、置信度、写入时间、TTL 和作用域，冲突时按权威源和新近性合并，分不清就问用户；过期和被用户删除的条目，要从检索路径里彻底消失。这题问的是记忆写入以后的生命周期，召回率再高也解决不了它。

先说冲突。比如用户上周说自己吃素，这周点了烤肉。省事的做法是两条都召回，让模型去猜哪条是真的，结果模型很可能把过期的偏好当现行事实用。所以每条记忆至少要有 `source`、`confidence`、$t_{\mathrm{write}}$、`TTL`、`scope`（会话 / 项目 / 全局），合并时按优先级来：显式用户更正 $\gt$ 权威业务系统 $\gt$ 较新的直接观察 $\gt$ 模型推断。CRM、权限服务这类业务系统写入的条目，比对话里推出来的更权威；网页和工具返回默认不能覆盖用户已经确认的约束。

同一个 scope 里用时间戳覆盖。跨 scope 不要全局覆盖项目约束，「这个仓库禁用 Python」不等于用户永远不用 Python。置信度接近、来源又同级的时候，问用户一句，别悄悄选一边。多个假设可以短暂并存，但检索时必须标 `conflicted`，不能当成单一事实注入。合并要能回放，记下谁覆盖了谁、依据哪条规则，不然下周旧的素食偏好又会被召回来。

有效性可以这样定义：

$$
\mathrm{valid}(m,t)=\mathbf{1}\big[t \lt t_{\mathrm{write}}(m)+\mathrm{TTL}(m)\big]\cdot\mathbf{1}[\neg\mathrm{deleted}(m)]
$$

过期或者已删除的条目 $\mathrm{valid}=0$，检索层直接滤掉，别指望模型自己「注意时效」。

## 到期和删除也要清理索引

凭证、价格、政策、库存用短 TTL；饮食偏好、项目惯例用长 TTL，并允许用户编辑。TTL 到了，要把向量索引、关键字索引和热缓存里的条目都驱逐掉，还要防止 compaction / summarizer 把过期的句子再写回 semantic memory。用户删除是硬约束：按合规要求留存的导出副本可以有，面向 Agent 的检索路径里必须看不见。只加个 `deleted=true` 做软删、却仍然参与 ANN，就等于没忘。过期清理要放进后台队列，别等下一次检索才发现这条早就失效了。密钥类记忆到期后，依赖它的 procedural 条目也要一起失效，免得流程还在教模型用一个已经作废的 token。

评测上，「能不能想起上周的偏好」只是一小部分。要构造冲突集（新旧偏好、项目 vs 全局）、过期集（已失效的价格还被引用）、删除集（用户要求忘记后，还会不会出现在 top-$k$ 或摘要里），指标看 false-memory harm 和 freshness accuracy。Memory 评测只报 Recall@$K$，正好会把这些问题盖住，见 `agent-memory-retrieval`。写入策略见记忆分类题，这题关注旧记忆有没有被正确替换、失效条目有没有从检索系统里清除。面试时对方如果只答「按时间戳取最新」，可以接着问：最新的那条是网页注入的怎么办？项目 scope 会不会误伤全局？

## 追问

**这和 `agent-memory-retrieval` 怎么分？**
那题是评测协议：read 和 write 拆开测，光看 Recall@$K$ 不够。这题是冲突、TTL、遗忘的系统设计。

**两条冲突记忆都召回，让模型裁决行不行？**
默认不行，模型会把过期的制度当成现行政策说出来。先让旧条目失效，裁决权放 on-policy 层，不交给生成。

**摘要压缩会不会把已删的内容复活？**
会。compaction 本身就是一次 write，必须重新跑删除和 TTL 过滤，并回归「忘记」的用例。

**项目约束能覆盖全局偏好吗？**
不能自动覆盖。scope 是隔离的，跨 scope 冲突要么问用户，要么按当前任务的 scope 取，不做全局覆盖。
