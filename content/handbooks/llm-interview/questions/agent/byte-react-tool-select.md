---
id: byte-react-tool-select
section: agent
order: 208
level: A
title: 字节实习一面：ReAct 里怎么选工具，选错了怎么纠？
quick: "先在 Thought 里说清当前缺什么信息、要改变什么状态，再按工具 schema 和观察结果选最贴缺口的工具。选错后，把真实的错误或空结果带进下一轮决策，换工具或参数，不能假装成功。工具目录很大时，先检索候选，再按需加载完整说明。"
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

ReAct 里选工具，是先在 Thought 里写清当前缺什么信息、要改变什么状态，再按工具的字段和类型规范（schema）和已有的 Observation，选最少、最贴这个缺口的工具，Observation 再用来校验成败。选错了，就把真实的错误或空结果带进下一轮 Thought，换工具或换参数，不能在 Thought 里假装成功。纠正信号来自环境，模型自己补一段「已经查到了」不算。ReAct 是 Yao 等提出的先推理再行动的框架，结构总览见 `xiaohongshu-react-structure`。

举个例子，用户问「这个 PR 为什么 CI 红了」。Thought 写「需要失败日志」，调 `get_ci_log(run_id)`，Observation 指出是哪个单测文件，再 `read_file`。要是选成 `search_code("timeout")`，会捞回一堆无关命中，因为缺口是「这次 run 的失败栈」，仓库里所有 timeout 字符串和它没关系。这就是按缺口选、别看到名字就调：缺失败日志就调取日志的工具，要改文件就走编辑工具。Action 要填成可执行的请求，参数满足 schema，别写成自然语言散文。一次只选能闭合当前缺口的最少工具，「顺便搜一下」会把窗口打满。

这套做法的适用条件是工具有明确的 schema，返回结果能判定成败，比如错误码、空结果、校验失败。工具高度同质、返回全是自然语言，或者一次调用就不可逆（删库、对外发信）时，要先检索 / 分级披露，并在执行层加确认，光靠 Thought 自律不够。权限确认见 `byte-team-agent-security`。

选错之后，失败或空结果进入下一轮 Thought，改工具或者改参数，禁止补一句「日志显示超时」。Observation 明确返回 404，就该搜路径或者问用户，换个同名工具再赌没有意义。执行失败（超时、429）和选错工具是两类问题，前者见 `byte-tool-fail-retry`，后者是路由问题，盲着重跑同一个错误调用没用。模型产出的不是合法的工具调用时，Harness 应该拒收并要求重填，半截 JSON 不能当 Observation。步数上限要卡死，不然选错会变成无限「再试一个工具」。

候选工具很多时，工具目录要当检索对象，别一次性当附件塞进输入提示（prompt）。按意图、权限、业务域过滤后，只暴露当前阶段一小撮短 schema，选中了再加载完整文档，治理细节见 `jd-agent-tool-catalog-context`、`agent-tool-routing`。全量暴露会让选错率和文本处理单位（token）一起涨，也更容易被 prompt 注入成「去调那个高权限工具」。评测看工具选择准确率、无效调用率、选错后能否在 $k$ 步内纠正，光看最终答案不够；答对了但乱调工具，工程上仍然不合格，见 `jd-agent-eval-beyond-qa`。

## 追问

**没有显式 Thought 还算 ReAct 吗？**
不算完整的 ReAct，更接近 function-calling 循环。生产上仍然需要一段可检查的中间缺口描述，至少写在 trace 里。

**Observation 是自然语言怎么办？**
尽量结构化，用错误码、命中列表、截断句柄。散文式返回容易让模型把失败读成成功，选错了也更难纠。

**不可逆工具选错了怎么办？**
执行前就要确认、走沙箱；选错如果已经产生副作用，走补偿，别再调一次，见 `byte-multiagent-policy-conflict-recovery` 里的副作用原则。

**和 planner 两段式比呢？**
先规划再执行适合步骤稳定的任务，ReAct 适合观察会改变下一步的探查。CI 诊断更像后者。
