---
id: anthropic-hh-rlhf
section: anthropic
order: 9
level: S
title: Anthropic：HH-RLHF 里 helpful 和 harmless 冲突时，偏好怎么采？
quick: >-
  两套数据分开采：helpful 要尽量完成用户意图，harmless 要在有害请求上拒绝且别滑进说教。冲突时人标的是「更无害的那个」，不是折中成含糊答应。PM
  混训后会看到 Pareto：更有帮助往往更不拒，要显式加权，不要假装一个标量能同时最大。
tags:
  - Anthropic
  - RLHF
  - HH
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
  - title: Training a Helpful and Harmless Assistant (Anthropic)
    url: https://www.anthropic.com/research/training-a-helpful-and-harmless-assistant-with-reinforcement-learning-from-human-feedback
    type: primary
---

HH-RLHF 是 Anthropic 对齐岗的默认背景。Bai 等人 2022 年的论文把助手拆成 helpful 和 harmless 两轴，并写明这两个目标会冲突。面试要能讲清：冲突时标注员按什么规则挑，训练时损失怎么混，上线时怎么看回归。

## 冲突长什么样

Helpful：用户问怎么修自行车，你给步骤；用户问怎么写得更清楚，你改稿。Harmless：用户问怎么造爆竹、怎么跟踪前伴侣，你拒绝并尽量解释为什么，而不是把拒绝写成道德演讲，也不要假装没听见然后漏步骤。

典型打架：

- 用户明确要有害帮助。Helpful 想配合，harmless 想拒。
- 拒得太狠：无害查询也被拒（over-refusal），helpful 掉下去。
- 又想帮又想拒：给出「仅供教育」的半套步骤，两边都不满意。

论文观察到：把 helpful 推高，harmless 评测会掉；把 harmless 推高，模型变得回避问题、更多拒答。这是 Pareto 前沿，不是标注没标好。

## 采集时就拆开，不要让同一个人脑内加权

Anthropic 的做法是 **两套对比数据**：

1. **Helpful 对话。** 标注员扮演用户，和模型多轮聊，在两条回复里选更有帮助、更诚实、更不啰嗦的。这里尽量别塞进「是否安全」当主标准，否则 helpful 信号被无害性淹没。
2. **Harmless / 红队。** 标注员主动诱导有害行为，再在两条回复里选更无害的。有害请求上，「清楚拒绝 + 必要时给无害替代」优于「配合」；也优于「辱骂用户」或「空洞说教」。

冲突样本出现在红队集里。标注说明要写死优先级：**伤害优先于完成任务。** 不是 50/50 投票，也不是「看谁更有礼貌」。平局（两条都拒得一样好，或两条都有害）不要硬选；进 `anthropic-pref-bt` 的平局通道，或者丢掉。硬选会把噪声写进 PM。

诚实（honest）在论文里是第三轴，更难单独采：事实错误、编造来源。实践里常并进 helpful 的「别瞎编」条款，而不是再拉一套标注。面试提一句即可。

## 训练时混，但权重是超参

偏好模型仍是 Bradley-Terry：选中回复得分高于落选，

$$
P(y_w \succ y_l \mid x)=\sigma\bigl(r(x,y_w)-r(x,y_l)\bigr).
$$

数据混合 $D_H \cup D_{HH}$。混合比例是超参：harmless 太少，强化学习（RL） 之后一推 helpful 就越狱；harmless 太多，上线全是拒答。论文用同一个 PM 吃两套对比，再 PPO。RL 阶段奖励是 PM 分数减相对 监督微调（SFT） 的 KL，细节对照 `openai-instructgpt-kl`。

我还会看两条曲线，而不是一个 Elo：helpful 评测（人类或 held-out PM）和 harmless 评测（红队胜率、有害完成率）。一个数涨、另一个掉，就是在前沿上滑动，不是「对齐完成了」。

CAI / RLAIF 后来把 **harmlessness 的对比** 交给模型按条款标，helpful 仍可走人标。不要说 HH-RLHF 被 CAI 整包替换。见 `anthropic-rlaif`。

## 追问

- **一条回复能不能同时打 helpful 分和 harmless 分？** 能，变成多目标 PM。上线要用约束或拉格朗日：无害低于阈值就拒，而不是把两分加起来。加法会在高 helpful 的有害回答上作弊。
- **标注员意见不一致怎么办？** 红队任务一致性往往低于摘要偏好。记 disagreement 率，噪声标签用 `anthropic-pref-bt` 的稳健损失，不要假装黄金标签。
- **过度拒绝怎么压？** 在 harmless 数据里显式加入「该答的要答」对比：拒无害请求的当负例。CAI 的 constitution 里也有反过度拒绝条款。
- **和 直接偏好优化（DPO） 的关系？** 损失可以换成 DPO，冲突仍在数据里。换损失不解决「两轴打架」，只解决要不要单独训 奖励模型（RM）。

## 相关题

- [[anthropic-pref-collect]]：采集协议的全貌，包括双盲、平局和多轴分开采，冲突处理只是其中一节。
- [[anthropic-pref-bt]]：把对比变成分数时，平局和噪声标签怎么处理。
- [[align-cai]]：harmless 这一轴后来改用 constitution 加 AI 反馈，替代了大部分逐条人工标注。
