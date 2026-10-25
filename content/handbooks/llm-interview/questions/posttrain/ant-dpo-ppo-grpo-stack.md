---
id: ant-dpo-ppo-grpo-stack
section: posttrain
order: 120
level: A
title: 蚂蚁智能体优化算法：如何介绍 DPO、PPO、GRPO 的选型？
quick: "三个算法吃的信号不一样，按手里的信号和资源选：有稳定偏好对、要快速对齐用 DPO，简单但受数据质量和长度偏置影响；有可靠 verifier、要探索推理或工具轨迹用 GRPO，它用组内相对奖励代替 Critic；需要价值估计和复杂连续权衡才上 PPO，系统最重。选之前先报监督信号、探索需求和基础设施预算。"
tags:
  - Ant Group
  - DPO
  - PPO
  - GRPO
  - "2026"
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 20260508蚂蚁集团大模型智能体优化算法一二面
    url: https://www.nowcoder.com/feed/main/detail/263bc804663b4a0aa7b312154d720817
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型智能体优化算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：2026-05-08
- 来源类型与可信度：牛客候选人原帖，A（公司、岗位、日期与轮次明确）
- 原始措辞：**“介绍 dpo、ppo、grpo”**

我会先说这三个算法吃的信号不一样，再按手里的信号选：直接偏好优化（DPO）吃成对偏好，PPO 吃标量奖励加价值估计，GRPO 吃同题组内的相对奖励。所以点名算法之前先报现场约束：有没有稳定的偏好对，有没有可执行的验证器（verifier），卡够不够同时放下 actor、价值评估模型（critic）、ref 和奖励模型（RM）。约束没报就直接报算法名，下一问「为什么不换一个」就答空了。按「谁更新、谁更火」排序，或者说成同一目标的三种实现，都答偏了。

先说 PPO。它是 clipped on-policy actor-critic：轨迹奖励来自 RM 或环境，优势用 GAE 降方差，再加反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 把策略锚在参考附近，采样在当前策略上，见 `fund-kl-directions`。它适合安全分、成本、拒答同时拉扯这类要精细连续权衡的场景，代价是四个模型同时驻留，显存和同步最重。还有一个已知问题：clip 越界且处在有利方向时，这个 token 的梯度是 0，长思维链（CoT）和多轮 off-policy reuse 时更明显，CISPO 改的就是 clip 的对象，见 `pt-cispo`。

DPO 从同一个 KL 约束下的最优策略推出来，直接吃 $(x,y_w,y_l)$，训练图里没有在线采样轨迹（rollout）。它适合风格、安全、拒答，或者「在已有正确答案里挑更好的」。短板也要说清楚：数据是离线分布，有长度 bias，标签错了没法靠采样自己纠正。没有 verifier 的 Agent 轨迹，DPO 探不到新的工具路径。

GRPO 对同一个输入提示采 $n$ 条回答，$n\gt 1$ 才能定义组相对优势，见 `sys-rl-group-n`：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

组均值代替学出来的 $V$，所以省掉 critic，常配可验证奖励，比如数学、代码、字段校验。整组全对或全错时 $\mathrm{std}=0$，$\hat A=0$，这一步白算。$n$ 小更容易撞上零方差组；$n$ 太大，decode 成本线性增加，相对信号也被摊薄。

所以选型按信号来，和新旧无关。比如一个办业务的智能体：手里有成对偏好、要快对齐，用 DPO；每条轨迹跑完能用可靠的 verifier 判对错、要探索推理或工具轨迹，用 GRPO；要价值估计或复杂连续权衡、组内对照不够用，用 PPO。R1 这类公开流程常是监督微调（SFT）冷启动再 GRPO，中间可以穿插拒绝采样。信贷、风控这类场景，规则失败要写成硬门，别指望 RM 自己学会合规。

蚂蚁智能体我还会补一条可审计的要求：工具失败、规则拒绝、超时都必须进评测，光追自动分不够。自动分可以当训练奖励，上线门禁仍要有人工可审计的失败原因，不然钻奖励规则空子的问题会比业务指标先冒出来。

## 追问

**GRPO 为什么能省 critic？**
用同一题的组均值当 baseline。代价是 $n=1$ 时优势没有定义，$n$ 小又容易整组同奖励、得到零梯度，见 `sys-rl-group-n`。

**DPO 能不能替代 Agent 强化学习（RL）？**
不能。离线 pair 覆盖不到没见过的工具路径，也没法更新「当时失败的那条轨迹」。

**PPO 的 clip 和 CISPO 有什么区别？**
PPO clip 的是 surrogate $\rho A$，越界 token 的梯度可能是 0；CISPO clip 的是 detach 之后的 IS 权重，梯度仍然走 $\log\pi$，见 `pt-cispo`。

**组全错怎么办？**
换难度、升温、加大 $n$，或者用 DAPO 动态丢掉零方差组。别先加学习率。

**显存放不下四个模型，又必须用 PPO 呢？**
先缩 critic 规模，或者改用 GRPO。别悄悄去掉 ref，反向 KL 的锚一丢，策略漂移就没有仪表可看了。
