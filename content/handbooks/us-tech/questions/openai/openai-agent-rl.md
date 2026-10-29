---
id: openai-agent-rl
section: openai
order: 30
level: S
title: OpenAI：工具循环上的 RL，轨迹、credit、环境重置，和 token 级 PPO 差在哪
quick: >-
  工具 RL 的轨迹包含模型动作和环境观察，训练时只对模型生成的 token 计算 $\log\pi$，工具返回内容的 loss mask
  为零。回合末奖励可以用 GAE 沿轨迹分配，但长工具链的 credit assignment 更难；每次 sampling
  都要重置环境，防止旧文件、cookie 等残留泄漏答案。
tags:
  - OpenAI
  - RL
  - Agents
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary
  - title: WebGPT — Browser-assisted question-answering with human feedback
    url: 'https://arxiv.org/abs/2112.09332'
    type: primary
  - title: Function calling
    url: 'https://platform.openai.com/docs/guides/function-calling'
    type: primary
---

工具循环上的 RL，需要把轨迹里的模型动作和环境观察分清楚。模型会生成搜索词或工具参数，宿主执行后再把网页、JSON 或报错返回；这些返回内容并非模型生成，因此不能当作策略动作来算梯度。奖励可能到整个回合结束才出现，还要保证每次 sampling 从干净环境开始。

公开对照是 InstructGPT 和 WebGPT：前者对一段 completion 做 PPO，后者把行为克隆、reward model 和 PPO 接到了搜索、点击、引用的文本浏览器上。下面按轨迹、credit assignment 和环境重置来说明，Clip 与 KL 见 `openai-ppo-clip`、`openai-instructgpt-kl`，运行时如何加入观察见 `openai-tool-loop`。

## 先区分 token 动作与工具交互

**Token 级 PPO（InstructGPT）。** 状态 $s_t=x\circ y_{1:t-1}$（prompt 加已写前缀），动作 $a_t$ 是 vocabulary 里一个 token。奖励通常在 EOS 才有 $r_\phi(x,y)$，中间步 0，再减 token KL。GAE 把终局优势回传到每个 token。On-policy 数据是「同一 prompt 下的一条文本」。

**工具循环 RL。** 回合是

$$
\tau=(s_0,a_0,o_1,a_1,o_2,\ldots,a_{K-1},o_K,y).
$$

$a_k$ 是模型一次输出：自然语言、或一次 / 一组 `tool_calls`。$o_{k+1}$ 是宿主执行后的观察（JSON、网页、报错），不是 $\pi_\theta$ sampling 出来的。最终可能还有给用户的 $y$。奖励可以是任务成功、单测通过、或回合结束的 RM，往往稀疏。

实现时先标出 action boundaries。语义上一次 search 是一个工具动作，模型内部仍要逐 token 计算 $\log\pi$。PPO 的 $\rho$ 可按 token 组合，但整段连乘的序列级 $\rho$ 会随调用次数迅速变大，因此更要核对 token 级 clip，见 `openai-ppo-clip`。

policy loss 只覆盖 assistant 生成部分，观察 $o_k$ 的 `loss_mask=0`。否则模型会被要求拟合搜索引擎的输出。Value 可以读取全上下文，policy 仍不能对观察 token 计算动作梯度。

还要考虑部分可观测性。WebGPT 每步可换成一份状态摘要，记忆只留在摘要里；现代 chat 往往把全过程送回上下文，见 `openai-tool-loop`。两种写法中，$o$ 都来自环境。

WebGPT 的公开训练过程是：先行为克隆人的浏览轨迹，再对回合结束的 RM 做 PPO，每 token 加相对 BC 模型的 KL；他们还插了一批「只回答、不再逛」的 episode 提高样本效率。并行很多环境收 sampling 轨迹（rollout）。这给出了从示范轨迹到回合奖励训练的一套公开例子。

## Credit 和环境重置

如果奖励 $r$ 到第 $K$ 步才出现、前面全为 0，GAE 虽然仍能沿 token 回传，但跨过多次工具后，早期 search query 的 advantage estimation 方差会很大。

可以用编译通过、检索命中、中间 assertion 等过程奖励或单测，增加中间反馈。Let's Verify 针对数学步骤，体现的也是更细的反馈思想。还可以限制最大工具步、对重复调用熔断，缩短回合。新增的 reward shaping 必须说明，因为模型也可能靠反复 search 刷中间指标。

每次 sampling 轨迹（rollout）都要从干净沙箱开始。比如环境没有重置时，上一个 episode 写过 `out.txt`，这一个不调工具也能「读到答案」，RM 给高分，策略学到依赖残留状态的捷径。浏览器 cookie、账号额度、GPU 上的临时包，都是泄漏。WebGPT 用受限搜索 API，仍要假定查询有副作用；生产工具更甚。并行环境数不够时，PPO 的 batch 全是高度相关的轨迹，clip 看着稳，一换种子就崩。

KL 锚仍是冻结 SFT / BC，不是「对工具输出的 KL」。工具文本分布会变（网页改版），对观察做 KL 没有意义。模型还可能编造 tool 名、循环访问同一 URL，或把观察里的 prompt 当系统指令。环境要拒绝这些动作，并配相应负奖励，clip 本身修不好工具策略错误，见 `openai-instructgpt-kl`。

检查训练实现时，可以重点核对这几处：对话里的 tool 结果是否被误算进 InstructGPT 式的 $y$，token 级 ratio 是否仍正确计算，以及每轮是否真的重置环境。

## 追问

**观察很长怎么训？**
可以截断、摘要，或只保留按字段和类型规范（schema）整理的内容。截断方式属于数据决策，需要在轨迹里标记，才能复现。上下文墙见 `openai-long-ctx-train`。
**Off-policy 行不行？**
旧轨迹上的 $\rho$ 更炸，工具策略一变，观察分布也变。可以先 BC 再短 PPO；纯离线 DPO 对工具轨迹要小心，没执行过的调用没有真 $o$。
**和推理时搜索？**
推理时 BoN / 多想不更新权重，见 `openai-test-time`。Agent RL 改的是会不会调工具。可以叠：训完的策略在测试时再多开几条轨迹。
**并行工具怎么写进 $\tau$？**
把同一 assistant 步的多个无依赖调用记作同一个 $a$ 中的若干段 token，返回观察按工具调用 id 对齐。只按完成时间写回，会把结果对应错。

## 相关题

- [[coding-gae]]：这里说 credit 用 GAE 沿轨迹回传，那张要你手写 GAE 反向递推，并分清 done 和长度截断。
