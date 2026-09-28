---
id: pt-multiturn-preference-credit
section: posttrain
order: 232
level: S
title: 多轮对话偏好里，如何做 credit assignment？
quick: >-
  用户常只评整段会话，信号是稀疏终局偏好。要把功过分到关键 turn / token：回合级 DPO、逐步优势估计，
  或只对标注回合更新，避免误伤早期正确澄清；不要默认「最后一轮差评只怪最后一轮」。
tags:
  - Multi-turn
  - Credit Assignment
  - Preference Learning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Multi-turn Reinforcement Learning from Preference Human Feedback
    url: https://arxiv.org/abs/2405.14655
    type: primary
---

这块容易栽两处：把整段会话当一条 completion 做 DPO，梯度均匀推高 / 压低所有 turn；以及默认「最后一轮差评 = 只怪最后一轮」。用户常只评整段 $A\succ B$，真正导致胜负的可能是第 $t$ 轮错误工具调用，也可能是第 1 轮的错误承诺。稀疏终局偏好是 delayed reward，credit assignment 不解决，早期正确澄清会被误伤。

## 整段 DPO 为什么会摊匀功过

会话 $H=(x_1,y_1,\ldots,x_T,y_T)$。若损失对 $\log\pi_\theta(y_{1:T}\mid x)$ 整段反传，每个 token 分到的是同一个标量偏好间隔。第 2 轮正确的身份核验和第 4 轮乱承诺退款被同一符号更新。这和单轮里「序列级 advantage 抹平关键 token」是同类问题：粒度错了，再好的优化器也把功过摊匀。`pt-cispo` 关心的是 clip 不要丢掉 token 梯度；本题更上游，优势本身有没有分到该负责的 turn。没有 mask 的多轮 DPO，默认是在误伤。用户中途改需求、插入纠正、或只在结束时点踩，终局标签对中间 turn 是偏置的：早期按当时信息正确的澄清，不应被后来的新约束追溯惩罚。两条轨迹若前缀相同、只在分叉后不同，监督应落在分叉点之后；对共享前缀做反向更新，是把方差打到无关 token 上。工具调用穿插在对话里时，credit 更不能按「最后一句用户反馈」切：一次错误的 `search` 参数可能在两轮之后才表现为答非所问，回合级归因至少要能回溯到该次调用。

## 三种把信用分下去的办法

（1）回合级偏好：只比较分歧 turn 及其后继前缀，前面共享上下文当条件、不更新或低学习率保护。（2）把会话当 MDP，终局偏好训 reward / 偏好模型，再对 turn 或 token 做 GAE：

$$
\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t),\qquad
\hat A_t = \sum_{l\ge 0}(\gamma\lambda)^l \delta_{t+l}.
$$

中间步 $r_t$ 多为 0，终局才有偏好转换的回报。$\lambda$ 接近 1 会把终局信号回传到很早的澄清，方差大；$\lambda$ 过小则只打最后一两轮，早期承诺仍然学不到。Turn 级 GAE 通常比 token 级更稳：对话的决策单元是「这一轮说什么 / 调不调工具」，不是单个虚词。（3）裁判或注意力标出关键 span，只对局部优化。越细越准，但贵，且引入裁判噪声。`fund-judge` 的位置 / 冗长偏差会变成错误的 span 归因。客服五轮、用户因第 4 轮乱承诺而选另一轨迹：整段 DPO 可能削弱第 2 轮核验话术；回合级更新应集中在承诺相关 turn。实现上对 assistant token 做 mask：共享前缀 `requires_grad=False` 或乘零，只让分歧段进 loss。用户改需求时，把「需求变更」本身写成观测，使 $s_t$ 可区分，否则 value 会把两种任务混成一个状态。工具轨迹还要区分「选错工具」和「参数填错」：终局失败时常是前者，只打最后一轮自然语言道歉解决不了 credit。若只有会话级偏好、没有分叉标注，最低配是：用两轨迹最长公共前缀切开，只对后缀做 DPO / RL，前缀当条件。

先钉监督粒度和「哪些 turn 被 mask」，再谈 DPO / RL 公式。粒度不对，换 loss 名字没有用。

## 追问

- **最后一轮负反馈就只更新最后一轮吗？** 不一定。错误可能是第 1 轮承诺或中间工具选错。要对照轨迹或 span，而不是默认终端归责。
- **中间澄清要保护吗？** 要。共享前缀、正确澄清应 mask 或降权，避免被终局偏好带偏。
- **和 token-level RL？** 有正确时间结构的 advantage 才能分信用；只把 DPO 换成 token-level IS（如 `pt-cispo`）而不改奖励时间结构，照样摊匀。
- **标注太贵怎么办？** 先做分歧 turn 检测（两轨迹第一次分叉），只标分叉后；全量 span 留给抽检。
