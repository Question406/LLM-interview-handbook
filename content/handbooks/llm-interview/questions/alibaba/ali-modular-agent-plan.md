---
id: ali-modular-agent-plan
section: alibaba
order: 16
level: A
title: Modular Agent 如何实现多步规划？工具链路调度与 fallback 怎么设计？
quick: 规划器产出步骤/子目标，执行器按状态机调用工具；每步有输入输出契约、超时重试、幂等与降级。fallback：换工具、缩任务、澄清用户、转人工。
tags:
  - Alibaba
  - Agent
  - Harness
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

陷阱是把 Modular Agent 答成「再套一层 ReAct，让模型自己想下一步」。工业界要落到控制面：规划器产出步骤 / 子目标，执行器按状态机调工具；每步有输入输出契约、超时重试、幂等与降级。fallback 是换工具、缩任务、澄清用户、转人工，而不是再让模型「灵活一下」。延迟侧的串并行见 `ali-latency-3tools`，何时推翻计划见 `agent-when-to-replan`。

## 规划器与执行器拆开

规划：Plan-and-Execute 先出子目标再执行；ReAct 逐步交错。关键业务（退款、改地址、支付）用确定性工作流包住 LLM 规划——模型负责理解与填槽，状态转移写在编排里。调度要有工具白名单、并行 / 串行依赖、参数 schema 校验。没有契约的「自由规划」在淘天客服里会变成重复下单或跳过确认。单次打分不是 Agent，差别在控制回路，见 `ali-score-vs-agent`。

模块化的好处是可替换：换模型不必重写工具层，换物流供应商不必重训规划器。代价是接口要稳：每步声明预期观测，执行器只认合法输出，脏数据不得直接回灌成下一步指令。

## 每步契约：超时、幂等、降级

每一步写清输入 schema、输出 schema、超时、可重试次数、是否幂等。瞬时网络错误可重试；逻辑错误（订单不存在、政策不匹配）换策略，不要换参数死循环。写工具必须带幂等键，防止超时后重复扣款。可观测要有 trace、tool 指纹、重复调用检测，防死循环。预算（步数、金额、延迟）超限必须终止，而不是「再试一次」。

## fallback 要分级

瞬时错误 → 重试；工具不可用 → 换等价工具或缓存；任务过大 → 缩成可完成的子目标并澄清用户；高风险或连续失败 → Human-in-the-loop。不可逆动作的确认在代码层强制，见 `ali-hitl-risk`、`ali-guardrail`。fallback 不是把失败藏进一句「稍后再试」，而是改变状态并留下审计。

## 追问

- **为何不全用 ReAct？** 每步思考贵、尾延迟叠 prefill，且难保证幂等与权限。关键路径用工作流包住更稳。
- **规划错了怎么办？** 用观测与预期的偏差触发局部重规划，不要每步全局推倒。见 `agent-when-to-replan`。
- **如何防死循环？** 同指纹调用计数、步数上限、重复错误熔断，这些必须在执行器而不是 prompt。
- **模块化如何验收？** 冻结工具测换模型，冻结模型测换工具；只报端到端成功率会把 harness 改进算成模型变强。
