---
id: byte-harness-engineering
section: agent
order: 200
level: S
title: 字节 Agent 实习一面：什么是 Harness Engineering？和只调 LLM API 差在哪？
quick: "Harness 管模型之外的上下文组装、权限、工具执行、状态、日志、校验和重试。调用 LLM API 只拿到模型输出，还要由 Harness 检查并执行动作、验证结果、处理失败，复杂任务才跑得完。"
tags:
  - ByteDance
  - Harness
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节跳动-Agent开发实习生 一面（45分钟）
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/075c06bf50a143a785c039f9951624f6
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“什么是Harness Engineering”**；**“Harness的五个核心模块”**；**“你对 Agent Harness 怎么理解？它和单纯调用 LLM API 的区别是什么？”**

Harness Engineering 做的是模型之外的那一圈：上下文怎么组装、计划怎么约束、工具怎么受控执行、记忆怎么写、日志和失败怎么处理。只调 LLM API，拿到的只是一段意图文本；复杂任务能跑完，是因为 Harness 把每一步约束住、让它可观测、失败能回放。同一份权重，换一套工具错误码和重试策略，成功率能差一截，所以测的是 model + harness，「模型更会聊天」说明不了什么。把 Harness 讲成「更好的 system prompt」或者「SDK 再包一层 chat API」都不到位。概念总览见 `agent-harness`。

举个 Coding Agent 的例子。一套是「只有 shell」，另一套是「repo 检索 + 测试 + patch 回滚 + 结构化状态」，模型一样，这是两套完全不同的 Harness。在后一套里，模型输出一条工具调用文本，Harness 校验参数、查 ACL、在沙箱里执行，再把结构化的 Observation 写回去；模型说「删文件」，不等于真删了。

「五个核心模块」的划法不唯一，我不背五个英文词，只讲清覆盖了哪些模型外的职责。先是感知和上下文组装，当前任务、仓库切片、工具观察、权限可见范围，决定窗口里放什么。然后是规划，把目标拆成能验证的子步骤，规划本身还是模型做，但步数、什么时候终止、允不允许改计划，由 Harness 卡死。再是受控的工具执行，解析 schema、鉴权、沙箱、超时和幂等保护。还有记忆，短记忆服务本轮，长记忆跨会话，写入要带来源和失效条件，见 `byte-short-long-memory`。最后是观测和策略，日志、trace、超时、重试、审批，失败按错误码分类处理，一律再问一遍模型没用，见 `byte-tool-fail-retry`。权限和审计是执行层的一部分，光写在 prompt 里当补充说明不够，见 `byte-team-agent-security`。

再说和只调 API 的差别。只调 API，没有权限边界，没有确定性回放，失败了只能重问。Harness 决定能不能跑、跑在哪、结果怎么验；没有 executor，所谓 Agent 只是多轮聊天。可回放的要求是同一输入、同一工具版本、同一工作区快照，得到同一张执行图，这要靠工具副作用可记录、观察规范化，温度调到 0 做不到。预算与终止条件，也就是最大步数、token 用量和实际耗时，也必须放在环外管，不然模型会把「再试一次」写成无限循环。

最后是规格。规格、单测、禁止改的路径，是判断「这一步对不对」的预言机，要落成能跑的校验器，写成又一段 prompt 起不到这个作用。Harness 负责跑测试、比 diff，失败时按策略重试或升级。Spec 解决可判定，Harness 解决判定之后谁执行，两者怎么配合见 `byte-spec-sdd-openspec`。没有规格时 Agent 只能靠观感，只调 API 也做不了长任务。

## 追问

**五个模块必须是哪五个？**
不用背死。能讲清上下文、规划约束、受控执行、记忆、观测恢复，并指出权限和评测落在哪一层就行。

**换模型为什么成绩差很多？**
工具 schema、错误文案、Observation 格式一变，就等于策略分布偏移了。训练要锁定 harness 版本，并做 cross-harness 对照。

**Harness 和 Skills 什么关系？**
Skill 是按需展开的程序化知识，Harness 决定什么时候加载、怎么隔离不可信输出。仓库里写了 Skill，不等于已经有了执行和权限系统。

**最小可上线集是什么？**
解析器、鉴权沙箱、步数预算、结构化日志、失败分类。缺了这几项，演示能跑，到了生产就会把副作用写进真实环境。
