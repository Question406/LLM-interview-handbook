---
id: align-online-dpo
section: alignment
order: 19
level: A
title: 对齐：在线 / iterative DPO，策略滞后
quick: >-
  离线 DPO 假设 pair 来自接近 $\pi_{\mathrm{ref}}$ 的分布。策略一走远，旧 pair 的 $\Delta$ 梯度又噪又偏。Iterative DPO
  用当前策略采样、再标、再训，缩短滞后；参考模型更不更、标注跟不跟得上，是两件分开的事。
tags:
  - OpenAI
  - Meta
  - DPO
  - Online RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Self-Rewarding Language Models
    url: https://arxiv.org/abs/2401.08092
    type: primary
  - title: Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study
    url: https://arxiv.org/abs/2404.10719
    type: primary
---

DPO 论文本身是离线偏好。之后一堆 iterative / online 变体：当前策略采样两条、人 or AI 标、再 DPO，循环。Meta 的 self-rewarding、以及「DPO 对 PPO 全面比」里的在线实验，都在说同一件事：off-policy pair 会过时。对齐岗问策略滞后，不是让你背新名字。离线推导见 `align-dpo`；在线采样族见 `align-grpo`。

## 滞后是什么

DPO 梯度依赖 $\pi_\theta(y_w)$、$\pi_\theta(y_l)$ 相对 $\pi_{\mathrm{ref}}$。若 $y_w,y_l$ 来自很旧的策略，当前 $\pi_\theta$ 在这些序列上 logp 已经极低，ratio 进饱和区：rejected 早被打穿，chosen 也带不上来，看起来像 $\beta$ 太小，其实是 **数据过期**。这叫策略滞后：标注时的行为分布 $\neq$ 训练时的 $\pi_\theta$。

PPO / GRPO 每步用 $\pi_{\mathrm{old}}$ rollout，importance clip 管单步偏离；偏好来自刚刚采样的 $y$。DPO 把 rollout 和更新拆开，滞后可以跨很多 SGD step。离线 HH 还能用，是因为你不把策略推太远，或 pair 本来就覆盖宽。要持续涨能力、奖励会漂，离线一份 pair 不够。

参考模型是第二件滞后。经典做法冻 SFT 当 $\pi_{\mathrm{ref}}$，整条迭代 KL 中心不变，安全但后期 KL 预算花完就学不动。另一做法每轮把 ref 换成上一轮策略：中心跟着走，能继续学，也更容易离开可用语言、放大 RM hack，见 `align-reward-hack`、`align-rlhf-kl`。面试把「数据滞后」和「KL 锚滞后」分开说。

## 一轮 iterative 长什么样

最小闭环：

1. 从当前 $\pi_\theta$ 对一批 prompt 采 $k$ 条（$k=2$ 可直接比，更大可再筛）。
2. 打标：人、隔离的 RM、或隔离的 LLM judge。Judge 家族不要等于被训模型，见 `align-llm-judge`、`align-rlaif`。
3. 组成 pair 或 binary（KTO），见 `align-kto`。
4. DPO / IPO 若干 step，早停看 held-out 任务和 KL。
5. 把新策略当下一轮采样器。旧 pair 按时间衰减或丢掉，不要无限拼接当「更多数据」。

```python
def mix_pairs(fresh, replay, p_fresh=0.8):
    # keep a small replay to avoid catastrophic forgetting
    n = len(fresh)
    n_old = int(n * (1 - p_fresh))
    return fresh + replay[-n_old:]
```

纯新鲜会忘格式；纯 replay 等于离线。Replay 比例是超参，对着遗忘切片调。

标注吞吐决定循环半径。人标跟不上就变「在线采样 + 离线 RM」，RM 自己会过时，见 `align-reward-model`。AI 标要版本冻结、位置随机、定期人抽查。Self-rewarding 用当前策略当 judge，滞后变成自嗨，win-rate 对 judge 涨、对人跌。

## 和 PPO 怎么选

要 tight on-policy、奖励可验证：PPO / GRPO 更干净，少一次「先存 pair 再拟合 logistic」的弯。已有偏好模型、想少养 critic、接受一轮几百到几千新 pair：iterative DPO 合理。不是谁淘汰谁。经验上在线方法更容易涨，因为数据跟着 $\pi$；也更容易 hack，因为 RM / judge 也在被搜。

监控：相对 ref 的 KL、相对采样策略的覆盖（新 $y$ 的 logp）、长度、gold 任务、judge-vs-human 分叉。覆盖掉、KL 狂飙，就是滞后或 $\beta$ 过小。先减步数、加新鲜 pair，不要先加 LR。

## 追问

- **每轮都要换 $\pi_{\mathrm{ref}}$ 吗？** 不必。能力还在涨、KL 未爆，冻 SFT 更稳。KL 顶死再考虑挪锚，并加安全门禁。
- **旧 pair 全删吗？** 留一小段 replay 防忘；按 prompt 去重，避免同一题刷几百轮。
- **online DPO 还要 clip 吗？** 标准 DPO 没有 PPO clip。特别不稳时说明你已经该回到 on-policy RL，而不是给 DPO 加第三种 KL。
- **和 BoN 造 pair？** 用旧 RM 对当前采样做 BoN 再 DPO，是把 proxy 写进权重，滞后叠加 overoptimize，见 `align-best-of-n`。
