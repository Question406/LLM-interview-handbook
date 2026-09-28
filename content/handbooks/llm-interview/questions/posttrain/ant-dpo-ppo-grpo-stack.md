---
id: ant-dpo-ppo-grpo-stack
section: posttrain
order: 120
level: A
title: 蚂蚁智能体优化算法：如何介绍 DPO、PPO、GRPO 的选型？
quick: >-
  PPO 有 RM / value，在线稳但重；DPO 吃离线偏好，简单，但受数据和长度 bias 卡住；GRPO 组相对、可弱化
  critic，适合可验证奖励的推理 / Agent。我会按「有没有成对偏好、有没有 verifier、基建预算够不够」来选。
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

错法：「谁更新、谁更火」排个序，或者把三套算法说成同一目标的三种实现。它们吃的信号不同：DPO 吃成对偏好，PPO 吃标量奖励加价值估计，GRPO 吃同题组内相对奖励。蚂蚁智能体我还会加一条可审计约束：工具失败、规则拒绝、超时必须进评测，不能只追自动分。先报现场约束，有没有稳定偏好对、有没有可执行 verifier、卡够不够同时驻留 actor / critic / ref / RM，再点名算法。没报约束就报商标，下一问「为什么不换」会答空。

## 三条目标，不要背商标

PPO 是 clipped on-policy actor-critic。轨迹奖励来自 RM 或环境，优势用 GAE 降方差，再加反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 锚住参考，采样在当前策略上，见 `fund-kl-directions`。它适配需要精细连续权衡的场景，比如安全分、成本、拒答同时拉扯，但四件套同时驻留，显存和同步最重。Clip 越界且处在有利方向时，该 token 梯度为 0，长 CoT、多轮 off-policy reuse 时这是已知病，CISPO 改的就是 clip 对象，见 `pt-cispo`。

DPO 从同一 KL 约束最优策略导出，直接吃 $(x,y_w,y_l)$，训练图里没有 online rollout。适合风格、安全、拒答，或「在已有正确答案里选更好的」。短板要写清楚：离线分布、长度 bias、标签错了没法靠采样自纠。没有 verifier 的 Agent 轨迹，DPO 探不到新工具路径。

GRPO 对同一 prompt 采 $n$ 条，$n\gt 1$ 才能定义组相对优势，见 `sys-rl-group-n`：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

组均值代替 learned $V$，省 critic，常配可验证奖励（数学、代码、字段校验）。整组全对或全错则 $\mathrm{std}=0$，$\hat A=0$，这一步白算。小 $n$ 更容易撞上零方差组；太大则 decode 线性涨、相对信号被摊薄。

## 选型与 Agent 补丁

按信号选，不按新旧：有成对偏好、要快对齐，用 DPO；有可靠 verifier、要探索推理或工具轨迹，用 GRPO；需要价值估计或复杂连续权衡、组内对照不够用，用 PPO。信贷 / 风控把规则失败写成硬门，不要指望 RM 自己学会合规。R1 类公开流程常是 SFT 冷启动再 GRPO，中间可穿插拒绝采样。蚂蚁场景我会补一句：自动分可以当训练奖励，上线门禁仍要人工可审计的失败原因，否则 reward hacking 会先于业务指标出现。

## 追问

- **GRPO 为什么能省 critic？** 同一题的组均值当 baseline。代价是 $n=1$ 优势未定义，小 $n$ 易整组同奖励得到零梯度，见 `sys-rl-group-n`。
- **DPO 能不能替代 Agent RL？** 不能。离线 pair 覆盖不到没见过的工具路径，也更新不了「当时失败的那条轨迹」。
- **PPO clip 和 CISPO？** PPO clip 的是 surrogate $\rho A$，越界 token 梯度可为 0；CISPO clip 的是 detach 后的 IS 权重，梯度仍走 $\log\pi$，见 `pt-cispo`。
- **组全错怎么办？** 换难度、升温、加大 $n$，或用 DAPO 动态丢掉零方差组。不要先加学习率。
- **四件套显存不够又必须 PPO？** 先砍 critic 规模或改 GRPO；不要默默去掉 ref，反向 KL 锚丢了，漂移没有仪表。
