---
id: fund-kl-posttrain-index
section: fundamentals
order: 140
level: A
title: Forward / Reverse KL 后训练八股要准备哪些题？
quick: "按顺序准备：KL 定义和采样方向，SFT 正向与 RLHF 反向，Trust-Region 与 Drift KL，OPD / OPSD 蒸馏，最后是 $k_1/k_2/k_3$ 和 $\\beta$ 的工程问题。"
tags:
  - KL
  - Post-Training
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多 - 大模型算法 秋招一面
    url: https://www.nowcoder.com/discuss/906953010406772736
    type: candidate-first-hand
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

网上对得上的高频问法已经拆成独立卡。点下面每条就能跳到对应题。

## 先把定义写会

- Shannon 熵是什么？为什么是 $-p\log p$？最大最小分别在哪？
- Cross Entropy、MLE、KL 的关系？
- KL 散度为什么一定非负？等号何时成立？
- 从 logits 到 Softmax 再到交叉熵，梯度为什么是 $\hat{p}-y$？
- 条件熵和互信息怎么从熵推出来？和 KL 是什么关系？
- Entropy Regularization 和 Sampling Temperature 有什么区别？

## 方向本身

- Forward KL vs Reverse KL：Mode-Covering / Mode-Seeking 是什么意思？
- JS 散度和 KL 散度差在哪？为什么 GAN 早期爱提 JS？
- 拼多多秋招：正向 KL 和反向 KL 有何区别？

## 接到后训练目标

- SFT 在最小化哪种 KL？RLHF 又在最小化哪种？
- 对齐为什么用 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，而不是反过来？
- PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？
- 知识蒸馏默认用正向 KL，MiniLLM / OPD 为什么改成反向？
- On-policy Distillation 为什么能同时获得 RL 的 state-distribution relevance 和蒸馏的稠密反馈？
- OPSD 和 OPD 差在哪？同一套权重怎么当自己的老师？
- Self-OPD 家族怎么分？u-OPSD、π-Distill、LOPD 各补哪块？
- 没有标准答案时 u-OPSD 怎么自己当老师？和 GRPO 多数票差在哪？
- OPSD 和 STaR / Rejection Sampling 差在哪？为什么错解还能提供梯度？
- 前沿 Agent 只给动作不给 CoT 时，π-Distill 怎么把特权信息迁走？
- LOPD 为什么把特权上下文改成可学习的 latent，而不是再手写一种 $y^\star$？

## 工程落地

- 对齐为什么必须加 KL？系数太大或太小会怎样？
- 自适应 KL controller 在做什么，比固定 $\beta$ 好在哪？
- DPO 的 β 到底控制什么？
- KL 按 token 平均还是按整段序列加总？两种写法差在哪？
- Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？
- 蚂蚁一面：PPO 的 KL 能改成交叉熵吗？
- 蚂蚁：GRPO 的 KL 和 PPO 有何不同？K1/K2/K3 是什么？
- GRPO 的 KL 和 PPO 的 KL 是一模一样的吗？

串起来理解时，先看采样分布确定方向；Trust-Region 比较 $\pi_{\mathrm{old}}$，Drift 比较 $\pi_{\mathrm{ref}}$。外部 OPD 的学生采样常对应反向 KL；OPSD 还需要检查下一 token 的公式究竟是 $D(p_T\|p_S)$ 还是 $D(p_S\|p_T)$。
