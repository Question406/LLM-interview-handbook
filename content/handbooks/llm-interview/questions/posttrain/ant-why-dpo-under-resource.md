---
id: ant-why-dpo-under-resource
section: posttrain
order: 123
level: A
title: 蚂蚁日常实习：资源受限时为何选用 DPO？
quick: >-
  卡不够、推理并发也紧的时候，我会用 DPO。它不用同时占着 reward model、critic，也不用拉一大坨 online rollout，有比较稳的偏好对就能对齐。前提是偏好数据覆盖关键失败，且接受离线
  bias；若必须探索可验证推理或工具轨迹，仍应留给 GRPO / PPO。
tags:
  - Ant Group
  - DPO
  - Resource Constraints
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型llm算法日常实习面经
    url: https://www.nowcoder.com/feed/main/detail/c6aadaf60f9c431bbe0738e0c802dfd7
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型 LLM 算法日常实习
- 届别 / 流程：日常实习；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-31
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“场景下为什么选用DPO，卡和资源环境”**

这块容易只说「DPO 更简单、更好训」。我会先报资源账，再谈算法。PPO 通常要同时驻留 actor、reference、RM（或 verifier 服务）、critic，外加大量 online rollout；GRPO 可以弱化 critic，但仍吃每题 $n\gt 1$ 的采样和 verifier QPS，见 `sys-rl-group-n`。实习或业务试点常见约束是少量 GPU、排队长、不能长时间占推理集群。DPO 把问题收成离线偏好学习，训练图里主要是可训策略外加冻结参考，性价比才说得清。没报卡、没报能不能开 vLLM rollout，只说「简单」，账就没立住。

## 省掉的是采样环，不是数学

DPO 损失只含冻结 $\pi_{\mathrm{ref}}$ 与可训 $\pi_\theta$：

$$
\mathcal{L}=-\mathbb{E}\log\sigma\Big(\beta\big(\log\tfrac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\tfrac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\big)\Big).
$$

没有 online 采样、没有 GAE、没有组标准化，也就没有「有效组比例」这本账。显存和调度更简单，迭代周期短：改完偏好对就能再训一晚，不必排推理集群。当场景目标是风格、安全、拒答，或「在已有正确答案里选更好的」，且能构造 $(y_w,y_l)$ 时，它通常优于硬上 RLHF。数学上它仍来自反向 KL 约束的闭式解，见 `fund-kl-directions`，不是「没有正则的 pairwise CE」。$\beta$ 是偏离 ref 的温度，不是学习率，更不是省算力旋钮。

## 必须主动报的限制与升级条件

三件限制要自己讲：偏好对质量，覆盖不到的失败不会自己出现；长度 bias，总 logp 差偏向长 chosen；离线分布漂移，线上用户一变，间隔再漂亮也救不了。若卡其实够、verifier 可靠、任务需要没见过的推理链或工具路径，应升级 GRPO；需要价值估计或连续权衡再上 PPO。Clip / IS 变体（CISPO）解决的是已经在 rollout 之后的 off-policy 权重，见 `pt-cispo`，救不了「根本没有 rollout 预算」。回答里我会点名卡型号、单卡 batch、是否能开推理引擎，不背「DPO 省资源」。

## 追问

- **卡够了还用 DPO 吗？** 有稳定偏好、不需要探索时仍可用；一旦有 verifier，就该用 holdout 对比 GRPO，不要因为惯性停在离线。
- **为什么不先拒绝采样？** RS 仍要生成 $n$ 条再过滤，推理预算可能比离线 DPO 还贵，而且负例被扔掉。
- **$\beta$ 能不能当省算力旋钮？** 不能。$\beta$ 管贴 ref 的幅度，不管 GPU 小时。省算力靠去掉采样环，不靠拧 $\beta$。
- **一组偏好对算多少有效样本？** 一条 pair 对应一次间隔更新；不要和 GRPO 的 $n$ 条轨迹横向比「条数」。
- **没有 pair 只有规则？** 那就不是 DPO 的地盘。有规则就该走 verifier + GRPO，或先用规则造 pair 再承认这是弱监督。
