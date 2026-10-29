---
id: xiaohongshu-agent-business-eval
section: agent
order: 124
level: A
title: 小红书：如何面向业务设计并评估 Agent？
quick: >-
  面向业务先写清什么叫成功，比如违规识别准、依据可解释、标准变了能跟上、误伤能申诉，再反推工具、权限、记忆和人审节点。评估分任务、过程、成本与
  SLA、对齐四层，看误伤、漏放、时延成本和可复现的 trace，别拿对话流畅度当分数。路径几乎固定时，退回 Workflow 更稳。
tags:
  - Xiaohongshu
  - Agent
  - Evaluation
  - Trust and Safety
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书 大模型后训练一面
    url: 'https://www.nowcoder.com/discuss/872533899736334336'
    type: candidate-first-hand
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：NLP / 多模态 / 大模型实习生；社区生态治理 Agent
- 届别 / 流程：实习；一面
- 面试时间：2026-04-08 19:00
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如何看待 Agent，怎么面向业务设计、评估 Agent？”**

我看 Agent，先看「做成什么样算成功」，再决定要不要动态决策。社区生态治理这类业务，成功可能是准确识别违规、给出可解释的依据、支持标准变更，并且误伤可以申诉。用开放域 chatbot 的流畅度来评治理 Agent，评的就不是业务要的东西。路径完全固定时，Workflow 更合适，见 `meituan-workflow-vs-agent`。

举个场景：社区规范新增了一条针对某类笔记的条款。如果尺度写死在 prompt 里的形容词上，就得改代码、重新上线，也说不清哪些旧判定要重审；如果条款是版本化的 Skill，改一个版本，跑一遍回归桶，再灰度，trace 里能看到每次判定用的是哪一版政策。原帖反问里强调的价值观公约数和审核标准自适应，落下来就是把政策当成可版本化的数据。

成功定义写清之后，再反推工具和权限。工具包括检索社区规范、相似案例、多模态审核信号和升级人审。权限默认只读，处置动作必须审批。记忆只保留可引用的案例句柄和政策版本，用户隐私不写进长期层。Agent 的价值是规范更新时少改死代码、多改可版本化的 Skill，见 `xiaohongshu-mcp-skill-token-efficiency`。设计时把人审节点显式画出来：哪些类型自动处理，哪些必须给人，申诉怎么加入 evaluation set。没有将 appeals 纳入后续数据，误伤只会在线上累积。

评估分四层。任务层看精确率和召回，按违规类型切片，包括标准变更后的回归。过程层看该调用的工具有没有调、证据能不能追溯。成本与 SLA 看步数、时延和人审占用。对齐层处理网信办、用户、公众、运营之间的约束冲突，以成文政策为准，例外记录下来；价值观公约数也落在成文政策上，别让模型现场发明尺度。hallucination 和漏检要分开计，见 `xiaohongshu-hallucination-prompt`；「小编觉得通顺」代替不了切片指标。trace 必须可复现，政策版本、检索快照、模型 release 放进同一个 manifest，见 `pdd-prompt-template-versioning-rollback`。

政策是数据，Skill 是载体。审核标准会变，把条文、案例、阈值做成版本化的 Skill 或配置，路由时只加载相关条目，避免把全站 SOP 塞进 system prompt。标准变更后先跑回归桶，再灰度。Agent 要在政策更新时仍然可审计、可回滚，追求「更像人审」没有意义。如果评估发现路径几乎不变，就降级回 Workflow，把模型留给 edge cases。所以「面向业务」我会说成可申诉、可切片、可版本化，「Agent 更智能」这种话不用说。

## 追问

**为什么不能用 chatbot 的分数？**
治理要的是误伤、漏放和可申诉，会不会闲聊无关紧要。

**人审算不算 Agent 失败？**
不算。人审是权限设计，要看该升级的有没有升、不该升的有没有占满人力。

**标准变了怎么评？**
旧集做回归，新集做适配，政策版本写进 trace，不能混在一个总分里。

**什么时候不该上 Agent？**
路径固定、工具无副作用、不需要探索的时候，用 Workflow 更稳。
