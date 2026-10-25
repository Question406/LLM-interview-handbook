---
id: pt-rl-hparams-joint
section: posttrain
order: 249
level: A
title: RL 训练时 group size、学习率、PPO epoch、生成长度怎么一起定？
quick: "学习率和 epoch 乘在一起决定离 $\\pi_{\\mathrm{old}}$ 多远，常从 $10^{-6}$、1～2 个 epoch 起，epoch 加一档学习率就减一档；$G$ 常取 8 或 16，全对全错多就上动态采样；生成长度盖住正确答案的 P95，再加 overlong 惩罚。"
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

这四个数要一起定：学习率 $\eta$ 和 PPO epoch $E$ 乘在一起，决定一次更新离 $\pi_{\mathrm{old}}$ 多远；$G$ 和生成长度决定这笔梯度的方差和实际耗时。我一般从 $\eta$ 在 $10^{-6}$ 量级、$E$ 取 1 或 2、$G$ 取 8 或 16 起步，生成长度盖住正确推理的 P95，然后看监控调。

有效更新大约是 $\Delta\theta\propto\eta\cdot E\cdot\|\nabla L\|$，所以别把它们当成互不相干的 YAML。先定预算，再在预算里分配三件事：题内探索、题间覆盖、要不要复用旧轨迹。

先说 group size。GRPO 的优势是 $\hat A_i=(R_i-\mu_G)/(\sigma_G+\epsilon)$，$G$ 越大，$\mu,\sigma$ 越稳，稀疏的成功也更容易混进一组，但逐 token 生成（decode）的成本差不多线性上涨。token 预算固定时，$G$ 加大，能覆盖的不同输入提示就少了。全对或全错的组多，就加动态采样，把 $G$ 开到 64 只是好看，见 `pt-grpo-group-size`、`byte-grpo-all-same-zero-adv`。$G=1$ 时组均值 baseline 没有定义。

再说学习率和 epoch。大模型策略梯度的学习率通常在 $1\times 10^{-6}$ 到 $5\times 10^{-6}$。同一批采样轨迹上 $E$ 越大，样本越 off-policy，$\rho=\pi_\theta/\pi_{\mathrm{old}}$ 越容易顶到 clip，所以 **epoch 加一档，学习率往往要减一档**。很多可验证奖励强化学习（RLVR）的实践倾向 $E=1$ 或 $2$，用新鲜采样换样本效率。clip fraction 飙升、KL 暴涨时，先砍 epoch 或 $\eta$，别先怪 $G$。

生成长度的上限必须盖住正确推理的 P95 / P99，否则对的长答案会被截断，变成假负例。但无限加长会喂长尾：一个 batch 的时间是 $\max_i T_i$，显存和奖励噪声也一起涨。DAPO 的 overlong shaping 把「答错」和「写超了」分开处理，见 `pt-dapo`。长度惩罚的权重不能盖过任务奖励，否则模型学会提前收尾，该写的证明不写。

调的时候一起看几项：有效组比例、clip fraction、策略熵、平均长度、holdout pass@1。比如 $G$ 加大了，有效组比例却不涨，说明难度不对；长度涨、reward 涨、holdout 不涨，是长度 hack。对应的动作也直接：信号稀疏就加 $G$ 或上动态采样；ratio 飘就减 $\eta$ 或 $E$；截断造成假标签就放长上限并配软惩罚；实际耗时主要被少数长轨迹拖住时，按长度分组、分段生成或改用异步调度，再加 $G$ 没用。

## 追问

**$G$ 和 global batch 是一回事吗？**
不是。$G$ 是每道题的 rollout 数，global batch 是一次 optimizer step 的样本数。混在一起会把组拆散，优势估计就坏了，见 `sys-rl-group-n`。

**为什么有人把 epoch 设成 1 还留着 clip？**
clip 配置还在，但 $\rho$ 几乎总在 $1$ 附近，clip fraction 恒为 0，这个监控就失效了。要么显式关掉 clip 改用 CISPO / REINFORCE，要么承认单步更新只靠 KL 和熵在约束，见 `sys-rl-fw-clip-zero`。

**小模型能把学习率开到 $10^{-5}$ 吗？**
有时可以，但要同时盯 KL 和格式崩坏。小模型更怕一步走太远，胆子不该更大。
