---
id: company-ant
section: companies
order: 9
level: A
title: 蚂蚁集团：大模型 / 智能体优化应重点准备什么？
quick: "我会把 直接偏好优化（DPO）、PPO、GRPO 怎么选，VeRL 的 采样轨迹（rollout） 账本，监督微调（SFT） 再切 强化学习（RL），以及金融数据跟安全，串成一条链来讲。手撕可能是 Beam Search 或者基础网络，光会 AI 补全不够。公开面经里还会追信贷意见、额度这类开放系统设计。"
tags:
  - Ant Group
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 26秋招蚂蚁金服大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e2585943c7874b3081b0878b646b6f01
    type: candidate-first-hand
  - title: 20260508蚂蚁集团大模型智能体优化算法一二面
    url: https://www.nowcoder.com/feed/main/detail/263bc804663b4a0aa7b312154d720817
    type: candidate-first-hand
  - title: 蚂蚁大模型llm算法日常实习面经
    url: https://www.nowcoder.com/feed/main/detail/c6aadaf60f9c431bbe0738e0c802dfd7
    type: candidate-first-hand
---

蚂蚁这边算法和平台工程会绑着问。我会训练，也得说清编排、账本、数据怎么服务信贷、风控这类任务。

## 准备主线

1. **算法选型**：同一岗位会连着问 直接偏好优化（DPO）、PPO、GRPO。我会按有没有成对偏好、有没有 验证器（verifier）、卡时预算来选，不会去背三份公式。
2. **强化学习（RL） 基建**：VeRL 的 `rollout.n`、global / micro batch 怎么决定每卡样本和 token 数。FlashAttention、ms-swift、Dify 我各准备一句话原理。
3. **数据与业务**：监督微调（SFT） 和 RL 两阶段各自解决什么。公开面经出现过「输入个人信息，输出信贷意见和额度」这类开放题，必须讲清数据、拆分、安全和可解释 奖励分数（reward）。
4. **手撕**：Beam Search 树、基础 PyTorch 网络、Hot100 中等题都出现过。

## 本手册真题卡

点击下面每条即可跳到对应题。

- 蚂蚁 26 秋招：VeRL 的 采样轨迹（rollout） 与 update batch 参数如何共同决定每卡样本数
- 现在做 LLM RL，面试会问哪些训练框架题？
- veRL 的 HybridEngine 解决什么？和 OpenRLHF 把 vLLM 单独拉一套有何不同？
- TRL / veRL / OpenRLHF 里为什么 clip fraction 会一直是 0？
- veRL 的 `use_dynamic_bsz` 和写死 micro-batch 有何不同？
- slime 的 rollout / global / micro batch 怎么对到 veRL 那套字段？
- slime 的 `--use-dynamic-batch-size` 和 veRL `use_dynamic_bsz` 怎么对？
- AI Infra 实习：训练完的权重怎么同步到推理引擎？
- 蚂蚁 26 秋招：如何用 PyTorch 构建 LLM token 预测的 Beam Search 树
- 蚂蚁智能体优化算法：如何介绍 DPO、PPO、GRPO 的选型
- 蚂蚁日常实习：资源受限时为何选用 DPO
- 蚂蚁：SFT 和 RL 两阶段各自解决什么
- 蚂蚁二面：如何训练一个能输出意见和额度的信贷系统
- 蚂蚁：Dense 和 MoE 有何区别，路由怎么做
- 蚂蚁：MoE 专家负载不均衡怎么解决，损失函数怎么改
- 蚂蚁：有了 Reward Model 为什么还需要 Critic
- 蚂蚁：DPO 的 loss 怎么写
- 蚂蚁：Agent 长期记忆如何存，历史很大时怎么查
- 蚂蚁：FlashAttention 原理是什么
- [[ant-rejection-sampling|蚂蚁：拒绝采样怎么做，真实采样数是否等于 rollout.n]]
- 蚂蚁：GRPO 的 KL 和 PPO 有何不同，K1/K2/K3 是什么
- 蚂蚁一面：PPO 的 KL 能改成交叉熵吗？
- Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？
- Forward / Reverse KL 后训练八股要准备哪些题？
- 蚂蚁：vLLM 如何做推理加速，PagedAttention 解决什么
- 蚂蚁：Claude Code 用 grep 不用 检索增强生成（RAG），二者有何差别
- 蚂蚁智能体应用一面：如何解决大模型幻觉？
- 蚂蚁一面：Skills 怎么写？Spring AI 的调用更像 Claude Code 还是别的 Harness？
- 蚂蚁：BM25 原理是什么，混合召回怎么接 RAG？
- 蚂蚁：没做过意图识别的话，可以怎么实现？
- 蚂蚁智能体优化一面：Dify 和 ms-swift 各解决什么问题？
