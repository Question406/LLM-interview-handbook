---
id: xiaohongshu-agent-business-eval
section: agent
order: 124
level: A
title: 小红书：如何面向业务设计并评估 Agent？
quick: >-
  先写清业务成功定义（审核通过、治理覆盖、用户可申诉），再反推工具、权限、记忆和人审节点。评估用任务成功、误伤、漏放、时延成本和可复现 trace，而不是只看对话是否流畅。
tags:
  - Xiaohongshu
  - Agent
  - Evaluation
  - Trust and Safety
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 小红书 大模型后训练一面
    url: https://www.nowcoder.com/discuss/872533899736334336
    type: candidate-first-hand
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：NLP / 多模态 / 大模型实习生；社区生态治理 Agent
- 届别 / 流程：实习；一面
- 面试时间：2026-04-08 19:00
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如何看待Agent，怎么面向业务设计、评估Agent？”**

陷阱是用开放域 chatbot 的流畅度来评社区治理 Agent。面向业务先固定「做成什么样算成功」，再决定要不要动态决策。治理场景的成功可能是准确识别违规、给出可解释依据、支持标准变更，并且误伤可申诉。路径完全固定时 Workflow 更合适，见 `meituan-workflow-vs-agent`。原帖反问里强调价值观公约数和审核标准自适应——把政策当成可版本化数据，而不是写死在 prompt 里的形容词。

## 先写成功定义，再反推工具和权限

工具应包括检索社区规范、相似案例、多模态审核信号和升级人审。权限默认只读，处置动作必须审批。记忆只保留可引用的案例句柄和政策版本，不把用户隐私写进长期层。Agent 的价值是在规范更新时少改死代码、多改可版本化 Skill，见 `xiaohongshu-mcp-skill-token-efficiency`。设计时显式画出人审节点：哪些类型自动、哪些必须人、申诉如何回流到评测集。没有申诉回流，误伤只会在线上累积。

## 评估分四层，不要只看对话

1. **任务**：精确率 / 召回按违规类型切片，含标准变更后的回归。
2. **过程**：该调用的工具有没有调、证据是否可追溯。
3. **成本与 SLA**：步数、时延、人审占用。
4. **对齐**：网信办 / 用户 / 公众 / 运营的约束冲突时，以成文政策为准并记录例外。

trace 必须可复现：政策版本、检索快照、模型 release 进同一 manifest，见 `pdd-prompt-template-versioning-rollback`。幻觉和漏检要分开计，见 `xiaohongshu-hallucination-prompt`。不要用「小编觉得通顺」代替切片指标。

## 政策是数据，Skill 是载体

审核标准会变。把条文、案例、阈值做成版本化 Skill / 配置，路由时只加载相关条目，避免把全站 SOP 塞进 system prompt。标准变更后先跑回归桶，再灰度。Agent 不是为了「更像人审」，而是为了在政策更新时仍可审计、可回滚。若评估发现路径几乎不变，就应降级回 Workflow，把模型留给边界 case。小红书这面要把「面向业务」说成可申诉、可切片、可版本化，而不是「Agent 更智能」。价值观公约数落在成文政策上，例外写进日志，不要靠模型现场发明尺度。

## 追问

- **为什么不能用 chatbot 分？** 治理要的是误伤、漏放和可申诉，不是会不会闲聊。
- **人审算不算 Agent 失败？** 不算。人审是权限设计；要看该升级的有没有升、不该升的有没有占满人力。
- **标准变了怎么评？** 旧集做回归、新集做适配，政策版本写进 trace，不能混在一个总分里。
- **什么时候不该上 Agent？** 路径固定、工具无副作用、不需要探索时，用 Workflow 更稳。
