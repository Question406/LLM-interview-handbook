---
id: drustz-ca92a1502b6dcd6644
section: agent-core
order: 6
level: A
title: 01 · Agent Loop 与 Tool 契约 · 4. Tool design：为非确定性调用者设计契约 ⭐⭐
quick: 作者文档章节 · 01 · Agent Loop 与 Tool 契约 · 4. Tool design：为非确定性调用者设计契约 ⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/01_loop_and_tools.md
    type: primary
---
## 4. Tool design：为非确定性调用者设计契约 ⭐⭐

```python
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict
    version: str
    risk: str  # read / reversible_write / irreversible
    parallel_safe: bool
    timeout_seconds: float
    max_result_bytes: int
    required_scopes: tuple[str, ...]
```



好工具 checklist：

- [ ] 名称和描述说明「何时用、何时不用、返回什么」。
- [ ] schema 小且约束强；枚举、required、范围、格式明确。
- [ ] 粒度围绕完整意图，而不是把底层 API 每个 endpoint 原样暴露。
- [ ] 返回最小但足够的上下文，并给稳定 ID；不要倾倒巨量 JSON。
- [ ] error 结构化：`code/message/retryable/retry_after`。
- [ ] secret 由 executor 注入，不进入 prompt、trace 或 model output。
- [ ] tool output 是不可信数据，不能修改 system policy。






**Retry matrix（按错误类型的默认策略）**



| 情况 | 默认策略 |
|---|---|
| read + transient 429/5xx | bounded exponential backoff + jitter |
| validation error | 不原样重试；把具体字段错误回传模型 |
| deterministic not-found | 通常不重试，除非模型能改变查询 |
| write 且 provider 支持 idempotency key | 同 key 可安全重试；先查 status 更稳 |
| write 且不支持幂等 | timeout 后进入 unknown，不自动重复 |
| permission denied | 不重试；解释需要的 authority |

write 超时后的 unknown 状态处理见 [./02_state_and_memory.md](?book=drustz-interview-2026&section=agent-core&question=drustz-027e90f708cef5244f) crash window 一节。





> 高分句：工具描述影响选择，但权限不在描述里；executor 再做 authentication、authorization 与 validation。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/01_loop_and_tools.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/01_loop_and_tools.md)。作者整理资料；许可和第三方来源范围见阅读指南。
