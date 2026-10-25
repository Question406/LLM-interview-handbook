---
id: xiaohongshu-agentic-rl-diff
section: agentrl
order: 120
level: S
title: 小红书：Agentic RL 与普通 RL 最大的不同是什么？
quick: "普通 LLM 强化学习（RL）通常针对单轮生成，用最终奖励优化 token 序列；Agentic RL 优化的是模型通过工具和环境交互的多步轨迹，动作带副作用，环境会被改变。难点随之变成分清各步贡献、部分可观测、工具失败、延迟很久才出现的奖励，以及不可逆的探索。"
tags:
  - Xiaohongshu
  - Agentic RL
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4
    type: candidate-first-hand
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“agentic RL 和普通的 RL 比最大的不同在哪里？”**

如果「普通 RL」指现在常见的 LLM outcome RL，也就是对一条 completion 给一个最终分，那最大的不同在于状态和动作的定义变了：动作从生成 token 扩展到带副作用的工具调用，状态也从文本前缀变成了会被这些动作改变的环境。所以给 chatbot 加几个 function call 再跑 GRPO，还不能叫 Agentic 强化学习（RL）。小红书这一面要听的是环境转移和轨迹级优化。

举个例子，数学题的世界是表达式，换一道题面就和上一道独立了；Agent 的世界会留下订单和权限，这一步发了帖、做了审核处置，下一步面对的就是被改过的环境。

定义上的变化有这几处。动作空间里除了 token，还有工具调用和发帖、审核处置、支付这类不可逆的副作用，动作的边界是 tool-call，句号不算。观测来自工具返回、UI、数据库，带噪声、有延迟、部分可观测，必须依赖历史和 memory，$s_t$ 不再是 输入提示（prompt） 全文。奖励常常稀疏而且滞后，没有过程奖励或可验证子目标，长轨迹就没法做 credit assignment，见 `arl-credit`。探索时错误动作不可回滚，只能在沙箱和权限门里进行，见 `arl-sparse-reward-exploration`。评测光看 BLEU 或单轮正确率也不够，要看任务成功、步数、违规和恢复，见 `arl-eval`。策略骨架可以是 ReAct 的 Thought → Action → Observation，但训练要对齐日志的 字段和类型规范（schema） 和可回放的环境，见 `stepfun-react-io-blocks`。没有环境转移，就还是文本 RL。

落到算法上，普通 LLM RL 的方差已经不小，Agent 还要把一个滞后的 $R$ 分到几十步工具上，还要处理工具版本和页面漂移。On-policy 假设 $p(s_0)$ 固定，环境不重置时这个假设就不成立，见 `arl-environment-reset`；旧轨迹里的网页可能已经变了，不能当成当前策略的梯度数据，见 `arl-offpolicy-reuse`。所以 Agentic RL 的难，一半在算法，一半在环境工程，reset 和 checkpoint 都成了算法假设，这正是它和数学 outcome RL 的分界。同一面问到的 credit 见 `xiaohongshu-credit-assignment`。

## 追问

**有 function calling 就算 Agentic RL 吗？**
不算。关键是环境转移和轨迹级优化。单轮选一个 tool 再生成答案，仍然更接近文本 RL。

**和传统控制里的 RL 比呢？**
公式是同一类的，但动作是语言加工具，观测是文本或多模态，转移通常不可微、不可逆，工程上的假设更脆。

**为什么 credit 更难？**
终局的 $0/1$ 要分到多步、多人、多次通信上，见 `xiaohongshu-credit-assignment`、`arl-multi-credit`。过程奖励和 GiGPO 怎么选，见 `arl-process-vs-gigpo`。

**评测为什么不能沿用单轮的？**
单轮正确率看不见越权、空转和不可恢复的失败，必须报轨迹质量和安全。
