---
id: design-prompt-mgmt
section: design
order: 13
level: A
title: 设计：prompt / 工具 schema 版本、灰度、回滚
quick: >-
  提示和工具 schema 是生产配置，和模型权重一起发版。改一句系统提示等于改模型行为。要 git、评测闸门、按流量灰度、
  能按版本回滚。热补生产提示且不跑评测，算事故。
tags:
  - OpenAI
  - Anthropic
  - Microsoft
  - Prompt
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
  - title: openai/evals
    url: https://github.com/openai/evals
    type: secondary
---

OpenAI function calling、Anthropic 工具循环、Microsoft Copilot 都把提示和 schema 当产品表面。白板问版本 / 灰度 / 回滚，是因为现场事故经常是「改了一句系统提示」。不是某次逐字题。工具运行时见 `design-tool-prod`；评测闸门见 `design-eval-platform`、`design-offline-eval`。客服话术见 `design-chat-tools`。

## 版本：提示、schema、模型钉死成发布

我会先问：几个表面（web、API、内部 agent）、谁能改提示、是否多模型、工具是否对外。然后把一份 **release** 定义成：

`model_ckpt + system_prompt@sha + tool_schema@sha + decoder_params + policy_flags`

缺一项就无法复现用户投诉。提示当代码：PR、diff、review、owners。不要在控制台热改生产。模板变量（产品名、政策日期）和指令文本分开，避免「改日期」误改行为。

工具 schema：名字、JSON 字段、必填、副作用级别。演进只加可选字段；改名或改语义走新工具名 + 弃用窗口。模型按 schema 版本生成调用，运行时拒绝未知必填缺失。Anthropic 强调工具少而稳，见 `anthropic-tool-use`。schema 一变，旧对话里的 tool 历史可能失效，要迁移或切断会话。

多表面不要复制粘贴三份系统提示。核心政策一份，表面包装一份。复制后必漂。

## 灰度：评测先于流量

变更路径：

1. 离线集 + 金标对话重跑，见 `design-offline-eval`。提示敏感切片：拒答、工具确认、接地。
2. 影子：新提示只打分不对外，对比旧版裁判和人抽查，见 `align-llm-judge`。
3. 金丝雀：1% 用户或内部员工。护栏：安全事故、工具误操作、p95、过度拒绝。
4. 放量。按用户哈希，避免同一用户来回跳版本。

模型升级和提示升级尽量不同时。两个一起变，回滚不知道回哪。前缀缓存键必须含提示 sha，见 `sys-prefix-cache`、`design-chat-serving`。

Feature flag 钉在 release id 上，不是钉在「最新 git」。回滚是切回旧 release，不是再热改一句「先 hotfix」。

```python
def resolve_release(user_id, flags):
    # pin a full tuple, not "latest prompt"
    if hash_to_unit(user_id) < flags.canary_pct:
        return flags.canary_release
    return flags.stable_release
```

A/B 同一套护栏纪律，不要每天 peek，见 `design-eval-platform`。

## 回滚和事故

回滚必须秒级切流量，不依赖重新部署权重。提示存在配置服务，带签名和权限。谁改了生产提示要审计：作者、diff、评测链接、审批。事故回顾看的是这条链，不是模型 loss。

失败模式：prod 控制台改提示；schema 删字段导致旧客户端崩；灰度只看点赞忽略工具误操作；回滚了提示忘了清前缀缓存，用户仍吃到旧 KV；多语言提示只改了英语。

工具确认文案也是提示的一部分，必须进版本。UI 写「退款」JSON 写另一回事，是提示和 schema 不一致，见 `design-agent-harness`。

## 追问

- **提示算代码还是数据？** 当代码发版，当数据做评测。两边都要。
- **用户自定义系统提示怎么办？** 产品表面和政策提示分层。政策层不可被用户覆盖，见 `anthropic-prompt-injection`。
- **要不要把提示微进模型？** 稳定政策可蒸馏；日更条款不要进权重，见 `design-prod-rag`。
- **schema 加字段旧模型不会填？** 可选字段 + 服务端默认。需要新行为就新工具名，不要静默改语义。
