---
id: pt-pg-to-ppo-to-grpo
section: posttrain
order: 4
level: S
title: 从 Policy Gradient 怎么一步步推到 PPO，再推到 GRPO？
quick: "REINFORCE 无偏但方差大；减 baseline 得到 advantage，再用 Critic + GAE 估它；想复用旧轨迹就乘 $\\rho$，PPO 用 clip 限制 $\\rho$。最后把 $V_\\psi$ 换成同一道题的组内均值，就是 GRPO，clip 原样留着。"
tags:
  - Policy Gradient
  - PPO
  - GRPO
  - GAE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Policy Gradient Methods for Reinforcement Learning with Function Approximation
    url: https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
  - title: Trust Region Policy Optimization
    url: https://arxiv.org/abs/1502.05477
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---
这条链每一步都只修上一步的一个毛病：REINFORCE 给出无偏梯度但方差大，减 baseline 降方差，用 Critic 和 GAE 去估 advantage，用重要性采样复用旧轨迹，用 clip 限制 ratio 得到 PPO，最后把 Critic 换成同题组内的统计量，就是 GRPO。白板上按这个顺序推，比背三份互不相关的公式好讲得多。

## 1. REINFORCE：让不可微的环境也能求导

目标是 $J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)]$。用对数导数 $\nabla\pi=\pi\nabla\log\pi$，把「对分布求导」变成「对 $\log\pi$ 取期望」：

$$
\nabla_\theta J=\mathbb{E}_{\tau\sim\pi_\theta}\Big[R(\tau)\sum_t\nabla_\theta\log\pi_\theta(a_t\mid s_t)\Big].
$$

因果性允许把整段 $R$ 换成从 $t$ 开始的回报 $G_t$，仍然无偏，这就是 REINFORCE。完整板书见「Policy Gradient Theorem / REINFORCE 怎么从目标函数推出来？」。

它的毛病是一条轨迹的 $G_t$ 噪声极大，好状态里的普通动作和坏状态里的好动作，被同一把尺子衡量。

## 2. Baseline / Advantage：期望不变，只降方差

只依赖 state 的 $b(s)$ 满足 $\mathbb{E}_{a\sim\pi}[\nabla\log\pi(a\mid s)b(s)]=0$，所以

$$
\nabla_\theta J=\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t-b(s_t))\big]
$$

和原来是同一个期望。最自然的选择是 $b(s)=V^\pi(s)$，系数就变成了 advantage $A^\pi=Q^\pi-V^\pi$，意思是「这个动作比这个状态下的平均行为好多少」。细节见「Policy Gradient 为什么可以减 Baseline？」和「Bellman Equation、V、Q、Advantage 的关系？」。

接下来的问题是真实的 $V^\pi$ 没有闭式解。用 Monte Carlo 估 $G_t$ 噪声还是大，用一步 TD 又可能有偏。

## 3. Actor-Critic + GAE：用 $V_\psi$ 在 bias 和 variance 之间插值

于是再训一个 Critic $V_\psi(s)$。TD residual $\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$ 是一步的 advantage；GAE 把不同 horizon 的 $\delta$ 做指数混合，用 $\lambda$ 在「信 bootstrap」和「信整条回报」之间滑动。推导见「从 TD residual 推导 GAE，并解释 $\gamma$、$\lambda$」。

到这一步已经是 on-policy 的 actor-critic 了：Actor 用 $\hat{A}$ 做策略梯度，Critic 拟合 $V^\pi$。LLM 基于人类反馈的强化学习（RLHF）里的 PPO 就是这个骨架，再加上 clip 和 KL。

可它每更新几步就得重新采样，样本太贵，大家自然想在同一批采样轨迹（rollout）上跑好几个 epoch。

## 4. Importance Sampling：在旧轨迹上估新策略

数据来自 $\pi_{\mathrm{old}}$，要优化的却是 $\pi_\theta$，所以乘一个重要性权重

$$
\rho_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)}
$$

得到一阶 surrogate

$$
L(\theta)=\mathbb{E}_{t\sim\pi_{\mathrm{old}}}\big[\rho_t(\theta)\,\hat{A}_t\big].
$$

在 $\theta=\theta_{\mathrm{old}}$ 处 $\rho=1$，一阶导数和真实的 on-policy 梯度一样，所以可以小步复用这批数据。可一旦 $\rho$ 离 1 太远，少数几个样本就会支配整个估计，方差爆炸。这一步对应「Importance Sampling 为什么成立？为什么 variance 会爆？」和「On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？」。

所以还需要一个机制，别让 $\theta$ 跑太远，不然 surrogate 就不可信了。

