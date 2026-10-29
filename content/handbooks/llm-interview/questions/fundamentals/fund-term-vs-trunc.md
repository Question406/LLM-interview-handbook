---
id: fund-term-vs-trunc
section: fundamentals
order: 158
level: A
title: 轨迹自然结束和 max-length 截断，bootstrap 各该怎么做、偏在哪？
quick: >-
  真正 terminal（EOS、环境吸收态）之后没有未来，bootstrap 必须是 0，否则就把 $V$ 的 hallucination
  加进了已经结束的回合。max-length / time-limit 只是你停止 sampling，任务理论上还在，通常仍要用 $V(s_T)$
  接上；误当成 terminal 会系统性低估长回复，这是负偏，跟降方差无关。
tags:
  - GAE
  - Bootstrap
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: 'https://arxiv.org/abs/1506.02438'
    type: primary
  - title: Time Limits in Reinforcement Learning
    url: 'https://arxiv.org/abs/1712.00378'
    type: primary
---

自然结束时 bootstrap 取 0，截断时要用 $V(s_T)$ 接上，两者的处理正好相反。EOS、环境吸收态之后真的没有未来了，再接一个 $V$ 是凭空加回报；打到 `max_tokens` 只是你不采了，任务理论上还在继续，当成结束会低估长回复。很多实现用一个 `done` 同时表示任务成功/失败和打到 `max_tokens`，把两者一律当「没有下一状态」，这类 bug 就是这么来的。手写递推见 `code-gae`，这里重点讲偏差的方向。

## 自然结束：未来是 0，再 bootstrap 就是正的 hallucination

任务自然结束，比如 EOS、验证器（verifier）已经判定、环境进入吸收态，真实的 $V^\pi(s_{\mathrm{term}})=0$，后面没有还没发生的奖励。GAE / TD 应该写成

$$
\delta_{T-1}=r_{T-1}+\gamma\cdot 0-V(s_{T-1}),
$$

后面的 trace 也要断掉。如果仍然乘上 $V(s_T)$，而实现里这往往是对 padding 位置乱估出来的一个数，就等于给已经结束的回合加了一截假回报。$V$ 恒正时这是正偏：模型会以为「结束之后还有分」，可能学到拖长，也可能学到提前结束，取决于 $V$ 的符号和你有没有把 EOS 当成动作。

## 截断：假装结束是负偏

`max_new_tokens`、time-limit、partial sampling 轨迹（rollout）切一刀时，环境并没有说「以后都是 0」，正确答案往往还在后面，$G_t$ 的尾巴等于被砍掉了。比如一道数学题推了一大半，正好撞上长度上限，这时如果按结束处理、不 bootstrap：

$$
\hat G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}
$$

就缺了 $\gamma^{T-t}V(s_T)$，对仍有正期望回报的状态是系统性低估，也就是负偏。长而还没写完的正确推理会被当成「到这里为止就这点分」，策略于是更爱短答。这也算不上无偏 MC，无偏 MC 要求轨迹按任务定义走完，按计算预算停下的不算。

正确做法是截断处仍然

$$
\delta_{T-1}=r_{T-1}+\gamma V(s_T)-V(s_{T-1}),
$$

承认「后面我没采，用 critic 估一下」。这会重新引入 bootstrap 偏差，但比谎称结束诚实。Pardo et al. 那篇 time-limit 的结论就是：训练时的时间上限应该当 truncation 处理，不该写进环境动力学当 terminal。

在 LLM 里，EOS 是 terminal；达到长度上限、`--partial-rollout` 的半截、异步 abort 都是 truncation。半截轨迹还叠着 off-policy 的问题，旧 prefix 要 mask 或者做 TIS，见 `fund-vtrace`。把截断直接当负例（超长就给 $r=0$）是又一层目标扭曲，DAPO 用 overlong shaping 就是为了避开这种假标签，见 `pt-dapo`。

## 追问

**$\gamma=1$ 时截断更致命吗？**
是。没有折扣，被砍掉的尾巴权重是 1，负偏更大。

**没有价值评估模型（critic）的 GRPO 怎么处理截断？**
没有 $V(s_T)$ 可接。常见做法是不训半截、mask 掉没完成的 token，或者给长度惩罚，但不把「没写完」等同于「答错」。别发明一个 0 当 bootstrap。

**答对了但超长呢？**
任务可能已经对了。按 terminal 处理并给对的 $r$，同时用 shaping 罚长度，别只因为截断就把 $r$ 打成 0。

**为什么两个 mask 都要？**
`terminated` 断 bootstrap 和 trace；`truncated` 只断 sampling，不断 bootstrap。合成一个 `done` 是经典 bug。
