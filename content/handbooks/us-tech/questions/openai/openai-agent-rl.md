---
id: openai-agent-rl
section: openai
order: 30
level: S
title: OpenAI：工具循环上的 RL，轨迹、credit、环境重置，和 token 级 PPO 差在哪
quick: >-
  Token 级 PPO 的动作是下一个词，状态是前缀；工具 RL 的动作是一整段调用，状态含环境观察，奖励常在回合结束才到。只对模型自己吐的
  token 记 $\log\pi$，观察要 mask。Credit 用 GAE 沿整条轨迹回传；环境必须重置，否则上回合的文件和 cookie 会漏奖。
tags:
  - OpenAI
  - RL
  - Agents
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: WebGPT — Browser-assisted question-answering with human feedback
    url: https://arxiv.org/abs/2112.09332
    type: primary
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
---

## 题怎么来的

InstructGPT 的 PPO 是对着一段 completion 优化 RM，动作粒度是 token。WebGPT 已经把同一套 BC → RM → PPO 接到文本浏览器上：搜索、点击、引用，回合结束才打分。现在的工具循环更长、观察更脏。对齐岗会问：轨迹怎么存、梯度打在谁身上、环境怎么重置。Clip 和 KL 锚见 `openai-ppo-clip`、`openai-instructgpt-kl`。运行时怎么塞观察见 `openai-tool-loop`，本题只收训练。

不编未公开的内部 agent 算法。公开对照就是 InstructGPT + WebGPT。

## 两条 MDP，别用同一个 $a_t$

**Token 级 PPO（InstructGPT）。** 状态 $s_t=x\circ y_{1:t-1}$（prompt 加已写前缀），动作 $a_t$ 是词表里一个 token。奖励通常在 EOS 才有 $r_\phi(x,y)$，中间步 0，再减 token KL。GAE 把终局优势回传到每个 token。On-policy 数据是「同一 prompt 下的一条文本」。

**工具循环 RL。** 回合是

$$
\tau=(s_0,a_0,o_1,a_1,o_2,\ldots,a_{K-1},o_K,y).
$$

$a_k$ 是模型一次输出：自然语言、或一次 / 一组 `tool_calls`。$o_{k+1}$ 是宿主执行后的观察（JSON、网页、报错），不是 $\pi_\theta$ 采样出来的。最终可能还有给用户的 $y$。奖励可以是任务成功、单测通过、或回合结束的 RM，往往稀疏。

关键差三条：

1. **动作边界。** 一次工具调用内部仍是 token 级 $\log\pi$，但语义动作是「调了 search」。PPO 的 $\rho$ 仍按 token 乘；序列级 $\rho$ 随调用次数指数炸，更要 token 级 clip，见 `openai-ppo-clip`。
2. **哪些 token 有梯度。** 只在 assistant 自己生成的 token 上算 policy loss。把 $o_k$ 当模型输出反传，等于让模型去拟合搜索引擎。实现上 observation 段 `loss_mask=0`。Value 可以看全上下文，policy 不能对观察 token 更新。
3. **部分可观。** WebGPT 每步甚至换一份状态摘要，记忆只留在摘要里。现代 chat 把全程塞回上下文，见 `openai-tool-loop`。无论哪种，$o$ 是环境，不是策略。

WebGPT 的公开做法我会主动提：先行为克隆人的浏览轨迹，再对回合结束的 RM 做 PPO，每 token 加相对 BC 模型的 KL；他们还插了一批「只回答、不再逛」的 episode 提高样本效率。并行很多环境收 rollout。这是工具 RL 的最小故事。

## Credit 和环境重置

稀疏奖励：$r$ 在第 $K$ 步才到，前面全 0。GAE 仍沿 token 回传，但跨了若干次工具，早期 search query 的优势估计方差很大。缓解：

- 过程奖励 / 单测：编译过、检索命中、中间 assertion。Let's Verify 是数学步骤，不是工具，但「不要只给终局」是同一逻辑。
- 缩短回合：最大工具步、重复调用熔断。无限步的 agent 把 credit 稀释到噪声。
- 奖励塑形要声明：塑形错了会教模型刷中间指标（疯狂 search）。

重置：每个 rollout 必须从干净沙箱开始。没重置的失败模式很具体：上一个 episode 写过 `out.txt`，这一个不调工具也能「读到答案」，RM 给高分，策略学会躺赢。浏览器 cookie、账号额度、GPU 上的临时包，都是泄漏。WebGPT 用受限搜索 API，仍要假定查询有副作用；生产工具更甚。并行环境数不够时，PPO 的 batch 全是高度相关的轨迹，clip 看着稳，一换种子就崩。

KL 锚仍是冻结 SFT / BC，不是「对工具输出的 KL」。工具文本分布会变（网页改版），对观察做 KL 没有意义。Hacking：模型发明不存在的 tool 名、对同一 URL 死循环、把观察里的提示词当系统指令。这些要环境拒绝 + 负奖励，不能指望 clip 解决，见 `openai-instructgpt-kl`。

错法：把整段对话（含 tool 结果）当 InstructGPT 的 $y$ 做 PPO；说 agent RL 不需要 token 级 ratio；不谈重置。

## 追问

- **观察很长怎么训？** 截断、摘要、只留 schema 化字段。截断是数据决策，要在轨迹里打标，否则复现不了。上下文墙见 `openai-long-ctx-train`。
- **Off-policy 行不行？** 旧轨迹上的 $\rho$ 更炸，工具策略一变，观察分布也变。可以先 BC 再短 PPO；纯离线 DPO 对工具轨迹要小心，没执行过的调用没有真 $o$。
- **和推理时搜索？** 推理时 BoN / 多想不更新权重，见 `openai-test-time`。Agent RL 改的是会不会调工具。可以叠：训完的策略在测试时再多开几条轨迹。
- **并行工具怎么写进 $\tau$？** 一次 assistant 步里多个无依赖调用，算同一 $a$ 里的若干段 token，观察按 tool call id 对齐写回，不要按完成时间乱序。
