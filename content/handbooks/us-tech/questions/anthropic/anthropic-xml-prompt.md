---
id: anthropic-xml-prompt
section: anthropic
order: 6
level: A
title: Anthropic：为什么偏爱 XML 标签组织 tool / 条款，解析失败怎么降级？
quick: "XML 风格标签能把 instructions、documents、example 分开，让模型更容易分清指令和资料。解析时先按标签名抽取完整块，失败再退回纯文本并返回错误；半截工具参数不执行，真正的工具调用交给 API schema。"
tags:
  - Anthropic
  - Prompt
  - XML
  - Tool use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Prompt engineering best practices (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
---

XML 风格标签适合把复杂 prompt 中的不同内容分开，因为它能嵌套、能按名字指代，也方便程序抽取。比如条款、检索文档、用户输入和 tool 结果挤在同一个上下文时，边界不清就容易让模型把资料当成指令。标签能减少这类混淆，但不能保证模型输出合法 XML。

## 标签在干什么

官方说法很具体：输入提示里同时有指令、上下文、示例、可变输入时，用描述性标签包起来，减少误读。没有「模型只认某一组神圣标签名」，但名字要稳定，后文要用同一名字指代。「看 documents 里的合同」比「看上面那段」稳。

嵌套可以这样组织：documents 下面多个 document，每个有 source 和 document_content。条款同理：constitution 下面一条条 principle。tool 结果用 result 包原始输出，避免用户或网页里的句子看起来像系统指令。这和 `anthropic-prompt-injection` 是同一条边界：不可信内容进资料标签，指令留在系统侧。

模型在网上见过大量尖括号文本，这种格式需要的转义较少。用 JSON 包 diff 或代码时，则要转义引号和换行。Anthropic 讲 agent-computer interface 时明确说过，格式开销大会把模型写进死角。所以给模型看的用标签或接近自然语言的字段；给运行时执行的用 JSON Schema。两层不要混成「模型直接吐我去 `eval` 的字符串」。

## 解析失败怎么降级

生产里标签不是 well-formed XML。模型会漏闭合、把标签写进正文、嵌套打叉。我的降级顺序：

1. 严格抽块。按标签名做嵌套计数，取出第一段平衡块。成功就只用块内文本。
2. 宽松抽块。找不到闭合就取到下一个同级开标签或文末。记下 `truncated=true`。
3. 放弃结构。当纯文本，不执行任何 tool。把「解析失败、请用指定标签重写」作为 tool 错误或下一轮用户可见指令还回去。
4. 绝不猜测执行。半截 JSON、半截参数名单，当作没调用。

```python
def grab(text, tag):
    open_, close = f"BEGIN_{tag}", f"END_{tag}"
    i = text.find(open_)
    if i < 0:
        return None
    j = text.find(close, i)
    if j < 0:
        return None
    return text[i + len(open_):j]
```

白板可以用 `BEGIN_tag` / `END_tag` 这种占位，表达的是开闭成对，不是真去上线一套新语法。真系统里用正则硬切嵌套一定翻车，嵌套要用计数或栈。

条款场景的降级更保守：某条 principle 抽不出来，就当该条不存在并告警，不要用模型「补写一条类似的」。补写等于改 constitution。CAI 里条款是人写的版本化规则，见 `anthropic-constitutional-ai`。

原生 tool use 和这些标签各有用途。

现在 API 的 tool 调用使用结构化 `tool_use` 块和 JSON 参数，不需要从散文里抽取标签。XML 还在两头：system 里组织文档与条款；自定义 ACI 里给模型看的 tool 说明。解析失败走 `is_error` 结果，让模型换参数，不要在宿主侧「智能修复后执行」。修复执行是注入的经典口子。

## 追问

- **Markdown 标题不够吗？** 标题不能可靠嵌套，也不好按名字抽取。短 prompt 用纯文本；一混文档和指令就上标签。
- **输出也要标签吗？** 若下游要切「推理 / 答案 / 引用」，让模型用 answer 这类标签包最终答案。失败则整段当答案，不要切错。
- **标签能防注入吗？** 只能降低串角色。网页自己写伪造闭合标签时，宿主必须在入模前转义或替换标签字符。真正边界在产品层，见 `anthropic-prompt-injection`。
- **和 structured output 什么关系？** Schema 约束解码是执行层；XML 标签是给模型看的提示层。能走 API tool schema 就不要用散文伪 XML 当协议。
