---
id: ant-dify-msswift
section: systems
order: 181
level: B
title: 蚂蚁智能体优化一面：Dify 和 ms-swift 各解决什么问题？
quick: >-
  Dify 管应用编排，把工作流、知识库、Agent 可视化地配成可上线的应用，偏上线和运营。ms-swift 管训练、微调和评测，SFT、LoRA、RLHF
  这些，偏改权重。面试各说明各自职责、再说中间怎么交接就够了。
tags:
  - Ant Group
  - Dify
  - ms-swift
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 20260508蚂蚁集团大模型智能体优化算法一二面
    url: 'https://www.nowcoder.com/feed/main/detail/263bc804663b4a0aa7b312154d720817'
    type: candidate-first-hand
  - title: Dify
    url: 'https://github.com/langgenius/dify'
    type: primary
  - title: ms-swift
    url: 'https://github.com/modelscope/ms-swift'
    type: primary
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型智能体优化算法
- 届别 / 流程：一面
- 面试时间：2026-05-08（帖题）
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“介绍 Dify 平台”**；**“介绍 Ms-swift 平台”**

Dify 解决怎么把模型用起来，ms-swift 解决怎么把模型改得更听话：一个管编排和上线，一个管改权重，中间隔着推理网关，交接物是 checkpoint 和推理服务。说成「都是大模型平台」或者展开成产品介绍，都没答到点上。各给一句输入输出，再讲项目里用的是哪一层就行。

智能体优化岗两个都可能碰到。比如线上发现 Agent 路由不对，改工作流就在 Dify 里做；发现模型的领域话术或工具调用格式不够好，就得用 swift 去微调。两边职责别互相覆盖。

Dify 把 prompt、知识库、工具和工作流配成可以发布的应用，适合「不改基座，先把业务跑通」。输入是文档、API 和工作流 DSL，输出是可观测的应用和会话。它的强项是可视化编排、知识库接入和运营侧的日志；检索质量、工具鉴权和评测设计它替代不了，Agent 节点的 schema、超时和失败策略也还得自己定义。把它当成「低代码 LangGraph」来讲 division of responsibilities 就够了，别背功能清单，相关的可以看 `meituan-langgraph-vs-prompt`、`ant-skills-vs-harness`。

ms-swift 是 ModelScope 那边的轻量训练框架，把数据格式、LoRA 和全参、多卡、部分 SFT/ RLHF/ GRPO 收成命令行和配置。输入是数据集和模型，输出是 checkpoint 和评测指标。强项是把常见的微调路径跑通；线上工作流、权限和知识库它不管。蚂蚁问它，是因为智能体优化经常要用 LoRA 改工具格式或领域话术，没打算拿它替代 Dify。如果追问训练并行、ZeRO 细节，转到 `baichuan-deepspeed`，这题里别展开内核。

两者的交接是这样的：swift 产出可部署的权重 → 推理服务（vLLM 等）→ Dify 只引用 endpoint 和 prompt、工具配置。版本要钉住：哪个 checkpoint、哪套模板、哪版工具 schema。别在 Dify 里「再训一版」，也别指望 swift 给你会话记忆。评测也分开看：swift 这边看 SFT/RL 指标，Dify 这边看工作流完成率、检索命中和工具失败码。

## 追问

**只用 Dify 能不能优化智能体？**
能优化编排和检索，改不了权重；格式和领域能力不够时还是要微调。

**ms-swift 和 Megatron、veRL 什么关系？**
swift 偏中小规模微调；大规模预训练或者 RL 编排，常换成 Megatron / veRL。

**知识库该放在哪一层？**
索引和 ACL 在检索系统里，Dify 只是接入层。检索质量的问题在画布上解决不了。

**怎么避免出现两套 prompt？**
训练模板和 Dify 应用模板放在同一个版本库，推理侧做一致性检查。上线 checklist 里要把 swift 产出的 chat template 和 Dify 的系统提示对拍一次。
