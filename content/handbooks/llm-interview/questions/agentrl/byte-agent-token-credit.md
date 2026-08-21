---
id: byte-agent-token-credit
section: agentrl
order: 100
level: S
title: 字节 27 暑期：Agent 行为分数怎样落到 token 上？
quick: >-
  环境通常只对完整 action 给分，训练时可把 action / completion 级 advantage 广播到对应的可训练 token；tool result、prompt
  和 padding 要 mask。关键是先说明 credit 的粒度与因果边界，不要把环境分数误当成每个 token 的独立真值。
tags:
  - ByteDance
  - 2027 Summer Intern
  - Agent RL
  - Credit Assignment
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 字节27暑期 大模型算法一面凉经分享（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/28b254940eb940189188d795f4606c52?urlSource=home-api
    type: candidate-first-hand
---
## 真题记录

- 公司：字节跳动
- 团队 / 岗位：大模型算法
- 届别 / 流程：27 届暑期实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“针对Agent行为打分，在反向传播的时候，具体到token分数是怎么计算的”**

这题容易答成「每个 token 都有自己的真实奖励」。环境通常只在完整 action / 轨迹结束后给一个标量，语言模型的 $\sum_t \log\pi(a_t)$ 却是逐 token。面试官要听的是 **credit 粒度与 mask 边界**，不是发明 per-token 真值。和 `arl-credit`、`xiaohongshu-credit-assignment` 同一条线，只是字节这问落到反传实现。

## 先定分数在哪一层，再广播到可训练 token

我会先切三层，不要一上来写 loss：

1. **环境分数** 出现在 trajectory、semantic step 或完整 tool action 之后，记为 $R$ 或 $r_k$。
2. **优势** 在同一粒度估计：整段 completion 一个 $A$，或每个 tool-call 一个 $A_k$（GAE / return-to-go / 组相对）。
3. **落到 token：** 把 $A_k$ 赋给该 action 内部、策略生成的那些 token 的 PG 或 PPO/GRPO surrogate，再按 mask 求和或平均。

Mask 必须关掉：system / user prompt、tool result / observation、padding、以及 harness 插入的非策略文本。这些 token 没有 $\pi_\theta$ 的因果贡献，反传会污染。Observation 属于 $s$，不属于 $a$，见 `arl-gui-observation` 里同一原则。

广播的含义是：同一步里的 Thought 与 JSON 共享同一个 $A_k$，**不是**每个 token 独立测到了环境奖励。长 action 会让 credit 变粗；token 平均与 sequence 平均会改变长度权重——平均会打压长调用，求和会鼓励啰嗦。报告时必须写清归一化口径和长度分布，避免把 length effect 当能力。

## 长 horizon 不要只靠一层广播

步数多时，整段 $A$ 刷到所有生成 token，方差大、归因糊。可加：

- 在可验证 checkpoint 给 step-level $r_k$，再用 GAE 传到 token；
- GRPO 在同任务多条轨迹间比，不依赖绝对 $0/1$；
- 反事实 replay 验证某 step 是否真改变终局，见 `arl-hindsight`。

诊断看：去掉 observation 的梯度是否真为零；等价改写 JSON 空白后 $A$ 是否稳定；按 action 长度分桶的回报。mask 漏了 tool 回包，模型会「背答案」而不是学调用。

面试收口：环境分在 action / 轨迹级；优势广播到该 action 的可训练 token；prompt、tool 结果、padding 全 mask。这不是 per-token 真值。长链用 step reward 或组相对改善归因，并报 mask 与长度口径。

## 追问

- **Thought 和 tool JSON 要不要不同分？** 默认同一步共享 $A_k$。没有逐步 oracle 就不要给 CoT 单独「漂亮分」，那是 hacking。
- **Token 平均还是 sequence 平均？** 会改长度权重。先固定一种，按长度分桶看回报；不要在没声明的情况下两套混报。
- **Observation 漏进 loss 会怎样？** 模型背工具返回里的答案，线上换环境即崩。这是数据泄漏，不是能力。
- **和过程奖励的关系？** 过程分先定义在 step / 事件上，再按本题广播到 token。不要跳过事件层直接给每个字打分。