## 5. TRPO：硬信任域，PPO 的理论动机

TRPO 直接写成约束：最大化 $L(\theta)$，同时要求 $D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)\le\delta$。这是相对上一轮行为策略的正向 KL，保证新策略不会把旧策略认为好的动作概率压没。实现上要共轭梯度加线搜索，工程很重。

PPO 的贡献就是不去真的解这个带约束的二次规划，改用 clip，在「有利方向更新过头」时把 surrogate 削平。

## 6. PPO：clip 近似信任域，RLHF 再加 drift KL

Clipped objective 是：

$$
L^{\mathrm{CLIP}}(\theta)=\mathbb{E}_t\left[\min\big(\rho_t\hat{A}_t,\ \mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\hat{A}_t\big)\right].
$$

$\hat{A}_t>0$ 时限制 $\rho$ 别太大，$\hat{A}_t\lt 0$ 时限制 $\rho$ 别太小。clip 的是目标函数，真实的概率比并没有被强制截进区间。符号上的效果见「PPO clipped objective 为什么长这样？」和百度真题卡。

接到 LLM 对齐上，还要再加一套 KL。clip 和 TRPO 管的是相对 $\pi_{\mathrm{old}}$ 的 Trust-Region；InstructGPT 式的 PPO 还会在奖励里减掉

$$
r_t\leftarrow r_\phi(x,y)-\beta\log\frac{\pi_\theta(y_t\mid x,y_{1:t-1})}{\pi_{\mathrm{ref}}(y_t\mid x,y_{1:t-1})},
$$

这是相对冻结监督微调（SFT）模型的 Drift，方向是反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$。这两套 KL 管的东西不一样，见「PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？」。

PPO 在 RLHF 里是四件套：Actor 被优化，Reference 冻结当锚，Reward Model 打分，Critic 出 $V$ 给 GAE，见「Actor、Reference、Reward Model、Critic 分别做什么？」。

它的毛病出在 Critic 上。Critic 几乎和 Actor 一样大，要同步，会过拟合，在长思维链（CoT，即分步推理过程）上 $V(s)$ 也很难估。数学、代码这种同一道题可以互相对比、奖励只在序列末尾出现的任务，逐步 bootstrap 根本用不上。

## 7. GRPO：用组均值代替 $V_\psi$，clip 留下

对同一个输入提示 $x$ 采 $G$ 条回复 $o_1,\ldots,o_G$，得到标量奖励 $r_1,\ldots,r_G$，做组内归一化

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon},\qquad \mu=\frac1G\sum_j r_j
$$

当作这条回复里每个 token 共享的 advantage。PPO 的 clip 原样保留，$\rho$ 还是 $\pi_\theta/\pi_{\mathrm{old}}$。DeepSeekMath 把相对 $\pi_{\mathrm{ref}}$ 的 KL 写成 $k_3$ 加进损失（loss），没有扣进奖励分数（reward）。

这一步改的只是 baseline 的构造方式，策略梯度还是那个策略梯度。PPO 用学出来的 $V^\pi(s)$ 减掉「这个前缀往后的期望回报」；GRPO 用「同一道题、这一组样本的经验均值」，衡量的是这条回复比同题其它回复好多少。组均值不是 Value Function，也没有逐步的 future return，见「GRPO 是什么？为什么能去掉 Critic？」。

在 reasoning 强化学习（RL）里这么做是合理的。outcome reward 到 EOS 才出现，一条回复里的 token 本来就共享同一个回报 $G$，同一个输入提示的多条 rollout 天然就是一组对照，GAE 的逐步信用分配挖不出信息，花那么大成本训 Critic 就显得亏了。

如果面试官只问「PPO 和 GRPO 的公式差在哪」，我会说：两者是同一套 clipped IS 策略梯度，差在 advantage 从哪来，以及还要不要训 Critic。

## 追问

**GRPO 还需要 fresh rollout 吗？**
需要。GRPO 仍然是近似 on-policy 的，epoch 太多、ratio 偏离太远，$\rho$ 一样会出数值问题。

**GRPO 为什么还要 clip？**
美团会这么问。组 baseline 只换掉了 $A$ 的来源，信任域没换，所以 clip 还得留着。

**一组全对或全错会怎样？**
$\hat{A}=0$，没有相对信号，这一批就是空梯度。PPO 的 Critic 在这种情况下还可能给出非零的 $A$，只是不一定对。

**除以 $\sigma$ 做归一化有代价吗？**
有。它会改变不同题目的权重，Dr.GRPO 指出了长度和 std 带来的偏置。RLOO 用的是「不含自己的组均值」，更接近教科书里的 baseline。
