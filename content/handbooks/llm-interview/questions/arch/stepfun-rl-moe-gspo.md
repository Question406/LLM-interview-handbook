---
id: stepfun-rl-moe-gspo
section: arch
order: 144
level: S
title: 阶跃星辰：RL 训练 MoE 有什么问题，GSPO 怎么改进？
quick: "强化学习（RL）会改变生成 token 的分布，专家路由也随之变化，可能造成负载不均和训练、推理的路由差异。MoE 的专家切换还会放大 token 级重要性采样的方差。GSPO 让整段回答共享序列级比率，减轻局部比率突变对更新的影响。"
tags:
  - StepFun
  - MoE
  - GSPO
  - RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
  - title: GSPO
    url: https://arxiv.org/abs/2507.18071
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“RL训练MoE架构时的问题？怎么改进？问GSPO？”**

常见误区是：把 GSPO 说成「更好的 GRPO」或只复读「稀疏省算力」。回答要说明两点：RL 会改变路由分布，并放大 token 级重要性比率的方差；GSPO 则在序列（或组）级计算比率，减少局部比率突变造成的不稳定更新。细节以论文为准，见 arXiv 2507.18071。组内优势定义见 `stepfun-grpo-group-advantage`、`code-grpo`，不要和本题混成一道。

## 强化学习（RL） + MoE：策略更新会改变路由分布

MoE 的 top-$k$ 路由是 token 特征的函数。RL 更新后，同一输入提示下，生成 token 的语义、长度和格式都会变化，路由器可能把更多 token 分配给少数专家：训练时 capacity / drop 与推理 serving 的 expert parallel 不一致，出现训推路由错位，见 `sys-moe-train-infer-routing-mismatch`。负载均衡损失在监督微调（SFT）阶段可能还能控制专家分配，但随着 on-policy 采样分布变化，aux loss 往往不足以维持均衡。

重要性采样也会受到影响。PPO/GRPO 常用的 token 级比率为

$$
\rho_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)}.
$$

专家一切换，$\log\pi$ 可跳一个数量级，$\rho_t$ 随之突变。clip 可能将梯度截断，也可能未能阻止过大的更新。Dense 模型也会受到这种噪声影响；MoE 还会改变下一层路由器的输入，使误差逐层放大。改进不必先上新算法：冻结或部分冻结 router、加强负载均衡、训推同一套 routing 实现、减小更新步长、监控专家利用率。这些是工程兜底，见 `arch-moe-balance`、`byte-moe-rollout-routing-gspo`。

## GSPO：比率收到序列级，对齐「整段好不好」

GSPO 把重要性权重定义在序列（或组）上，而不是每个 token 各算各的 $\rho_t$。整段回答共享一个比率，再乘组内优势。这样，局部 token 因专家切换产生的比率突变不会单独引起过大的路由更新，也更符合基于可验证奖励的强化学习（RLVR）对整段回答是否正确的评价方式。它改的是 IS 的粒度，不取消 GRPO 的组内标准化，也不是 MoE 专用路由损失。面试承认超参与是否 sequence-level 几何平均以论文为准，但必须说清动机：token 比方差在 MoE 上被路由放大。

「序列级 KL / 序列级 clip」不必和 GSPO 商标绑死，同类思想在 CISPO 等变体里也有，见 `pt-cispo`。现场可以先解释 MoE+RL 的不稳定来源，再说明冻结 router 等工程措施，最后介绍 GSPO 对比率计算粒度的调整。

## 追问

- **GSPO 是更好的 GRPO 吗？** 两者解决的问题不同。GRPO 用组内均值作 baseline，省去价值评估模型（critic）；GSPO 调整重要性采样（IS）的粒度。两种设计可以结合使用。见 `pt-grpo`。
- **冻结 router 会不会学不动？** 早期防塌缩有效；后期专家功能要随政策变，可解冻并继续 aux loss。一刀切不是答案。
- **token 级 clip 为什么不够？** clip 只能把越界梯度置零，不能消灭「相邻 token 已走另一专家」造成的分布错位。方差来源在路由，不在 $\varepsilon$。
- **训推不一致具体指什么？** 训练 drop token / 不同 capacity，推理用另一套 expert parallel 或 top-$k$。同一 checkpoint 路由统计应对齐，见 `sys-moe-capacity-token-drop`。
- **和共享专家的关系？** 共享专家减轻「全靠路由」的脆弱性，但不能替代序列级 IS。DeepSeek 细粒度 MoE 仍会在 RL 时漂，见 `tencent-qwen-vs-deepseek`。
