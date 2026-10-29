---
id: stepfun-rl-moe-gspo
section: arch
order: 144
level: S
title: 阶跃星辰：RL 训练 MoE 有什么问题，GSPO 怎么改进？
quick: >-
  RL 会改变生成 token 的分布，专家路由跟着漂，容易出现负载不均和训推路由不一致；专家一切换，token 级 importance ratio
  也会突变，方差被放大。GSPO 让整段回答共享一个序列级比率，局部比率的突变就不会单独拉出过大的更新。
tags:
  - StepFun
  - MoE
  - GSPO
  - RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3'
    type: candidate-first-hand
  - title: GSPO
    url: 'https://arxiv.org/abs/2507.18071'
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“RL 训练 MoE 架构时的问题？怎么改进？问 GSPO？”**

RL 训 MoE 的麻烦有两层：策略一更新，生成 token 的分布就变了，路由跟着漂；专家一切换，token 级的 importance ratio 又会突变，方差被放大。GSPO 的改法是把比率放到序列（或组）级，整段回答共享一个比率，减少局部比率突变带来的不稳定更新。它和 GRPO 解决的是不同的问题，说成「更好的 GRPO」不准确，只复读「稀疏省算力」也答不到点上。细节以论文为准，见 arXiv 2507.18071。组内优势的定义见 `stepfun-grpo-group-advantage`、`code-grpo`，那是另一道题，别混在一起讲。

## RL 加 MoE：策略更新会改变路由分布

MoE 的 top-$k$ 路由是 token 特征的函数。RL 更新之后，同一个 prompt 下，生成 token 的语义、长度和格式都会变，路由器可能把更多 token 分给少数几个专家。这时训练里的 capacity / drop 和推理 serving 的 expert parallel 对不上，就出现了训推路由错位，见 `sys-moe-train-infer-routing-mismatch`。负载均衡损失在 SFT 阶段可能还压得住专家分配，但随着 on-policy sampling 的分布变化，aux loss 往往不够用了。

importance sampling 也会受影响。PPO / GRPO 常用的 token 级比率是

$$
\rho_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)}.
$$

比如一段回答里，中间某个 token 换了一个专家，$\log\pi$ 可能跳一个数量级，$\rho_t$ 随之突变。clip 可能把梯度截掉，也可能没拦住过大的更新。Dense 模型也有这种噪声，但 MoE 还会改变下一层路由器的输入，误差逐层放大。

改进不一定先上新算法。冻结或部分冻结 router、加强负载均衡、训练和推理用同一套 routing 实现、减小更新步长、监控专家利用率，这些都是工程上的 safeguards，见 `arch-moe-balance`、`byte-moe-rollout-routing-gspo`。

## GSPO：把比率收到序列级

GSPO 把重要性权重定义在序列（或组）上，每个 token 不再各算各的 $\rho_t$。整段回答共享一个比率，再乘上组内优势。这样，某个 token 因为切换专家产生的比率突变，就不会单独引发过大的路由更新；这也更贴合 RLVR 按整段回答对不对来打分的方式。它改的是 IS 的粒度，GRPO 的组内 standardization 照样保留，它也不是 MoE 专用的路由损失。超参，以及是不是用 sequence-level 几何平均，面试时可以承认以论文为准，但动机一定要讲清楚：token 级比率的方差在 MoE 上被路由放大了。

「序列级 KL / 序列级 clip」也不必和 GSPO 这个名字绑死，同类思想在 CISPO 等变体里也有，见 `pt-cispo`。现场可以按这个顺序讲：先解释 MoE + RL 为什么不稳，再说冻结 router 等工程措施，最后讲 GSPO 怎么调整比率的计算粒度。

## 追问

**GSPO 是更好的 GRPO 吗？**
两者解决的问题不同。GRPO 用组内均值做 baseline，省掉价值评估模型（critic）；GSPO 调的是 importance sampling（IS）的粒度。两种设计可以一起用，见 `pt-grpo`。

**冻结 router 会不会学不动？**
早期用来防塌缩很有效。后期专家的功能要跟着策略变，可以解冻，继续加 aux loss。一刀切地冻结不是答案。

**token 级 clip 为什么不够？**
clip 只能把越界的梯度置零，消除不了「相邻 token 已经走了另一个专家」造成的分布错位。方差的来源在路由，调 $\varepsilon$ 解决不了。

**训推不一致具体指什么？**
训练时 drop token、用不同的 capacity，推理时又用另一套 expert parallel 或 top-$k$。同一个 checkpoint 的路由统计应该对得上，见 `sys-moe-capacity-token-drop`。

**和共享专家有什么关系？**
共享专家能减轻「全靠路由」的脆弱，但替代不了序列级 IS。DeepSeek 的细粒度 MoE 在 RL 时仍然会漂，见 `tencent-qwen-vs-deepseek`。
