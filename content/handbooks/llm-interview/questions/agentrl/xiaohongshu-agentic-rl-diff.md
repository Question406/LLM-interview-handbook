---
id: xiaohongshu-agentic-rl-diff
section: agentrl
order: 120
level: S
title: 小红书：Agentic RL 与普通 RL 最大的不同是什么？
quick: >-
  普通 LLM RL 多在单轮生成上优化最终 token 序列奖励；Agentic RL
  是环境交互轨迹（工具、状态、多步），信用分配、部分可观测、工具失败与长程延迟是核心难点。
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

若「普通 RL」指当前常见的 LLM outcome RL（对一条 completion 给最终分），最大不同不是「多了几个 function call」，而是状态与动作不再只是文本前缀和下一个 token，而是带副作用的环境交互。这块容易直接答成把「给 chatbot 加了工具再跑 GRPO」直接叫 Agentic RL。小红书这面要听环境转移与轨迹级优化。同面 credit 见 `xiaohongshu-credit-assignment`。

## 状态、动作、奖励都换了定义

可以压成五条，面试按条讲：

1. **动作空间：** 除了生成 token，还包括工具调用与不可逆副作用（发帖、审核处置、支付）。动作边界是 tool-call，不是句号。
2. **观测：** 工具返回、UI、数据库有噪声、延迟和部分可观测，必须依赖历史与 memory。$s_t$ 不是 prompt 全文。
3. **奖励：** 常稀疏且滞后，需要过程奖励或可验证子目标，否则长轨迹无法 credit assignment，见 `arl-credit`。
4. **安全 / 探索：** 错误动作不可回滚，探索必须在沙箱和权限门内，见 `arl-sparse-reward-exploration`。
5. **评测：** 不能只看 BLEU 或单轮正确率，要看任务成功、步数、违规与恢复，见 `arl-eval`。

策略骨架可以是 ReAct：Thought → Action → Observation，但训练必须对齐日志 schema 与可回放环境，见 `stepfun-react-io-blocks`。没有环境转移，就还是文本 RL。

## 算法后果：信用、非平稳、off-policy

普通 LLM RL 的方差已经不小；Agent 还要把一个滞后 $R$ 分到几十步工具上，还要处理工具版本和页面漂移。On-policy 假设 $p(s_0)$ 固定，环境不 reset 就破，见 `arl-environment-reset`。旧轨迹的网页可能已经变了，不能当当前策略梯度，见 `arl-offpolicy-reuse`。所以 Agentic RL 的「难」一半在算法、一半在环境工程。这正是和数学 outcome RL 的分界。数学题的世界是表达式，换一条题面就独立；Agent 的世界会留下订单和权限，reset 与 checkpoint 都成为算法假设。

最后我会补一句：普通 LLM RL 优化单轮 token 序列；Agentic RL 优化带副作用的交互轨迹。核心难点是部分可观测、稀疏滞后奖励、不可逆探索和可回放环境，而不是多包一层 function calling。

## 追问

- **有 function calling 就是 Agentic RL 吗？** 不是。关键是环境转移与轨迹级优化。单轮选一个 tool 再生成答案，仍更接近文本 RL。
- **和传统控制 RL？** 公式同类，但动作是语言 + 工具，观测是文本 / 多模态，转移常不可微、不可逆。工程假设更脆。
- **为什么 credit 更难？** 终局 $0/1$ 要分到多步、多人、多次通信。见 `xiaohongshu-credit-assignment`、`arl-multi-credit`。过程奖励和 GiGPO 怎么选，见 `arl-process-vs-gigpo`。
- **评测为什么不能沿用单轮？** 单轮正确率看不见越权、空转和不可恢复失败。必须报轨迹质量与安全。
