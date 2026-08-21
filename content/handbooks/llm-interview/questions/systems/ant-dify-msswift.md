---
id: ant-dify-msswift
section: systems
order: 181
level: B
title: 蚂蚁智能体优化一面：Dify 和 ms-swift 各解决什么问题？
quick: >-
  Dify 是应用编排（工作流、知识库、Agent 可视化），偏上线与运营。ms-swift
  是训练 / 微调 / 评测工具链（SFT、LoRA、RLHF 等），偏改权重。面试各给一句边界，不要把二者说成同一个平台。
tags:
  - Ant Group
  - Dify
  - ms-swift
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 20260508蚂蚁集团大模型智能体优化算法一二面
    url: https://www.nowcoder.com/feed/main/detail/263bc804663b4a0aa7b312154d720817
    type: candidate-first-hand
  - title: Dify
    url: https://github.com/langgenius/dify
    type: primary
  - title: ms-swift
    url: https://github.com/modelscope/ms-swift
    type: primary
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型智能体优化算法
- 届别 / 流程：一面
- 面试时间：2026-05-08（帖题）
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“介绍Dify平台”**；**“介绍Ms-swift平台”**

蚂蚁智能体优化一面这题，最容易把 Dify 和 ms-swift 说成「都是大模型平台」或展开成产品广告。面试要听边界：一个管编排与上线，一个管改权重；交接物是 checkpoint / 推理服务，而不是把训练框架嵌进工作流画布。各给一句输入输出，再落到你项目里用了哪一层。智能体优化岗两者都可能碰到：线上改路由走 Dify，领域话术不够走 swift，不要用其中一个覆盖另一个的职责。

## Dify：编排应用，不改基座

Dify 把 prompt、知识库、工具和工作流配成可发布应用，适合「不改基座、先跑通业务」。输入是文档 / API / 工作流 DSL，输出是可观测的应用与会话。强项是可视化编排、知识库接入和运营侧的日志；弱项是不能替代检索质量、工具鉴权和评测设计。Agent 节点仍要你自己定义 schema、超时和失败策略。把它当「低代码 LangGraph」来讲边界即可，不要背功能清单。相关卡：`meituan-langgraph-vs-prompt`、`ant-skills-vs-harness`。

## ms-swift：改权重的训练工具链

ms-swift 是 ModelScope 侧的轻量训练框架，把数据格式、LoRA / 全参、多卡、部分 SFT / RLHF / GRPO 收成命令行与配置。输入是数据集与模型，输出是 checkpoint 和评测指标。强项是把常见微调路径跑通；弱项是不管你的线上工作流、权限和知识库。蚂蚁问它，是因为智能体优化经常要 LoRA 改工具格式或领域话术，而不是因为要用它替代 Dify。训练并行、ZeRO 细节若追问，转到 `baichuan-deepspeed`，不要在这题里展开内核。

## 二者如何交接

swift 产出可部署权重 → 推理服务（vLLM 等）→ Dify 只引用 endpoint 与 prompt / 工具配置。版本要钉死：哪个 checkpoint、哪套模板、哪版工具 schema。不要在 Dify 里「再训一版」，也不要指望 swift 给你会话记忆。评测也不要混：swift 侧看 SFT/RL 指标，Dify 侧看工作流完成率、检索命中和工具失败码。面试收口：Dify 解决怎么把模型用起来；ms-swift 解决怎么把模型改得更听话；中间隔着推理网关。

## 追问

- **只用 Dify 能不能优化智能体？** 能优化编排和检索，改不了权重；格式和领域能力不够时仍要微调。
- **ms-swift 和 Megatron / veRL 什么关系？** swift 偏中小规模微调；大规模预训练或 RL 编排常换 Megatron / veRL。
- **知识库该放哪？** 索引与 ACL 在检索系统；Dify 是接入层。质量问题不在画布上解决。
- **如何避免两套 prompt？** 训练模板与 Dify 应用模板同一版本库，推理侧做一致性检查。上线 checklist 里要把「swift 产出的 chat template」和「Dify 系统提示」对拍一次。
