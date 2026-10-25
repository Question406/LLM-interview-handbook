---
id: align-online-dpo
section: alignment
order: 19
level: A
title: 对齐：在线 / iterative DPO，策略滞后
quick: "Iterative DPO 每轮用当前策略生成回答，重新标偏好后再训练，减少旧数据跟不上策略的问题。参考模型是否更新要单独决定：固定 SFT 比较稳，逐轮移动参考点能继续学，但更容易放大奖励偏差。"
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

在线 / iterative DPO 用当前策略重新采样、标注和训练，目的是让偏好数据跟上策略变化。比如一对旧回答的好坏已经很容易分清，当前模型却几乎不会再生成它们，继续反复训练这对数据，提供的信号就很有限。原始 DPO 使用离线偏好；Meta 的 Self-Rewarding 和 DPO 与 PPO 的比较实验，都讨论了更新采样分布的价值。

## 数据和参考点会分别滞后

离线偏好对通常来自接近 $\pi_{\mathrm{ref}}$ 的分布；策略走远后，旧 pair 中的 $\Delta$ 梯度会变得嘈杂且有偏。DPO 梯度依赖 $\pi_\theta(y_w)$、$\pi_\theta(y_l)$ 相对 $\pi_{\mathrm{ref}}$。若 $y_w,y_l$ 来自很旧的策略，当前 $\pi_\theta$ 在这些序列上 logp 已经极低，ratio 进饱和区：rejected 早被打穿，chosen 也带不上来，看起来像 $\beta$ 太小，其实是数据过期。这叫策略滞后：标注时的行为分布 $\neq$ 训练时的 $\pi_\theta$。

PPO / GRPO 每步用 $\pi_{\mathrm{old}}$ 采样轨迹（rollout），importance clip 管单步偏离；偏好来自刚刚采样的 $y$。DPO 把 rollout 和更新拆开，滞后可以跨很多 SGD step。离线 HH 还能用，是因为你不把策略推太远，或 pair 本来就覆盖宽。要持续涨能力、奖励会漂，离线一份 pair 不够。

参考模型要单独考虑。冻结监督微调（SFT）作为 $\pi_{\mathrm{ref}}$，整轮迭代的 KL 中心不变，通常更稳，但后期可能受 KL 预算限制而学不动。每轮换成上一轮策略，可以继续移动，却也更容易损害语言可用性，放大奖励模型（RM）的偏差。更新数据并不意味着必须同时更新这个参考点。

## 一轮怎么做

每轮按下面的顺序更新：

1. 从当前 $\pi_\theta$ 对一批 输入提示（prompt） 采 $k$ 条（$k=2$ 可直接比，更大可再筛）。
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

全部用新数据可能忘掉原有格式，全部重放旧数据又回到了离线训练。Replay 比例要根据遗忘切片调。

实际每轮能走多快，还取决于标注吞吐。人标跟不上时，系统往往变成在线采样、离线 RM 打分，这个 RM 本身也会过时。AI 标注要冻结版本、随机展示位置并定期人抽查。Self-rewarding 用当前策略当 judge 时，可能出现对 judge 的 win-rate 上涨、对人的偏好却下降的情况。

如果需要严格跟随当前策略采样，而且奖励可验证，我会考虑 PPO / GRPO，省去先存偏好对再拟合 logistic 的环节。已有偏好模型、希望少维护一个价值评估模型（critic），也能接受每轮几百到几千个新 pair 时，iterative DPO 比较合适。在线方法的数据跟着 $\pi$，通常更容易提升，也更容易利用 RM / judge 的漏洞。

监控时我会一起看相对 ref 的 KL、新 $y$ 的 logp、回答长度、gold 任务，以及 judge 和人评是否分叉。覆盖下降、KL 快速上升，可能是数据滞后或 $\beta$ 太小，先减少更新步数、补新 pair，再判断是否需要调学习率。

相关：`align-dpo`、`align-grpo`、`align-reward-hack`、`align-rlhf-kl`、`align-reward-model`。

## 追问

**每轮都要换 $\pi_{\mathrm{ref}}$ 吗？**
不必。能力还在涨、KL 未爆，冻 SFT 更稳。KL 顶死再考虑挪锚，并加安全门禁。
**旧 pair 全删吗？**
留一小段 replay 防忘；按 prompt 去重，避免同一题刷几百轮。
**online DPO 还要 clip 吗？**
标准 DPO 没有 PPO clip。特别不稳时说明你已经该回到 on-policy 强化学习（RL），而不是给 DPO 加第三种 KL。
**和 BoN 造 pair？**
用旧 RM 对当前采样做 BoN 再 DPO，是把 proxy 写进权重，滞后叠加 overoptimize，见 `align-best-of-n`。

## 相关题

- [[align-dpo]]：离线 DPO 的目标和 $\beta$ 的作用，这里讨论的滞后问题建立在它之上。
- [[openai-dpo-loss]]：讲 DPO 去掉了 on-policy rollout，这张卡讲去掉之后怎么补回来。
- [[align-kto]]：直接用线上的二元反馈训练，是另一种拿到当前策略数据的办法。
