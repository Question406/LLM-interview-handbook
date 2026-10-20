---
id: align-agent-rl
section: alignment
order: 21
level: S
title: 对齐：多智能体 / 工具 RL 的稀疏奖励与信用分配
quick: "轨迹几十步，奖励只在终点给 0/1。不要把每个 token 分配同一个回报就当解决了。要说清信用落在哪一层：token、一次工具调用、还是整段 episode；组内比较回报能降低方差，但不能从全零奖励里变出信号。"
tags:
  - OpenAI
  - DeepMind
  - Agent
  - RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: WebArena — A Realistic Web Environment for Building Autonomous Agents
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: DeepSeek-R1 — Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

OpenAI / DeepMind / 做 agent post-training 的岗会问「工具环上怎么做 RL」，需要解释训练过程，单独背出 ReAct 名称不够。公开环境像 WebArena 把成功钉在功能结果上：页面状态对了才给 1，中间点击全是 0。不是某次现场逐字题。我会按稀疏奖励、信用落在哪一层、多 agent 把故障乘起来，接到 `align-grpo` 和 `align-tool-rl`。

## 轨迹长、奖励短，梯度在罚谁

一次 episode 交替包含模型生成的 token、工具调用和环境返回的观察。典型是 $r_t=0$（$t\lt T$），终局 $r_T\in\{0,1\}$：单测过、表单提交成功、WebArena 的终态检查。Monte Carlo 回报

$$
G_t=\gamma^{T-t}r_T.
$$

若把同一个 $\hat A$ 乘到整段 response 的每个 token 上，等于宣布「这百步里每一字同等有功」。必要的探索点击和最后一次幸运提交被当成同一笔账。这是把信用分配问题藏进共享标量。

三层别混：

1. **Token 级。** 和普通 LLM 强化学习（RL）一样，只在模型自己吐的 token 上乘优势。工具返回的观察不是动作，把观察也计入策略梯度，就等于把「读页面」当成模型的动作。
2. **Turn / tool 级。** 一次完整调用（名字 + 参数 + 是否被宿主执行）一个优势。适合「点错按钮」这种离散错。
3. **Episode 级。** 整段轨迹一个 $r_T$。实现最简单，稀疏最狠。成功率若接近 0 或 1，组内全平，GRPO 的 $\hat A=0$，见 `align-grpo`。

$\gamma\lt 1$ 会惩罚长轨迹，诱导少点几下；$\gamma=1$ 更公平但方差更大。可验证任务优先 $\gamma=1$ 再靠组标准化，不要靠折现假装有 shaping。

```python
def episode_adv(r_T, T, gamma=1.0):
    # 同一终局标量回放到每一步；真正的 credit 还要靠分组 / 过程信号
    gs = [ (gamma ** (T - t)) * r_T for t in range(T) ]
    return gs
```

只回放不够。组内要有成功/失败对照，否则全 0 没有梯度。温度、任务课程、重置到「差一步」的中间态，都是在制造可学习的对比，不是调 LR 能替代的。

## 多 agent：全局奖会变成甩锅

两个助手分别负责执行和检查，只给「最终对了」一个标量，训练会学会把锅推给对方：自己少说话、让别人承担探索。面试要能提 **counterfactual / difference reward（反事实奖励或差分奖励）** 的公开概念：固定其他人的动作，只换自己的 $a^i$，看全局 $r$ 差多少。LLM 里很难对其他 agent 真做积分，工程上退化为：每人有可检查的子目标（检索是否命中 ACL、补丁是否过单测），全局奖仍保留当门禁。过程信号必须来自环境事件，不要让人阅读思维链（CoT）后主观打「合作分」，见 `align-process-reward`。

失败模式：无限计划环；工具失败被解释成「再试」打爆下游；一个 agent 刷「我调用了工具」的痕迹拿 shaping，任务没动。奖励被刷的方式和单模型相同，见 `align-reward-hack`。反向 KL 到参考策略仍然要在，见 `align-rlhf-kl`；它约束策略偏离参考模型的程度，不负责告诉你哪一次点击有功。

## 面试怎么收

可验证、能重置的环境：outcome + 组相对（或 RFT 的 grader）是主路径，见 `align-rft`。开放网页、不可复现：先把评测环境冻住，见 `design-eval-agent`，再谈 RL。多 agent 在单循环的预算、trace、确认框还没稳之前不要上，见 `design-agent-harness`。白板画一条长轨迹、终点一个 0/1、问「这 1 分给哪几个动作」：面试官要听到的是：共享 $\hat A$ 无法区分哪些动作真正促成了成功。

## 追问

- **共享优势是不是就等于解决了 credit？** 不是。它只是方差约化。谁有功仍没拆开，除非过程信号或 counterfactual。
- **成功率 2% 能不能直接 GRPO？** 组内经常全 0。先课程、演示、或可重置的中间态，把成功率抬到能分出组。
- **观察 token 要不要进策略梯度？** 不要。观察是环境，不是动作；mask 只留模型自己的 token 和 tool 调用。
- **和过程奖励什么关系？** 过程奖是在密化 $r$，见 `align-process-reward`；信用分配是 $r$ 给定之后怎么回放到动作。两件事正交。
