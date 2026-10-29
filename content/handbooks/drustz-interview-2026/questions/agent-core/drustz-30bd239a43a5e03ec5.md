---
id: drustz-30bd239a43a5e03ec5
section: agent-core
order: 15
level: A
title: 02 · State、Durable Execution 与 Memory · 6. Memory tiers 与治理 ⭐⭐
quick: 作者文档章节 · 02 · State、Durable Execution 与 Memory · 6. Memory tiers 与治理 ⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/02_state_and_memory.md
    type: primary
---
## 6. Memory tiers 与治理 ⭐⭐

| Tier | 内容 | 生命周期 |
|---|---|---|
| Working memory | 当前目标、计划、未决问题、最近 observation | 随 run 结束 |
| Episodic memory | 一次任务的结果、失败、用户修正 | 有 provenance 和 TTL |
| Semantic memory | 稳定事实、术语、偏好或组织规则 | 写入门槛最高 |
| Artifact store | 文档、代码、trace、大结果 | context 只放 pointer/摘要 |

```python
@dataclass(frozen=True)
class MemoryRecord:
    id: str
    subject: str
    kind: str
    value: str
    source_ids: tuple[str, ...]
    scope: str
    confidence: float
    valid_from: datetime
    expires_at: datetime | None
    supersedes: str | None
```



写入 gate（模型的猜测不能直接成为全局事实）：

- [ ] 是否明确/有证据
- [ ] 是否新信息
- [ ] 是否长期有用
- [ ] 是否敏感
- [ ] scope 是否正确
- [ ] 谁能纠错

读取顺序：identity/tenant/ACL → time/TTL → task relevance → token budget。检索后仍要把 source 和不确定性送给模型。

RAG 检索专题见 [../03_gaps/rag.md](?book=drustz-interview-2026&section=agent-core&question=drustz-3ca2bc23429af23dbe)。






**删除的完整语义**



删除不是只从向量索引删一条：

1. 写 tombstone。
2. 清 raw、derived indexes、cache。
3. 验证后续 retrieval 不再返回。
4. 若法规要求 audit，只保留最小必要 metadata。





> 高分句：先建可治理的 MemoryRecord，再选检索技术；相似度不是权限，也不是事实性。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/02_state_and_memory.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/02_state_and_memory.md)。作者整理资料；许可和第三方来源范围见阅读指南。
