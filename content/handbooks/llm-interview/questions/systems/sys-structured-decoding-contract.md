---
id: sys-structured-decoding-contract
section: systems
order: 21
level: S
title: JSON Schema / Grammar constrained decoding 能保证什么，不能保证什么？
quick: 它能在解码阶段保证合法 token、JSON/grammar 和部分字段约束；不能保证业务语义、权限、SQL 安全或参数真的可执行。仍需服务端 validation、canonicalization、policy check，并测量约束的延迟与吞吐代价。
tags:
  - Structured Output
  - Constrained Decoding
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: vLLM Structured Outputs
    url: https://docs.vllm.ai/en/v0.9.2/features/structured_outputs.html
    type: primary
---

grammar 或 JSON Schema 在 token mask 层排除非法续写，因此可以保证格式、枚举、类型和部分结构。它适合 function arguments、机器可读 extraction 和稳定 UI，不需要事后反复 repair JSON。

但合法 JSON 仍能包含未授权的 account ID、危险 SQL、错误金额或不存在的业务对象。执行器必须进行 schema 之外的业务 validation、权限检查、参数 canonicalization、幂等键和高风险确认。

上线应观察 constrained decode latency、token mask 开销、fallback/repair rate 和 schema drift。不要让“模型输出有效 JSON”被误解为“工具调用安全且正确”。
