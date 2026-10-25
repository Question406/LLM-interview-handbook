---
id: openai-dpo-loss
section: openai
order: 10
level: S
title: OpenAI：DPO 相对 PPO 少了什么，implicit reward 怎么说
quick: "DPO 直接用偏好对优化策略，省掉显式奖励模型、在线 rollout、critic 和 PPO clip。参考策略和 KL 约束的影响仍保留在 log 概率比里；隐式奖励是 $r(x,y)=\\beta\\log(\\pi_\\theta/\\pi_{\\mathrm{ref}})$，不需要另训打分头。"
tags:
  - OpenAI
  - DPO
  - RLHF
  - Preference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

DPO 用偏好对直接训练策略，省掉 PPO 流程里的奖励模型和在线采样等环节，但参考策略仍然在损失里。比如同一问题有 chosen、rejected 两个回答，DPO 比较的是策略相对 reference 给它们增加了多少 log 概率，再推动 chosen 相对更高。

这是一道公开方法对照题：OpenAI 的公开主线是 InstructGPT PPO-RLHF，DPO 来自另一篇论文，不能说成已核实的 onsite 原题。InstructGPT 先用偏好数据 $\to$ 训练奖励模型 $r_\phi$ $\to$ 用当前策略采样 $\to$ 减 ref KL $\to$ 计算 GAE / value $\to$ 做 clip 更新。在线环节成本高、调试复杂，ratio 也可能出现极端值。

KL 约束的 基于人类反馈的强化学习（RLHF） 目标是

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}}).
$$

最优策略满足 $r(x,y)=\beta\log(\pi^*(y\mid x)/\pi_{\mathrm{ref}}(y\mid x))+Z(x)$。DPO 把这个 $r$ 反代回 Bradley-Terry：

$$
p(y_w\succ y_l\mid x)=\sigma\big(r(x,y_w)-r(x,y_l)\big),
$$

$Z(x)$ 消掉，得到

$$
\mathcal{L}_{\mathrm{DPO}}=-\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big).
$$

推导里用奖励差做偏好预测，$Z(x)$ 就抵消了。实现因而能直接训练策略，显式 RM、on-policy 采样循环、value / GAE、PPO clip 都不再需要；偏好对、冻结的 $\pi_{\mathrm{ref}}$ 和 $\beta$ 仍然保留。KL 的作用通过最优策略解析式进入了对 ref 的 log 比。

隐式奖励可以理解为当前策略相对 SFT 给这句回答增加了多少 log-mass。$\beta$ 大会更约束策略靠近 ref，$\beta$ 小则放大偏好间隔，容易过拟合 chosen/rejected。

实际使用时先冻结 $\pi_{\mathrm{ref}}$，不能让它随 $\theta$ 一起更新，否则 KL 锚也会移动。再检查数据是否太旧：当 $\pi_\theta$ 离采样策略很远，隐式 $r$ 上的 BT 假设会变差，PPO 则至少能在当前 $\pi$ 上采样。DPO 可定期换数据，或改用 online / iterative DPO。

序列 log 比按 token 求和，长回答容易获利，可以做长度归一化或在数据里控制 chosen/rejected 长度。模型也可能利用标注偏好的表面特征，所以仍要独立于偏好数据的 eval。计算损失时在 log 空间算 $\Delta$，使用 `logsigmoid`，避免先 exp 再减。CAI 的原则式反馈可对照 `anthropic-constitutional-ai`。

相关：`openai-instructgpt-kl`、`openai-ppo-clip`、`openai-eval-harness`

## 追问

**还要 PPO clip 吗？**
标准 DPO 不要。$\beta$ 和 ref 已经在管步长。有人加 DPOP / hinge，那是变体。
**implicit reward 能当 RM 用吗？**
能打偏好对的分数差，但不保证绝对尺度，也不能直接当 best-of-n 的黄金 RM。
**和 InstructGPT 三阶段？**
DPO 通常接在 监督微调（SFT） 后，替换 RM+PPO。SFT 还在，否则 $\pi_{\mathrm{ref}}$ 太弱。
**为什么面试还要会 PPO？**
因为 OpenAI 原设定、在线探索、过程奖励、工具调用 强化学习（RL），DPO 闭式罩不住。

## 相关题

- [[align-dpo]]：同样讲隐式奖励，但重点放在 $Z(x)$ 怎么消掉，以及 $\beta$ 太大、太小各会怎样。
- [[coding-dpo-weighted]]：要求手写 DPO 梯度并解释每对样本的权重，准备白板轮时看这张。
- [[align-online-dpo]]：接着「DPO 去掉了 on-policy rollout」往下问：离线 pair 滞后时怎么用迭代采样补回来。
- [[msft-orpo]]：ORPO 连参考模型也去掉了，和这张卡连起来能讲清 PPO、DPO、ORPO 各要加载几个模型。
- [[us-llm-paper-stack]]：DPO 和 InstructGPT 都在面试前的精读论文栈里，那张卡说明要读到什么程度。
- [[align-reward-model]]：DPO 砍掉的那张显式 RM 怎么用 Bradley-Terry 训，两边是同一个偏好模型。
