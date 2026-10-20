---
id: msft-constrained-decode
section: microsoft
order: 14
level: A
title: Microsoft：约束解码 / JSON 文法，和自由生成的质量
quick: "文法先编译成 token 掩码：每步只许合法续写，JSON 括号和字段名由运行时保证。工具调用和表单需要这份硬保证。推理题若一上来就把 answer 键卡死，思维链会被挤掉，公开实验里比自由生成再解析更差。先想后填结构，或只约束外壳。"
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

## 题怎么来的

微软推理 / Copilot / Agent 岗会问：工具参数和表格输出怎么保证是合法 JSON，而不是「prompt 里写请输出 JSON」。公开锚点是 Guidance（正则 / 文法引导生成）、Outlines 那类把 CFG 编成词表掩码的工作，以及 Azure OpenAI 的 structured outputs。质量对照用 *Let Me Speak Freely?*（2024）：越严的格式限制，推理任务掉得越狠。不是某场逐字面经。`realInterview: false`。接到插件时和 `msft-semantic-kernel`、`msft-autogen` 是同一条合同：机器可读的失败，不能靠模型口述。

## 约束是词表上的掩码，不是事后正则

自由生成：每步在整个词表上 softmax。约束解码：先把 JSON Schema / CFG 编成自动机，当前前缀对应一个状态，下一步只允许进入合法状态的 token。非法 token 的 logit 置成 $-\infty$。括号、逗号、字段名、`true/false/null` 由运行时保证，不靠「请遵守 schema」。

Shape 口播：logits 仍是 `[B, V]`，多了一张同形的 mask。开销在状态迁移和「这个 token 会不会跨过文法边界」：一个 BPE 可能含半个引号，朴素字符级文法会错误地排除本来合法的 token，所以工业实现要在词表上预计算 token 是否可接受。Guidance 把正则 / 选择 / JSON 嵌进提示；Azure structured outputs 把 schema 放到响应格式里，服务端做硬约束。面试画的是这层，不要背 SDK 字段名。

伪代码只表达合同：

```python
def step(logits, fsm):
    allow = fsm.allowed_token_ids()
    masked = torch.full_like(logits, float("-inf"))
    masked[allow] = logits[allow]
    tok = sample(masked)
    fsm.push(tok)
    return tok
```

常见误区是：生成完再 `json.loads`，失败就重试。短字段偶尔能过，长工具参数、嵌套数组可能因反复重试而耗尽 TPM 配额，见 `msft-azure-tpm`。重试还可能换一套字段，下游当两次副作用。

## 质量和自由生成：约束外壳，别约束思路

*Let Me Speak Freely?* 把限制分成三档：JSON-mode 硬约束、只在提示里要求格式、先自然语言再转结构。推理任务上，越早把输出卡成 JSON，分数掉得越明显。一个具体机制：schema 若把 `answer` 放在 `reason` 前面，模型会先填答案再编理由，思维链被结构挤掉。分类 / 枚举反而可能涨：候选集合变小，乱说话的空间没了。

我会拆产品：

1. **工具参数、表单、要进数据库的字段。** 硬约束。合法比「更会推理」优先。枚举、必填、类型由文法保证。
2. **要多步推理再给结论。** 先自由生成（或只约束「最终一行是 JSON」），再二次调用或正则抽出结构。Azure 上这是两次 TPM，但比一次 JSON-mode 把 GSM8K 打崩更可测。
3. **中间思维链给用户看。** 不要用 JSON 模式生成给用户读的散文。约束留给机器接口。

「自由生成质量更好」不是永远成立。自由生成会漏括号、会在字符串里塞未转义换行、会发明 schema 没有的键。产品指标要拆：**可解析率** 和 **答案正确率**。只报其中一个，会把「漂亮但解析失败」或「合法但答错」洗掉。

和 function calling 的衔接：模型该调工具时，解码目标是 `tool_calls` 结构，不是聊天散文。并行工具、必填参数，schema 能提供比提示词更严格的保证。写操作仍要确认，约束不管副作用，见 `msft-semantic-kernel`。

## 追问

- **约束会不会改变分布，导致「合法但傻」？** 会。掩码是在截断条件分布。schema 过窄（日期只许一个格式、枚举漏同义词）会逼模型选次优合法值。验收要带「合法但错」切片，不要只跑 parser 通过率。
- **JSON mode 和 JSON Schema 差在哪？** 前者多半只保证能 parse；后者卡字段名、类型、必填。工具调用要后者。只开 JSON mode，模型仍能发明 `cityy`。
- **和 检索增强生成（RAG） 引用一起用？** 引用 id 做成枚举或正则（只许检索返回的 doc id），比让模型自由写文件名安全。权限仍在检索层做掉，见 `msft-copilot-ground`、`msft-azure-ai-search`。
- **延迟？** 每步多一次掩码。短 JSON 可忽略；长 schema、大词表要预编译 token 集合。别在热路径上每次从 Schema 现编自动机。
