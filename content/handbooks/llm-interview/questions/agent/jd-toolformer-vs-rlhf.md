---
id: jd-toolformer-vs-rlhf
section: agent
order: 102
level: S
title: 京东大模型：Toolformer 自监督 tool-call 数据与 RLHF 有何不同，为什么可能更泛化？
quick: "Toolformer 让模型自己插入候选 API 调用并执行，只保留能降低后文 token 损失的调用，当作自监督示范来训练；RLHF 用偏好或奖励直接优化整条策略。Toolformer 不靠人工偏好标签，能从大量未标注文本覆盖更多调用模式，这是「可能更泛化」的来源。对新工具、新权限仍要在 held-out 工具和任务上测，自监督本身给不了保证。"
tags:
  - JD
  - Toolformer
  - Tool Use
  - RLHF
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 秋招面经-京东大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/3f02a8e652fa414c819de810452a2b2a
    type: candidate-first-hand
  - title: 'Toolformer: Language Models Can Teach Themselves to Use Tools'
    url: https://arxiv.org/abs/2302.04761
    type: primary-paper
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Toolformer中通过自监督学习生成tool call数据,这个训练范式和RLHF的差别在哪里?为什么它更容易泛化?”**

两者的差别在监督信号从哪来。Toolformer 用语言模型自己当过滤器造伪标注：插入调用、执行、看它对后文预测有没有帮助，有帮助的留下来做模仿学习；基于人类反馈的强化学习（RLHF）用偏好或环境奖励直接优化整条策略。说 Toolformer「更容易泛化」，意思是它不依赖狭窄的人工偏好，能从开放文本里覆盖更多 API 使用模式；对新工具、新权限语义，它没有保证，这一点算不上定理，面试里要补一句 held-out 工具和任务的测试。

举个例子，一段文本前面给了件数和单价，后面接着「总价是……」。Toolformer 会在这里试着插一个计算器调用，执行拿到结果，再看把结果写进去之后，后面那串 token 的损失有没有下降，降了就把这条调用留下来当训练数据。

Toolformer（Schick et al., arXiv:2302.04761）的完整流程是：在自然语言的位置插入候选 API 调用，执行得到观测结果（observation），再看这段调用是否降低了后续文本处理单位（token）的损失。只有能改善语言建模、也就是下文预测的调用才被保留，插回文本当训练数据，然后训练模型模仿这些调用。它不要求每条都有人类偏好标签或线上奖励分数（reward），所以能吃更广的未标注文本和 API 文档，学会什么时候调用、怎么把 observation 写回上下文。

它的局限也来自这个目标。目标函数是下一词似然，跟任务成功没有直接关系，过滤器问的是「这次调用对把句子说完有没有帮助」，管不到「最终有没有下对单」。所以它擅长补计算器、日历、检索这类能立刻改善局部文本的工具；需要多步、有副作用、要权衡成本的策略，信号就偏弱。数据是自监督伪标注，噪声来自过滤器本身，能降低 perplexity 的调用不一定是用户想要的动作。

RLHF 和后来的基于可验证奖励的强化学习（RLVR）直接优化人的偏好、规则或环境给出的标量，适合处理整条回答或动作序列里的权衡，比如最终成功、延迟、安全和成本。它依赖奖励定义和采样到的轨迹分布：偏好数据贵，容易过拟合标注员的口味；模型还会钻奖励规则的空子，学会讨好评分，工具却没用对。和 Toolformer 比，RLHF 不造「何时调用」的监督文本，它改的是整条策略的采样分布。

泛化要靠实验来证明。新工具的字段和类型规范（schema）、权限或环境动态一变，两种范式都要在 held-out tools / tasks 上测：Toolformer 对新 API 仍要能采样出合法调用，并让过滤器看到下文增益；RLHF 则要 reward 覆盖新的失败模式。工具调用里监督微调（SFT）和强化学习（RL）怎么分工，见 `ali-tool-call-error-sft-rl`，格式和基本调用可以靠 imitation，对错与重试更适合带环境的 RL。生产 Agent 的 tool schema 和权限是另一层，见 `agent-tool-call`，训练范式解决不了越权。

## 追问

**过滤器只看 perplexity，会留下什么坏样本？**
能让下文更流畅、却调用了不该用的工具，或者编出看起来合理的 observation。要再用 schema 校验和执行成功加一层硬过滤。

**两者能不能叠用？**
可以。Toolformer 式的伪标注做 SFT 打底，再用 RLHF / RLVR 优化成功率和安全，回答时说清各管哪一段损失。

**泛化怎么实证？**
留出没见过的工具名或参数格式，看调用是否仍然合法、对任务有没有用。「自监督」三个字推不出保证。

**和 Function Calling 的 SFT 有什么不同？**
普通 SFT 依赖人工或蒸馏的轨迹；Toolformer 的监督来自「调用有没有改善 LM loss」，规模可以更大，但它的目标不是任务 reward。
