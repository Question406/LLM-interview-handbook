---
id: jd-agent-reflection-error-attribution
section: agent
order: 101
level: S
title: 京东大模型：Reflection 如何归因知识缺失还是工具调用错误？
quick: "先记录可回放轨迹，把失败拆成知识与检索、工具选择、参数、执行、结果使用和规划问题。然后替换成标准证据或正确工具结果，重放执行器，观察哪项替换消除了失败。归因应指向具体修复，不能只让同一个模型自评。"
tags:
  - JD
  - Agent
  - Reflection
  - Error Attribution
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 秋招面经-京东大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/3f02a8e652fa414c819de810452a2b2a
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Reflection机制里,如何判断一个Agent的失败是由知识缺失还是工具调用错误引起的?”**

常见误区是：让同一个 LLM 再写一段「我这次是缺知识还是调错工具」。自评没有反事实，高置信不等于对。京东这面要先有可回放 trace，再做受控替换：换金标证据、换金标工具结果、replay 执行器，看失败在哪一环消失。归因必须指向不同修复路径，统一「再反思一次」会修错模块。评测为什么不能只看 QA，见 `jd-agent-eval-beyond-qa`。

## 先要 trace，再做替换实验

轨迹至少记录任务、检索证据、候选工具、选中的工具及参数、执行器响应、状态快照和最终答案。缺少这些信息，就很难可靠归因。

对同一 state 做替换：

- 提供标准证据或正确检索结果后成功 → 知识覆盖或检索有因（文档没有、切块丢了、召回没中）。
- 固定使用正确工具结果后仍失败 → 更像 planning / 不会用观察，工具本身多半没问题。
- 字段和类型规范（schema） 校验失败、argument 一改就过、或 executor replay 失败 → 归调用链：选错工具、填错参、执行器/权限/超时。

「知识缺失」要再拆：参数里没有、索引里没有、检索没召回、召回了但没放进窗口。后三者常被误叫成模型不懂。工具错误也要拆：选错、填错、执行失败、观察没用上。混成两个大标签会修错模块。

## 归因是多标签，带置信度

一次失败经常有主因和辅因：检索漏了关键 SOP，同时参数把订单号填错。报告 primary cause、contributing cause 和置信度。高置信来自替换实验；只有模型自述时标低置信，不能直接改线上。

我会建可重放的 failure set，按错误类型分别统计回归。工具目录或文档更新后要重跑，避免归因绑在过期 schema 上。Reflection 模块若用于训练信号，必须用这些桶，别用「反思文本像不像人」。

## 修复路径随桶变化

- 知识 / 检索：补数据、改切块、改召回，别加更长的「请仔细想」。
- 选错工具：改 description、路由、权限可见集，或 监督微调（SFT） 示范，见 `jd-agent-tool-catalog-context`。
- 参数错误：schema、constrained decoding、参数校验器。
- 环境失败：retry、幂等、超时策略，见 `byte-tool-fail-retry`。
- 规划不用观察：改提示或训练，让 Observation 成为下一跳的强制输入。

不要统一「反思一次再试」：缺文档的任务再试仍缺；403 再试是噪声。训练把错误调用写进 SFT/RL 时要对齐桶，见 `ali-tool-call-error-sft-rl`。

## 追问

- **能不能只用 LLM-as-judge？** 可以当弱信号，不能当主归因。没有替换实验，judge 会把文笔流畅当成根因正确。
- **知识缺失和幻觉怎么分？** 索引里确无证据且模型仍给出具体数字，是幻觉/捏造；索引有但没召回，是检索失败。二者修复不同。
- **工具返回是错的算谁的？** 先 replay 执行器。环境 bug 归基础设施；模型在错误观察上编造结论，归 工具结果的使用。
- **多 Agent 时怎么归因？** 先定位是哪个 Agent 的哪次 proposal，再用同一套替换；不要让它们互相写检讨，见 `byte-multiagent-policy-conflict-recovery`。
