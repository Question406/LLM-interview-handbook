---
id: pt-prm-orm-critic
section: posttrain
order: 21
level: S
title: Outcome Reward、Process Reward、PRM 与 Critic 有什么区别？
quick: "ORM 看最终结果对不对，PRM 看每一步本身对不对，Critic 估的是按当前策略从这一步走下去还能拿多少期望回报。Critic 的值随策略变化，也不需要逐步正确性标签，所以它和 PRM 谁也替代不了谁。"
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

这三个东西回答的是三个问题：ORM 问整条轨迹最后成没成，PRM 问某一步本身好不好，Critic 问当前策略从现在走下去期望还能拿多少。都叫成「打分模型」的话，监督标签、reward shaping 和价值基线就混成一团了。

举个例子，一道数学题，模型第三步算错，第五步又凑巧改对，最后答案正确。ORM 给满分；PRM 会在第三步扣分；Critic 在第三步之后的估值，取决于当前策略通常能不能从这种错误里爬出来，策略一变，这个值也跟着变。

| 对象 | 典型输出 | 回答的问题 | 标签从哪来 |
| --- | --- | --- | --- |
| 最终结果奖励 / ORM | $R(\tau)$ 或 $r(x,y)$ | 最后成功了吗？ | 答案核对、单测、偏好模型对整段打分 |
| Process reward / PRM | $r_t$ 或 step score | 这一步本身是否正确 / 有帮助？ | 逐步人工或自动标注，如 Let's Verify Step by Step |
| Critic | $V^\pi(s_t)$ | 从 $s_t$ 按当前 $\pi$ 继续，未来期望回报多少？ | 不需要逐步正确性；用 return / TD target 拟合 |

ORM 最接近「任务真的完成了」，数学里对最终数字、代码里跑测试套件都属于这类。目标干净，缺点是稀疏：长 CoT 里早错晚对、答案对但过程荒唐，全挤进一个标量，credit assignment 很难做。

PRM 把稀疏的结果信号细化成逐步反馈。Let's Verify Step by Step 发现，在逐步筛选这类搜索里，过程监督往往比只看最终答案更会找出错的那一步。它和 $V^\pi$ 是两回事：同一个中间式，后续策略换了，Critic 的值会变；PRM 如果标的是「这一步数学上合不合法」，就尽量不依赖后面怎么走。实际上「有帮助」很难标，正确的过程也不唯一，step grader 一样会被 hack，模型学会写得像对的。

Critic 是 actor-critic / PPO-GAE 里的 baseline，估的是 $V^\pi(s)=\mathbb{E}[G_t\mid s_t]$，策略变了，目标就跟着变。它不需要逐步正确性标签，用 Monte Carlo 或 TD 就能学。代价是 bootstrap 误差、和 Actor 同量级的显存，长推理里 $s_t$ 也不好定义。

## 放进 RL 里怎么分工

只有 ORM 时，整段共享一个 $R$，GRPO 的组均值比的就是「谁最后对了」，过程错但答案对的也会被抬上去。加上 PRM，可以把逐步奖励放进 $G_t$，也可以只在搜索 / 重排时用 PRM，RL 仍用 outcome 当锚，免得过程标签的偏差写进策略。ORM 加 Critic 就是 PPO 的做法：用 $V$ 当 baseline，并不声称每一步正确；GAE 插值调的是 future return 的方差，和解题步骤对错无关。

Agent RL 里常见的组合是：环境的最终结果当真实目标，Critic 帮着把长轨迹的回报分到各步，格式、安全和少量 process 奖励只做辅助。辅助项权重一大，模型就会去优化 rubric，任务本身没变好。

这里有个容易讲偏的地方。Let's Verify 的实验主场是逐步验证与搜索，它没有说 PRM 可以替换 PPO 四件套里的 $V_\psi$，讲成「以后不要 Critic」就偏题了。

三者谁也不严格包含谁。PRM 高分不代表 $V^\pi$ 高：一步正确但走进了死胡同，期望回报可以很低。$V^\pi$ 高也不代表逐步正确，策略可能靠猜碰对 outcome。ORM 成功更说明不了过程可解释。

## 追问

**PRM 一定比 ORM 好吗？**
不一定。dense credit 有用，但过程标签错了，策略会学到错误的步骤偏好；ORM 虽然稀疏，却更难被「像那么回事」的步骤骗过去。

**能不能用 PRM 当 Critic？**
可以把 $r_t$ 加进 $G_t$ 或 TD target，但 Critic 拟合的仍是未来累计期望，学出来的东西和单步 PRM 分数不是同一个量。

**Let's Verify 的主结论是什么？**
过程监督在找错步、做验证上强于 outcome 监督。它支持「搜索时用 PRM」，推不出「用 PRM 替换 PPO 的 $V$」。
