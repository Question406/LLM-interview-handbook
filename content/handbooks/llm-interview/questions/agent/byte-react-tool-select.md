---
id: byte-react-tool-select
section: agent
order: 208
level: A
title: 字节实习一面：ReAct 里怎么选工具，选错了怎么纠？
quick: >-
  先把用户目标拆成可验证子目标，再按 schema 和当前观察选最少工具。选错就用工具返回当观察，别硬编下一跳。候选工具多时做检索或分级披露，避免全量塞进 prompt。
tags:
  - ByteDance
  - ReAct
  - Tool Calling
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“ReAct 框架下，Agent 如何选择工具？选错了怎么纠正？”**

错法：「看到工具名字就调」，或选错之后在 Thought 里假装成功。ReAct（Yao 等，先推理再行动）里选工具是：Thought 写清当前缺口，Action 按 schema 和 Observation 选最少、最贴缺口的工具，Observation 用来校验成败。纠正信号来自环境，不是模型补一段「已经查到了」。结构总览见 `xiaohongshu-react-structure`。

## 按缺口选，不按名字选

Thought 要回答两件事：缺什么信息、要改变什么世界状态。缺失败日志就调取日志的工具；要改文件就走编辑工具。Action 必须填成可执行请求：参数满足 schema，而不是自然语言散文。一次只选能闭合当前缺口的最少工具，避免「顺便搜一下」把窗口打满。

适用条件：工具有明确 schema、返回可判定成败（错误码、空结果、校验失败）。工具高度同质、返回都是自然语言、或一次调用不可逆（删库、对外发信）时，要先检索/分级披露，并在执行层加确认，而不是靠 Thought 自律。权限确认见 `byte-team-agent-security`。

例如用户问「这个 PR 为什么 CI 红了」。正确路径：Thought「需要失败日志」→ `get_ci_log(run_id)` → Observation 指出单测文件 → 再 `read_file`。选成 `search_code("timeout")` 会捞到一堆无关命中。缺口是「这次 run 的失败栈」，不是仓库里所有 timeout 字符串。

## 选错了：把 Observation 写回，禁止臆造

纠正循环：失败或空结果进入下一轮 Thought，改工具或改参，禁止补「日志显示超时」。若 Observation 明确 404，应搜索路径或问用户，而不是换一个同名工具再赌。执行失败（超时、429）和选错工具是两类问题：前者见 `byte-tool-fail-retry`，后者是路由问题，盲着重跑同一错误调用没有意义。

解析失败（模型产出的不是合法 tool call）应由 Harness 拒收并要求重填，不要把半截 JSON 当 Observation。步数上限要卡死，否则选错会变成无限「再试一个工具」。

## 候选很多时不要全量塞进 prompt

工具目录是检索对象，不是一次性附件。按意图、权限、业务域过滤后，只暴露当前阶段一小撮短 schema；选中再加载完整文档。治理细节见 `jd-agent-tool-catalog-context`、`agent-tool-routing`。全量暴露会让选错率和 token 一起涨，也更容易被 prompt 注入成「去调那个高权限工具」。

评测看工具选择准确率、无效调用率、选错后是否在 $k$ 步内纠正，而不是只看最终答案。答对但乱调工具，工程上仍不合格，见 `jd-agent-eval-beyond-qa`。

## 追问

- **没有显式 Thought 算不算 ReAct？** 不算完整 ReAct，更接近 function-calling 循环。生产仍需要可检查的中间缺口描述，至少写在 trace 里。
- **Observation 是自然语言怎么办？** 尽量结构化（错误码、命中列表、截断句柄）。散文返回会让模型把失败读成成功，选错更难纠。
- **不可逆工具选错了？** 执行前确认和沙箱；选错若已发生副作用，走补偿而不是再调一次，见 `byte-multiagent-policy-conflict-recovery` 里的副作用原则。
- **和 planner 两段式比呢？** 先规划再执行适合步骤稳定的任务；ReAct 适合观察会改变下一步的探查。CI 诊断更像后者。
