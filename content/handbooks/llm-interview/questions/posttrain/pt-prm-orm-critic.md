---
id: pt-prm-orm-critic
section: posttrain
order: 21
level: S
title: Outcome Reward、Process Reward、PRM 与 Critic 有什么区别？
quick: >-
  ORM/Outcome reward 只评价最终结果；Process reward/PRM 给中间 reasoning step 质量信号；Critic
  不是步骤正确性评分器，而是当前 policy 下从 state 出发的 expected future return。
tags:
  - Reward
  - PRM
  - Credit Assignment
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: "Let's Verify Step by Step"
    url: https://arxiv.org/abs/2305.20050
    type: primary
---

这块容易把三个词都叫成「打分模型」。它们回答的问题不同：轨迹最后对不对、某一步本身好不好、以及当前策略从现在走下去期望还能拿多少。混用会把监督标签、奖励整形和 value baseline 焊成一团。

## 1. 一张表钉定义

| 对象 | 典型输出 | 回答的问题 | 标签从哪来 |
| --- | --- | --- | --- |
| Outcome reward / ORM | $R(\tau)$ 或 $r(x,y)$ | 最后成功了吗？ | 答案核对、单测、偏好模型对整段打分 |
| Process reward / PRM | $r_t$ 或 step score | 这一步本身是否正确 / 有帮助？ | 逐步人工或自动标注，如 Let's Verify Step by Step |
| Critic | $V^\pi(s_t)$ | 从 $s_t$ 按当前 $\pi$ 继续，未来期望回报多少？ | 不需要逐步正确性；用 return / TD target 拟合 |

ORM 最靠近「任务真的完成了」。数学里对最终数字、代码里对测试套件，都是 outcome。优点是目标干净；缺点是稀疏：长 CoT 里早错晚对、对了但过程荒唐，都挤在一个标量里，credit assignment 难。

PRM 把稀疏 outcome 拉成逐步密度。Let's Verify Step by Step 表明：在搜索（如逐步筛选）里，过程监督往往比只看最终答案更会找错步。它不是 $V^\pi$。同一中间式，换一条后续策略，Critic 的值会变；PRM 若标的是「这一步数学上是否合法」，则尽量不依赖后面怎么走。实践里「有帮助」很难标，过程也不唯一，step grader 一样会被 hack（写得像对的）。

Critic 是 actor-critic / PPO-GAE 里的 baseline：估的是 $V^\pi(s)=\mathbb{E}[G_t\mid s_t]$，策略变了，目标跟着变。它可以在没有逐步正确性标签时，用 Monte Carlo 或 TD 学。代价是 bootstrap 误差、与 Actor 同阶的显存，以及长推理上 $s_t$ 难定义。

## 2. 信用分配怎么接进 RL

- 只有 ORM：整段共享一个 $R$，GRPO 的组均值就是在比「谁最后对了」。过程错但答案对也会被抬上去。
- ORM + PRM：逐步奖励进 $G_t$，或只在搜索 / 重排时用 PRM，RL 仍用 outcome 当锚，减少过程标签的偏差写进策略。
- ORM + Critic：PPO 用 $V$ 减 baseline，不宣称每步正确；GAE 插值的是 future return 的方差，不是解题步骤对错。

Agent RL 里常见组合：环境最终结果当真实目标，Critic 处理长 horizon credit，格式 / 安全 / 少量 process 奖励只做辅助。辅助项权重过大，模型会优化 rubric 而不是任务。Let's Verify 的实验主场是逐步验证与搜索，不是宣称 PRM 可以替换 PPO 四件套里的 $V_\psi$；把论文结论讲成「以后不要 Critic」会偏题。

## 3. 谁也不严格包含谁

PRM 高分不等于高 $V^\pi$：一步正确但进入死胡同，期望回报可以很低。$V^\pi$ 高不等于逐步正确：策略可能靠猜答案碰对 outcome。ORM 成功更不蕴含过程可解释。面试若被追「用 PRM 当 Critic」，答：可以把 process reward 加进 return，Critic 拟合的仍是累计期望，不是单步 PRM 分数的拷贝。

## 追问

- **PRM 一定比 ORM 好吗？** 不一定。Dense credit 有用，但错误过程标签会把 inductive bias 直接写进 policy；ORM 稀疏却更难被「像那么回事」的步骤欺骗。
- **Critic 能不能从 PRM 学？** 能把 $r_t$ 纳入 $G_t$ 或 TD target；学到的仍是未来累计，不是逐步正确性打分器。
- **Let's Verify 的主结论是什么？** 过程监督在找错步 / 验证上强于 outcome 监督；它支持「搜索时用 PRM」，并不自动等于「用 PRM 替换 PPO 的 $V$」。
