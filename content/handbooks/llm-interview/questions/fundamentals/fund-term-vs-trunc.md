---
id: fund-term-vs-trunc
section: fundamentals
order: 158
level: A
title: 轨迹自然结束和 max-length 截断，bootstrap 各该怎么做、偏在哪？
quick: >-
  真正 terminal（EOS、环境吸收态）之后没有未来，bootstrap 必须是 0，否则把 $V$ 的幻觉加进已经结束的回合。max-length /
  time-limit 只是你停止采样，任务理论上还在，通常仍要用 $V(s_T)$ 接上；误当成 terminal 会系统性低估长回复，这是负偏，不是降方差。
tags:
  - GAE
  - Bootstrap
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: Time Limits in Reinforcement Learning
    url: https://arxiv.org/abs/1712.00378
    type: primary
---

陷阱是把框架里的 `done` 一律当「没有下一状态」。很多实现一个 `done` 既表示任务成功/失败，又表示打到 `max_tokens`。两者对 $V(s')$ 的处理相反。手写递推见 `code-gae`；本题只钉 **偏倚方向**。

## Terminal：未来是 0，再 bootstrap 是正的幻觉

任务自然结束：EOS、verifier 已判定、环境进入吸收态。真实 $V^\pi(s_{\mathrm{term}})=0$（没有尚未发生的奖励）。GAE / TD 应

$$
\delta_{T-1}=r_{T-1}+\gamma\cdot 0-V(s_{T-1}),
$$

后面的 trace 也断掉。若仍乘 $V(s_T)$（实现上常是对 padding 位置乱估的一个数），等于给已结束的回合加了一截假回报。$V$ 若恒正，这是 **正偏**：模型会以为「结束之后还有分」，也可能学到拖长或提前结束，取决于 $V$ 的符号与你是否把 EOS 当动作。

## Truncation：假装结束是负偏

`max_new_tokens`、time-limit、partial rollout 切一刀时，环境并没有说「以后都是 0」。正确答案往往还在后面。此时 $G_t$ 的尾巴被砍掉。若不 bootstrap：

$$
\hat G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}
$$

缺少 $\gamma^{T-t}V(s_T)$，对仍有正期望回报的状态是 **系统性低估**（负偏）。长而尚未写完的正确推理会被当成「到这里为止就这点分」，策略更爱短答。这不是无偏 MC——无偏 MC 要求轨迹按任务定义走完，而不是按计算预算走完。

正确做法：truncation 处仍

$$
\delta_{T-1}=r_{T-1}+\gamma V(s_T)-V(s_{T-1}),
$$

承认「后面我没采，用 critic 估」。这重新引入 bootstrap 偏差，但是比「谎称结束」更诚实。Pardo et al. 的 time-limit 结论就是：训练用的时间帽应视为 truncation，不应写入环境动力学当 terminal。

LLM 实务：EOS 是 terminal；打到长度帽、`--partial-rollout` 的半截、异步 abort 是 truncation。半截还要叠 off-policy：旧 prefix 该 mask 或 TIS，见 `fund-vtrace`。把 truncation 当负例（超长直接 $r=0$）是又一层目标扭曲，DAPO 用 overlong shaping 就是为了避免这种假标签，见 `pt-dapo`。

## 追问

- **$\gamma=1$ 时截断更致命吗？** 是。没有折扣，砍掉的尾巴权重是 1，负偏更大。
- **没有 critic 的 GRPO 怎么 truncation？** 没有 $V(s_T)$ 可接。常见是：不训半截、mask 掉未完成 token、或给长度惩罚但不把「没写完」等同「答错」。不要发明一个 0 当 bootstrap。
- **成功但超长呢？** 任务可能已经对。当 terminal 并给对的 $r$，同时用 shaping 罚长度；不要只因截断把 $r$ 打成 0。
- **两个 mask 为什么都要？** `terminated` 断 bootstrap 与 trace；`truncated` 只断采样、不断 bootstrap。合成一个 `done` 是经典 bug。
