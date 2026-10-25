---
id: pt-prorl-scale-boundary
section: posttrain
order: 247
level: S
title: 结合 ProRL，怎样把 RL 训练边界真正拉开？
quick: "ProRL 的结论是边界能拉开，前提是训得够长、训得稳：难度卡在组内奖励方差非零的临界区，用 clip-higher / 动态采样防熵塌，KL 加周期性 reference reset 免得正则阻碍更新，同时提高 rollout 吞吐。只加 GPU 不算 scale RL。"
tags:
  - ProRL
  - RLVR
  - Exploration
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ProRL — Prolonged Reinforcement Learning Expands Reasoning Boundaries
    url: https://arxiv.org/abs/2505.24864
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

ProRL 给的答案是边界能拉开，但要把稳定训练拉到数千步，并且数据难度、探索、步数、verifier 和 rollout 吞吐一起 scale，只加卡没用。

先说为什么有人觉得拉不开。短训、只刷数学、base 已经过拟合的题上，常见的现象是 pass@1 涨、大 $K$ 持平，看起来就是 reweighting，见 `pt-rlvr-discovery-vs-reweighting`。ProRL 的反驳是，很多否定结论来自训得太短、题太熟。它把 GRPO 拉到两千步以上，任务也从数学、代码扩到 STEM、逻辑谜题和指令遵循。

要训这么久，第一件事是数据一直可学。组内要满足 $0\lt\mathrm{Var}(R_1,\ldots,R_G)$，全对没梯度，全错也没梯度。所以课程要跟着当前策略的临界区走，DAPO 的动态采样就是专门挑方差非零的组，见 `pt-dapo`。长期滤掉全错桶会变成一种隐性 curriculum，要周期性把超难题拿回来再探一探。

第二是探索预算，也就是 $G$、温度和输入提示（prompt）的多样性。熵一旦塌，后面的步数都只是在同一条链上刷分。熵塌是长训的第一杀手，只加温度多半只是把塌缩往后推。ProRL 用的是 DAPO 的 clip-higher 和动态采样。

第三是 KL 怎么处理。ProRL 保留了 KL，因为它从已经会 CoT 的蒸馏起点接着训，R1-Zero 是从 base 冷启动，起点不一样。训到后面 KL 项会逐渐主导 loss，这时周期性把 $\pi_{\mathrm{ref}}$ 重置成当前 $\pi_\theta$ 并清掉优化器状态，让正则回到「别一步走太远」的作用，免得永远钉死在旧 SFT 上。这和「DAPO 去掉 KL」不矛盾，两边的起点和任务都不同，见 `xiaohongshu-grpo-drop-kl`。

还有两件事决定能不能训到那么长。一是 verifier 得靠得住：边界能不能扩，取决于验证器有没有洞，刷到奖励模型（RM）的表面特征不算新能力。二是 rollout 吞吐：实际耗时受最长样本限制，系统跟不上，算法再稳也训不长，异步、partial、长度分组统计见 `byte-grpo-rollout-tail-gpu`。判断该不该继续训，要看 holdout pass@K 还在不在涨，训练 reward 到了平台不代表该停。ProRL 的看法是，提前停就是把「还没探索完」写成了「RL 不能发现新路径」。

论文还报告了两点：base 无论采多少次都过不了的题，长训后能过；轨迹和预训练语料的重叠在下降。这是边界可能扩大的证据，算不上定理。实验协议仍要锁温度、$K$ 和 verifier，否则又会把计算不足写成 discovery。ProRL 给的是一份长训配方，它没有说无限训就会变强。

## 追问

**这和「RL 只是重加权」怎么同时讲？**
两个结论可以同时成立。熟题上是 reweighting，base 本来就不会的逻辑谜题上更可能出新路径。按任务切片报，别用一个形容词概括整个 run。

**reference reset 会不会让 KL 失效？**
会换锚点。reset 以后约束的是相对最近稳定快照的近端偏离，管不到相对原始监督微调（SFT）的 drift，两套 KL 要分开看，见 `pt-trust-region-vs-drift-kl`。

**没有 2k 步预算怎么办？**
先保证有效组比例和熵，再谈步数。步数堆在零方差组和熵塌上，只是浪费 rollout。
