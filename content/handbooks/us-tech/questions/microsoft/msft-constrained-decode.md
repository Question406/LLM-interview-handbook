---
id: msft-constrained-decode
section: microsoft
order: 14
level: A
title: Microsoft：约束解码 / JSON 文法，和自由生成的质量
quick: "约束解码把 JSON Schema / 文法变成逐 token 掩码，保证机器接口的字段和语法合法。格式约束也会改变生成分布，多步推理可先得出结果再填结构。验收分别看可解析率与答案正确率，副作用与权限仍由工具运行时检查。"
tags:
  - Microsoft
  - Constrained Decoding
  - JSON
  - Structured Output
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Guided Generation for Large Language Models
    url: https://arxiv.org/abs/2307.09702
    type: primary
  - title: Let Me Speak Freely? Format Restrictions and LLM Performance
    url: https://arxiv.org/abs/2408.02442
    type: primary
  - title: guidance-ai/guidance
    url: https://github.com/guidance-ai/guidance
    type: primary
  - title: Azure OpenAI structured outputs
    url: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/structured-outputs
    type: primary
---

约束解码可以在生成过程中保证 JSON 结构合法，但内容是否正确要另外评。工具参数需要字段、类型和必填项的硬约束；多步推理则要留出先推理再填答案的空间。比如 schema 要求先填 `answer` 再写 `reason`，模型可能先决定答案，之后才补理由。

## 文法如何限制下一个 token

自由生成在完整词表上 softmax，约束解码先将 JSON Schema / CFG 编成自动机，根据当前前缀只允许合法 token，其余 logit 置为 $-\infty$。logits 与 mask 都是 `[B, V]`，括号、逗号、字段名与 `true/false/null` 由运行时限制。

BPE token 可能跨字符边界，例如包含半个引号，朴素字符文法可能误排合法 token。实现需要预计算词表 token 的可接受性，并维护状态迁移。Guidance 把正则、选择、JSON 嵌入提示，Outlines 一类工作将 CFG 编为掩码，Azure structured outputs 在响应格式中接收 schema。本卡根据这些公开工作讨论，不作为逐字真题，`realInterview: false`。

```python
def step(logits, fsm):
    allow = fsm.allowed_token_ids()
    masked = torch.full_like(logits, float("-inf"))
    masked[allow] = logits[allow]
    tok = sample(masked)
    fsm.push(tok)
    return tok
```

生成后再 `json.loads` 并反复重试，可能耗尽长工具参数和嵌套数组的 TPM，见 `msft-azure-tpm`，还可能产生不同字段、触发重复副作用。结构化错误应像 `msft-semantic-kernel`、`msft-autogen` 的工具合同一样交给机器处理。

## 按任务选择约束位置

Let Me Speak Freely?（2024）对比硬 JSON、prompt 格式要求、自然语言后转结构，发现更早、更严的格式限制会损害部分推理任务。分类与枚举也可能因候选减少而受益，不能一概说自由生成更好。

工具参数、表单、落库字段可用硬约束，让枚举、必填和类型合法。多步推理可先自由生成，或只约束最终 JSON，再二次调用 / 解析成结构；Azure 上会多花一次 TPM，但能分别测出正确率。给用户阅读的散文不必放在 JSON 模式中。

自由生成可能漏括号、出现未转义换行或发明键，所以验收同时报告可解析率和答案正确率，也加入「合法但错」切片。掩码截断了条件分布，日期格式过窄、枚举漏同义词，都可能逼出合法却不合适的值。

Function calling 的目标是 `tool_calls`，并行工具与必填参数也可由 schema 限制。约束不管理写操作确认或副作用，执行边界仍见 `msft-semantic-kernel`。

## 追问

**JSON mode 与 JSON Schema 差在哪？**
前者通常保证能解析，后者限制字段、类型和必填。工具调用要避免 `cityy` 这类新键，需要后者。

**RAG 引用也能约束吗？**
可以把 doc id 限制为本次检索枚举或正则，减少编文件名。权限仍先在检索层做，见 `msft-copilot-ground`、`msft-azure-ai-search`。

**运行时开销如何控制？**
每步增加掩码，短 JSON 通常较小，长 schema 与大词表要预编译 token 集合，避免热路径现编自动机。
