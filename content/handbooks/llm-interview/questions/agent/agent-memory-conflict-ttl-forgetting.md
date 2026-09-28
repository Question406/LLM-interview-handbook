---
id: agent-memory-conflict-ttl-forgetting
section: agent
order: 212
level: S
title: Agent Memory 冲突、时效与遗忘策略怎么设计？
quick: 每条记忆我会带来源、置信、写入时间和 TTL。冲突时按权威源和新近性合并，分不清就提问。过期和用户删除必须真正不可再检索。
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

错法：只优化召回——冲突条目并列塞进窗口，让模型猜哪条是真的；用户删除或过期后只做软删，摘要器下一轮又写回来。Memory 评测若只报 Recall@$K$，正好掩盖这件事，见 `agent-memory-retrieval`。本题要的是写入后的生命周期：冲突怎么合并、TTL 怎么到期、遗忘怎么从索引里真正消失。

## 冲突：权威源、作用域、新近性，必要时分叉提问

每条记忆至少带 `source`、`confidence`、$t_{\mathrm{write}}$、`TTL`、`scope`（会话 / 项目 / 全局）。冲突例：上周说素食，本周点了烤肉。不要两条都召回。优先级通常是：显式用户更正 $\gt$ 权威业务系统 $\gt$ 较新的直接观察 $\gt$ 模型推断。同 scope 内用时间戳覆盖；跨 scope 不要全局覆盖项目约束（这个仓库禁用 Python，不等于用户永远不用 Python）。置信接近且来源同级时，向用户问一句，别静默选边。多假设可以短暂保留，但检索时必须标 `conflicted`，禁止当单一事实注入。合并策略要可回放：记下谁覆盖了谁、依据哪条规则，否则下周又会把旧素食偏好召回来。业务系统（CRM、权限服务）写入的条目应比对话推断更高权威；网页和工具返回默认不可覆盖用户已确认的约束。

$$
\mathrm{valid}(m,t)=\mathbf{1}\big[t \lt t_{\mathrm{write}}(m)+\mathrm{TTL}(m)\big]\cdot\mathbf{1}[\neg\mathrm{deleted}(m)]
$$

过期或已删的条目 $\mathrm{valid}=0$，检索层应直接滤掉，别靠模型「注意时效」。

## TTL 与遗忘必须打到索引，而不只是标记位

凭证、价格、政策、库存短 TTL；饮食偏好、项目惯例长 TTL，但允许用户编辑。TTL 到期要驱逐向量索引、关键字索引和热缓存，并禁止 compaction / summarizer 把过期句再写进 semantic memory。用户删除是硬约束：导出副本可以按合规留存，面向 Agent 的检索路径必须不可见。软删加 `deleted=true` 却仍参与 ANN，等于没忘。过期任务要进后台队列，别等下一次检索才发现「这条其实已经非法」。密钥类记忆到期后还要让依赖它的 procedural 条目失效，避免流程还在教模型去用已作废的 token。

评测不要只测「能不能想起上周的偏好」。构造冲突集（新旧偏好、项目 vs 全局）、过期集（已失效价格仍被引用）、删除集（用户要求忘记后是否仍出现在 top-$k$ 或摘要里）。指标看 false-memory harm 和 freshness accuracy，而不是召回。写入策略仍见记忆分类题；本题收的是 supersede 与 eviction 是否闭环。现场若只答「按时间戳取最新」，要补问：最新的是网页注入怎么办、项目 scope 会不会误伤全局。

## 追问

- **和 `agent-memory-retrieval`？** 那题是评测协议：read/write 拆开、不能只看 Recall@$K$。本题是冲突、TTL、遗忘的系统设计。
- **两条冲突记忆都召回让模型裁决？** 默认不要。会把过期制度又说成现行政策。先失效旧条，裁决权在策略，不在生成。
- **摘要压缩会不会复活已删内容？** 会。compaction 是一次 write，必须重新跑删除与 TTL 过滤，并回归「忘记」用例。
- **项目约束能覆盖全局偏好吗？** 不能自动覆盖。scope 隔离；跨 scope 冲突应提问或按当前任务 scope 取，而不是全局覆盖。
