---
id: design-prompt-mgmt
section: design
order: 13
level: A
title: 设计：prompt / 工具 schema 版本、灰度、回滚
quick: "提示、工具 schema 和模型权重一起组成可复现的发布配置，修改后先过评测，再按用户灰度。每次请求固定 release id，出问题时切回旧 release，并同步处理前缀缓存；直接热改生产提示会绕过这些检查。"
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

## 题目描述

本题是手册归纳的系统设计练习，不是某家公司现场题面的逐字记录。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

为多个模型产品设计提示模板和工具接口的发布管理平台。线上行为同时受模型版本、系统提示、工具 schema、解码参数和产品策略影响。

### 需要满足的功能

- 创建、审核、比较和发布一份完整配置，能识别其组成版本。
- 支持按指定用户或流量逐步启用新配置，并能恢复到此前可用版本。
- 根据一次历史请求确定当时生效的配置，支持离线复现及事故调查。

### 约束与交付物

同一次请求不能混用不兼容的模板与工具 schema。需要定义变更权限、兼容性检查、发布验收、回滚语义和审计保留范围。

请给出需求边界、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

发布配置 R2 后某批工具调用失败，调查者提供 request_id，应能找回它使用的模型、提示、schema 和参数，并确定该请求是否属于 R2 的灰度流量。

## 解题思路与参考答案

我会把模型、系统提示、工具 schema 和解码参数绑定成一份 release，先评测再灰度，出问题时整体切回旧版本。比如只改一句系统提示，也可能改变工具确认行为；如果日志只记模型版本，就复现不了用户投诉。OpenAI function calling、Anthropic 工具循环和 Microsoft Copilot 都涉及提示及 schema 的生产管理。工具运行时见 `design-tool-prod`；评测闸门见 `design-eval-platform`、`design-offline-eval`；客服话术见 `design-chat-tools`。

## 版本：将提示、schema 和模型绑定为一份发布配置

我会先问：几个表面（web、API、内部 agent）、谁能改提示、是否多模型、工具是否对外。然后把一份 release 定义成：

`model_ckpt + system_prompt@sha + tool_schema@sha + decoder_params + policy_flags`

缺一项就无法复现用户投诉。提示当代码：PR、diff、review、owners。不要在控制台热改生产。模板变量（产品名、政策日期）和指令文本分开，避免「改日期」误改行为。

工具 schema：名字、JSON 字段、必填、副作用级别。演进只加可选字段；改名或改语义走新工具名 + 弃用窗口。模型按 schema 版本生成调用，运行时拒绝未知必填缺失。Anthropic 强调工具少而稳，见 `anthropic-tool-use`。schema 一变，旧对话里的 tool 历史可能失效，要迁移或切断会话。

多个产品入口共用一份核心政策，再各自增加界面包装，避免复制几份系统提示后分别修改、逐渐漂移。

## 灰度：评测先于流量

变更路径：

1. 离线集 + 金标对话重跑，见 `design-offline-eval`。提示敏感切片：拒答、工具确认、有实际证据支持。
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

回滚必须秒级切流量，不依赖重新部署权重。提示存在配置服务，带签名和权限。谁改了生产提示要审计：作者、diff、评测链接、审批。事故回顾看的是这条链，不是模型 损失（loss）。

失败模式：prod 控制台改提示；schema 删字段导致旧客户端崩；灰度只看点赞忽略工具误操作；回滚了提示忘了清前缀缓存，用户仍吃到旧 KV；多语言提示只改了英语。

工具确认文案也是提示的一部分，必须进版本。UI 写「退款」JSON 写另一回事，是提示和 schema 不一致，见 `design-agent-harness`。

## 追问

**提示算代码还是数据？**
当代码发版，当数据做评测。两边都要。
**用户自定义系统提示怎么办？**
产品表面和政策提示分层。政策层不可被用户覆盖，见 `anthropic-prompt-injection`。
**要不要把提示微进模型？**
稳定政策可蒸馏；日更条款不要进权重，见 `design-prod-rag`。
**schema 加字段旧模型不会填？**
可选字段 + 服务端默认。需要新行为就新工具名，不要静默改语义。
