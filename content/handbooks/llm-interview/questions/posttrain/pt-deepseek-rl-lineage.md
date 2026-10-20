---
id: pt-deepseek-rl-lineage
section: posttrain
order: 252
level: A
title: DeepSeek 从 R1 到 V3.2，公开的 RL 改了什么？MoE RL 差在哪？
quick: "公开主线一直是 GRPO。R1 用规则奖励激励长思考；V3.2 把 reasoning、agent 和对齐并进一段 RL，并加了无偏 $k_3$、负样本 mask 和 MoE 的 Keep Routing。"
tags:
  - DeepSeek
  - GRPO
  - MoE
  - R1
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: DeepSeek-V3
    url: https://arxiv.org/abs/2412.19437
    type: primary
  - title: DeepSeek-V3.2
    url: https://arxiv.org/abs/2512.02556
    type: primary
---

发布名不是算法名。V3 是 MoE 基座，R1 是在强基座上堆可验证长思考，见 `kuaishou-v3-vs-r1`、`meituan-three-stage-v3-r1`。面试若一次问到 V3.2 /「V4」，按**已发表报告**讲，缺的就说缺。

## 时间轴上改了什么

**DeepSeekMath / GRPO。** 组内相对优势，去掉 Critic，见 `pt-grpo`。

**R1 / R1-Zero。** 规则奖励激励长 思维链（CoT，即分步推理过程） 和自检。R1-Zero 从 base 直接 强化学习（RL）；产品 R1 仍常用冷启动再 RL。它说明 RL 能激励推理行为，不说明从零发明预训练里没有的知识，见 `pt-r1zero`、`pt-where-reasoning-comes-from`。

**V3。** 后训练存在，但公开叙事的重心是 MLA、无辅助负载均衡、DualPipe、MTP。不要把 V3 说成「没做 RL」。

**V3.2（`2512.02556`）。** 架构相对 V3.1-Terminus 的可见改动是 DeepSeek Sparse Attention（DSA）：lightning indexer + 细粒度 token 选择，长上下文算力从二次降到近似线性。RL 侧仍写 GRPO，额外三点最常被追：

1. **一段 RL 混三件事。** reasoning、agent、人类对齐并进同一阶段，避免多阶段互相遗忘。reasoning / agent 用规则结果奖 + 长度惩罚 + 语言一致性；开放任务用带题目级 rubric 的生成式 奖励模型（RM）。
2. **稳住长训。** 用 $\pi/\pi_{\mathrm{old}}$ 修正 $k_3$，让 KL 梯度无偏；对负优势且相对采样策略 KL 过大的序列做 mask。数学域可以弱 KL 甚至去掉，和 DAPO 去 KL 不矛盾，见 `xiaohongshu-grpo-drop-kl`、`ant-grpo-kl-vs-ppo`。
3. **Keep Routing。** 采样时的 expert 路由在训练图上重放。MoE 训推框架不一致、再叠加策略更新，同一输入会走到另一组 expert，等于优化空间跳变。报告写从 V3-0324 起这条就关键。和 R2 / R3 / GSPO 怎么分层见 `pt-r3-routing-replay`；训推路由不一致的一般讨论见 `sys-moe-train-infer-routing-mismatch`。

GSPO / CISPO / SAPO 是别人的 clip 改法，不要安到 DeepSeek 头上，除非对方拿的是 Qwen / MiniMax 论文。

## MoE RL 和 Dense 差在哪

Dense 的 off-policy 主要是 $\rho$ 和数值隙。MoE 多一条**路由隙**：引擎和 trainer 的 top-$k$ 对不上，token 级 $\rho$ 方差更大。工程上优先 Keep Routing、重算 logp、必要时序列级 ratio。EP 的 all-to-all 是吞吐问题，见 `sys-expert-parallel`，不是 advantage 公式。

**V4。** 截至 2026-08 没有把 RL 配方写清楚的官方 V4 报告。把 DSA、Keep Routing 或内部传闻说成 V4，是在编。

## 追问

- **V3.2-Speciale 是另一种算法吗？** 公开表述是同一套协议堆更多 RL 算力，不是换了 损失（loss） 名字。
- **Keep Routing 和 GSPO 谁先上？** 路由先对齐，再谈 ratio 粒度。路由都错了，序列级 $\rho$ 也是错专家上的数。
- **和 ProRL 长训怎么一起讲？** V3.2 给的是 MoE 上可 scale 的 GRPO 稳定术；ProRL 给的是临界区数据 × 探索 × 步数，见 `pt-prorl-scale-boundary`。
