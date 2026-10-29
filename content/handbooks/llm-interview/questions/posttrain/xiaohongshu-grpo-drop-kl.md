---
id: xiaohongshu-grpo-drop-kl
section: posttrain
order: 122
level: S
title: 小红书大模型实习：GRPO 为何可以去掉 KL？Reward 怎么设？
quick: "去 KL 是强可验证奖励下的工程取舍：组内相对优势已经给了稳定基线，有人会减弱或去掉对 ref 的 KL 来放开探索，代价是格式崩和语言漂移。Reward 要能程序化复核（任务成功、格式、安全），同时盯 KL、熵和崩坏率，决定要不要把约束加回来。"
tags:
  - Xiaohongshu
  - GRPO
  - KL
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4
    type: candidate-first-hand
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary-paper
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary-paper
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“讲一下论文里的 GRPO 算法原理，为什么去掉 KL 散度，reward function 怎么设置”**

去 KL 是强可验证奖励下的一个工程取舍，DeepSeekMath 原文并没有推出这个结论。这题是三问，我会分三层答：GRPO 用组相对优势替代 Critic；KL 是把策略锚在 reference 上的护栏；奖励分数（reward）的定义要能复核，因为 KL 去掉以后，拉住策略的就只剩它了。最容易答坏的方式，是把「去 KL」讲成定理，或者把三问搅成一句「组内对比所以不需要约束」。

## GRPO 原理：组相对优势也是一种基线

对同一个 prompt sampling 一组输出，用组内 standardization 后的优势做 clipped policy gradient，这样就弱化了对 value model 的依赖。组相对 baseline 提供的是局部对比信号，这是它和 PPO+critic 的主要差别。clip 还在，ratio 过大照样会被裁。没有 critic 也不等于没有约束：reward 噪声大的时候，组内排序本身就会漂。公式和方差问题见 `pt-grpo`、`pt-grpo-variance`。

## 「去 KL」是取舍，探索不是白来的

KL 把 $\pi_\theta$ 锚在 SFT/ $\pi_{\mathrm{ref}}$ 上，抑制偏离和格式崩。如果任务奖励非常可靠，比如有可执行的验证器（verifier），而你更在意探索更长的推理链，那固定 $\beta$ 的 token 级 KL 就会拖慢、甚至压扁有用的探索。DAPO 等后续工作也讨论过减弱显式 KL，改用 sampling 和 clip 来管更新。

风险要同时讲清楚。比如训一个数学模型，去掉 KL 后训练 reward 一路涨，可抽几条看，推理段开始中英混杂、反复写同一句话，最后的答案格式倒是对的。这就是钻奖励规则空子、重复、乱码、语言漂移。实际常用的办法是动态 $\beta$、阶段性关闭，或者只在格式和安全这几维保留硬约束，再看熵、崩坏率和 holdout 成功率决定要不要加回来。相关卡：`gaode-dapo-no-kl`、`ant-grpo-kl-vs-ppo`。

## Reward 要能复核，过程分别看「像不像 CoT」

优先用规则和环境反馈：最终任务成功、格式能解析、安全不变量。过程分只覆盖能观测到的里程碑，比如编译过了、单测由红变绿、工具返回合法，不可验证的 chain of thought（CoT）文本不能直接当正确过程来奖励。credit assignment 要能解释到关键的错误步，再用反例集检查 hacking，比如空实现、恒真断言、把拒绝说成成功。主信号必须能程序化复核，LLM-as-judge 最多当辅助。去掉 KL 之后，奖励定义一松，熵和语言马上就会漂。

## 追问

**论文原文一定去 KL 吗？**
不一定。DeepSeekMath 的 GRPO 仍然可以带 KL，去掉是后续的工程选择。

**没有 KL 了，还要不要 clip？**
要。clip 管单步更新的幅度，KL 管相对 reference 的整体偏离，两个旋钮管的不是一件事。

**开放对话能不能去 KL？**
通常不行。奖励不可靠的时候，KL 往往是唯一还在的护栏。

**怎么决定把 KL 加回来？**
熵骤降、格式崩坏率上升、holdout 往下掉而训练 reward 还在涨，这时先加回约束或硬格式门，别继续加大探索。
