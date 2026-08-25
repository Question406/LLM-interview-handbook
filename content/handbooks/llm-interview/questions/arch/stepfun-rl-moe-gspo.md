---
id: stepfun-rl-moe-gspo
section: arch
order: 144
level: S
title: 阶跃星辰：RL 训练 MoE 有什么问题，GSPO 怎么改进？
quick: >-
  RL 会改变 token 分布，路由跟着漂，专家负载和训推路由容易错位；token 级重要性采样在 MoE 上方差更大。GSPO
  把比率收到序列级，减轻逐 token 比把路由冲垮。
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

这块容易把 GSPO 说成「更好的 GRPO」或只复读「稀疏省算力」。这题要两句话：问题在路由漂移 + token 级重要性比率方差；GSPO 把比率收到序列（或组）级，减轻逐 token 比把专家冲垮。细节以论文为准，见 arXiv 2507.18071。组内优势定义见 `stepfun-grpo-group-advantage`、`code-grpo`，不要和本题混成一道。

## RL + MoE：政策一变，路由器跟着漂

MoE 的 top-$k$ 路由是 token 特征的函数。RL 更新后，同一 prompt 的 token 语义、长度、格式都会变，路由器把流量抽向少数专家：训练时 capacity / drop 与推理 serving 的 expert parallel 不一致，出现训推路由错位，见 `sys-moe-train-infer-routing-mismatch`。负载损失在 SFT 阶段还能撑住，on-policy 采样一拉开，aux loss 往往跟不上。

更刺的是重要性采样。PPO/GRPO 常用 token 级

$$
\rho_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)}.
$$

专家一切换，$\log\pi$ 可跳一个数量级，$\rho_t$ 尖刺，clip 要么把梯度掐死，要么放行爆炸更新。对 Dense 模型这只是 creditable 噪声；对 MoE 它还会改下一层的路由输入，误差沿层放大。改进不必先上新算法：冻结或部分冻结 router、加强负载均衡、训推同一套 routing 实现、减小更新步长、监控专家利用率。这些是工程兜底，见 `arch-moe-balance`、`byte-moe-rollout-routing-gspo`。

## GSPO：比率收到序列级，对齐「整段好不好」

GSPO 把重要性权重定义在序列（或组）上，而不是每个 token 各算各的 $\rho_t$。整段回答共享一个比率，再乘组内优势。这样局部 token 因专家切换产生的尖刺不会单独把 router 撕开，也更贴 RLVR「整段对不对」的奖励。它不是把 GRPO 的组内标准化取消，也不是 MoE 专用路由损失；是改 IS 的粒度。面试承认超参与是否 sequence-level 几何平均以论文为准，但必须说清动机：token 比方差在 MoE 上被路由放大。

不要把「序列级 KL / 序列级 clip」和 GSPO 商标绑死，同类思想在 CISPO 等变体里也有，见 `pt-cispo`。现场我会先承认 MoE+RL 的病，再给冻结 router 等便宜药，最后才说 GSPO 改的是比率粒度。

## 追问

- **GSPO 是更好的 GRPO 吗？** 不是同一轴。GRPO 改 baseline（组内均值、不训 critic）；GSPO 改 IS 粒度。可以叠，不要互相替代。见 `pt-grpo`。
- **冻结 router 会不会学不动？** 早期防塌缩有效；后期专家功能要随政策变，可解冻并继续 aux loss。一刀切不是答案。
- **token 级 clip 为什么不够？** clip 只能把越界梯度置零，不能消灭「相邻 token 已走另一专家」造成的分布错位。方差来源在路由，不在 $\varepsilon$。
- **训推不一致具体指什么？** 训练 drop token / 不同 capacity，推理用另一套 expert parallel 或 top-$k$。同一 checkpoint 路由统计应对齐，见 `sys-moe-capacity-token-drop`。
- **和共享专家的关系？** 共享专家减轻「全靠路由」的脆弱性，但不能替代序列级 IS。DeepSeek 细粒度 MoE 仍会在 RL 时漂，见 `tencent-qwen-vs-deepseek`。
