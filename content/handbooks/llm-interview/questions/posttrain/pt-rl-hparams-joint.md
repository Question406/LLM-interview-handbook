---
id: pt-rl-hparams-joint
section: posttrain
order: 249
level: A
title: RL 训练时 group size、学习率、PPO epoch、生成长度怎么一起定？
quick: "学习率和 epoch 相乘决定离 $\\pi_{\\mathrm{old}}$ 多远，常从 $10^{-6}$、1～2 个 epoch 起；$G$ 常取 8 或 16；生成长度盖住正确答案的 P95，再加 overlong 惩罚。"
tags:
  - GRPO
  - Hyperparameters
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

这块容易把四个数当成互不相干的 YAML。有效更新大约 $\Delta\theta\propto\eta\cdot E\cdot\|\nabla L\|$：学习率 $\eta$ 和 PPO epoch $E$ 乘在一起。$G$ 和生成长度决定这笔梯度的方差和实际耗时。先定预算，再在预算里分「题内探索 / 题间覆盖 / 是否复用旧轨迹」。

## Group size

GRPO 的 $\hat A_i=(R_i-\mu_G)/(\sigma_G+\epsilon)$。$G$ 大，$\mu,\sigma$ 稳，稀疏成功更容易混进一组，但 逐 token 生成（decode）成本近似线性涨。token 预算固定时，增大 $G$ 就会减少能覆盖的不同输入提示。常见从 8 或 16 起；全对 / 全错多就加动态采样，而不是把 $G$ 开到 64 装好看，见 `pt-grpo-group-size`、`byte-grpo-all-same-zero-adv`。$G=1$ 时组均值 baseline 未定义。

## 学习率 × epoch

大模型策略梯度通常 $1\times 10^{-6}$ 到 $5\times 10^{-6}$。同一批采样轨迹上 $E$ 增大，样本更 off-policy，$\rho=\pi_\theta/\pi_{\mathrm{old}}$ 更容易顶到 clip。所以 **epoch 加一档，学习率往往要减一档**。很多可验证奖励强化学习（RLVR）实践倾向 $E=1$ 或 $2$，用新鲜采样换样本效率。clip fraction 飙升、KL 暴涨，先砍 epoch 或 $\eta$，不要先怪 $G$。

## 生成长度

上限必须盖住正确推理的 P95 / P99，否则对的长答案被截断，变成假负例。无限加长会喂长尾：batch 时间是 $\max_i T_i$，显存和奖励噪声一起涨。DAPO 的 overlong shaping 把「答错」和「写超了」分开，见 `pt-dapo`。长度惩罚权重不能盖过任务奖励，否则模型学会提前收束、该写的证明不写。

## 一起看的验收

有效组比例、clip fraction、策略熵、平均长度、holdout pass@1。$G$ 加大而有效组不涨，是难度错了。长度涨、reward 涨、holdout 不涨，是长度 hack。稀疏就加 $G$ 或动态采样；ratio 飘就减 $\eta$ 或 $E$；截断假标签就加长并配软惩罚；实际耗时主要由少数长轨迹决定时，就按长度分组、分段生成或采用异步调度，而不是再加 $G$。

## 追问

- **$G$ 和 global batch 是一回事吗？** 不是。$G$ 是每题 rollout 数；global batch 是一次 optimizer step 的样本数。混在一起会把组拆开，优势估计坏掉，见 `sys-rl-group-n`。
- **为什么有人把 epoch 设成 1 还留着 clip？** clip 配置还在，但 $\rho$ 几乎总在 $1$ 附近，clip fraction 恒为 0，监控失效。要么显式关掉 clip 改 CISPO / REINFORCE，要么承认单步只靠 KL 和熵，见 `sys-rl-fw-clip-zero`。
- **小模型能把学习率开到 $10^{-5}$ 吗？** 有时可以，但要同时看 KL 和格式崩。小模型更怕一步走太远，不是更该猛。
