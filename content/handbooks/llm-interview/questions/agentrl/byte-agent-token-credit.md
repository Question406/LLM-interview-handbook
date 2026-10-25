---
id: byte-agent-token-credit
section: agentrl
order: 100
level: S
title: 字节 27 暑期：Agent 行为分数怎样落到 token 上？
quick: "环境一般在完整动作或轨迹结束后才给分。训练时先在 action 或 completion 这一层估计优势，再分给这个动作里模型生成的 token；prompt、工具返回和 padding 全部 mask 掉，不算策略 loss。这只是归因方式，每个 token 并没有自己的真实奖励。"
tags:
  - ByteDance
  - 2027 Summer Intern
  - Agent RL
  - Credit Assignment
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
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

分数先在 action 或整条轨迹这一层算出优势，再广播到这个 action 里策略生成的那些 token 上；prompt、工具返回和 padding 都 mask 掉，不进策略 loss。每个 token 并没有自己的真实奖励，面试官想听的是 credit 落在哪个粒度、mask 边界划在哪。这和 `arl-credit`、`xiaohongshu-credit-assignment` 是同一条线，只是字节这一问落到了反传的实现上。

矛盾在于环境通常只在一个完整 action 或整条轨迹结束后给一个标量，而语言模型的 $\sum_t \log\pi(a_t)$ 是逐 文本处理单位（token） 算的。所以我会先分三层讲清楚，再写 损失（loss）。第一层是环境分数，它出现在 trajectory、semantic step 或完整 tool action 之后，记作 $R$ 或 $r_k$。第二层在同样的粒度上估优势，整段 completion 一个 $A$，或者每个 tool-call 一个 $A_k$，用 GAE、return-to-go 或组相对都可以。第三层才落到 token：把 $A_k$ 赋给这个 action 内部、由策略生成的那些 token，代入 PG 或 PPO/GRPO 的 surrogate，再按 mask 求和或平均。

举个例子，一步里模型先写了一段 Thought，再输出一个搜索调用的 JSON，环境执行后返回结果。这一步拿到的 $A_k$ 由 Thought 和 JSON 的 token 共享，返回结果的 token 一点梯度都不拿。要 mask 掉的有 system / user 的 输入提示（prompt）、tool result 也就是 观测结果（observation）、padding，以及 harness 插进来的非策略文本。这些 token 跟 $\pi_\theta$ 没有因果关系，算进去只会污染梯度。Observation 属于 $s$，不属于 $a$，`arl-gui-observation` 里也是这个原则。mask 要是漏了工具回包，模型会去「背答案」，学不会调用。

广播还会带来长度问题。长 action 会让 credit 变粗；token 平均和 sequence 平均会改变长度权重，平均会打压长调用，求和会鼓励啰嗦。所以报结果时要写清楚归一化口径和长度分布，不然容易把 length effect 当成能力。

步数一多，整段 $A$ 刷到所有生成 token 上，方差大，归因也糊。可以在可验证的 checkpoint 给 step-level 的 $r_k$，再用 GAE 传到 token；也可以用 GRPO 在同一任务的多条轨迹之间比，不依赖绝对的 $0/1$；还可以做反事实 replay，验证某一步是不是真的改变了终局，见 `arl-hindsight`。诊断时我会看三样：去掉 observation 之后它的梯度是不是真为零；把 JSON 空白等价改写以后，$A$ 稳不稳；按 action 长度分组统计的回报。

## 追问

**Thought 和 tool JSON 要不要分开打分？**
默认同一步共享 $A_k$。没有逐步 oracle，就别给 思维链（CoT，即分步推理过程） 单独打「漂亮分」，那是 hacking。

**Token 平均还是 sequence 平均？**
两者会改变长度权重。先固定一种，再按长度分组看回报，没声明的情况下别两套混着报。

**Observation 漏进 loss 会怎样？**
模型会背工具返回里的答案，线上一换环境就崩。这是数据泄漏，算不上能力。

**和过程奖励是什么关系？**
过程分先定义在 step 或事件上，再按这题的方式广播到 token。别跳过事件层，直接给每个字打分。
