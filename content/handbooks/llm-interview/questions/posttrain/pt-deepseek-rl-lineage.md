---
id: pt-deepseek-rl-lineage
section: posttrain
order: 252
level: A
title: DeepSeek 从 R1 到 V3.2，公开的 RL 改了什么？MoE RL 差在哪？
quick: >-
  公开主线一直是 GRPO。R1 用规则奖励激励长思考；V3.2 把 reasoning、agent 和对齐并进一段 RL，加了无偏的 $k_3$、负样本
  mask 和 MoE 的 Keep Routing。MoE RL 比 Dense 多一条路由隙，先要让 sampling 和训练走同一组 expert。
tags:
  - DeepSeek
  - GRPO
  - MoE
  - R1
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: DeepSeek-V3
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
  - title: DeepSeek-V3.2
    url: 'https://arxiv.org/abs/2512.02556'
    type: primary
---

公开报告里 DeepSeek 的 RL 主线一直是 GRPO。R1 用规则奖励激励长思考；V3.2 把 reasoning、agent 和人类对齐并进同一段 RL，又加了三样稳住长训的东西：无偏的 $k_3$、负样本 mask，以及 MoE 专用的 Keep Routing。MoE RL 和 Dense 最大的差别，是 sampling 和训练可能走到不同的 expert 上。

先把名字理清，发布名和算法名对不上。V3 是 MoE 基座，R1 是在强基座上堆可验证的长思考，见 `kuaishou-v3-vs-r1`、`meituan-three-stage-v3-r1`。面试里一次问到 V3.2 或「V4」，就按**已发表的报告**讲，报告里没有的就直说没有。

## 时间轴上改了什么

最早是 DeepSeekMath 提出 GRPO：用组内相对优势，去掉 Critic，见 `pt-grpo`。

到 R1 / R1-Zero，用规则奖励激励长 chain of thought（CoT，即分步推理过程） 和自检。R1-Zero 从 base 直接做 RL，产品版 R1 仍然常用冷启动再 RL。它说明 RL 能激励推理行为，没说明 RL 能从零发明预训练里没有的知识，见 `pt-r1zero`、`pt-where-reasoning-comes-from`。

V3 有后训练，只是公开叙事的重心在 MLA、无辅助负载均衡、DualPipe 和 MTP，别把 V3 说成「没做 RL」。

V3.2（`2512.02556`）相对 V3.1-Terminus，架构上能看到的改动是 DeepSeek Sparse Attention（DSA）：lightning indexer 加细粒度的 token 选择，长上下文的算力从二次降到接近线性。RL 这边还是 GRPO，最常被追问的是三点。一是一段 RL 混三件事，reasoning、agent 和人类对齐放进同一个阶段，免得多阶段之间互相遗忘；reasoning 和 agent 用规则结果奖励加长度惩罚和语言一致性，开放任务用带题目级 rubric 的生成式 reward model（RM）。二是稳住长训，用 $\pi/\pi_{\mathrm{old}}$ 修正 $k_3$，让 KL 的梯度无偏，再把负优势、并且相对 sampling 策略 KL 过大的序列 mask 掉。数学域可以把 KL 调弱甚至去掉，这和 DAPO 去 KL 不矛盾，见 `xiaohongshu-grpo-drop-kl`、`ant-grpo-kl-vs-ppo`。三是 Keep Routing，sampling 时的 expert 路由在训练图上原样重放。

## MoE RL 和 Dense 差在哪

Dense 模型的 off-policy 问题主要来自 $\rho$ 和数值误差。MoE 多了一条**路由隙**：推理引擎和 trainer 的 top-$k$ 选择对不上，token 级的 $\rho$ 方差更大。比如同一个 token，sampling 时走的是一组 expert，训练重算时因为训推框架不一致、再叠加策略更新，走到了另一组，算出来的概率比其实是在两套不同的参数上比的，等于优化空间跳了一下。报告写从 V3-0324 起，Keep Routing 就是关键的一条。它和 R2 / R3 / GSPO 怎么分层见 `pt-r3-routing-replay`，训推路由不一致的一般讨论见 `sys-moe-train-infer-routing-mismatch`。

工程上优先做 Keep Routing、重算 logp，必要时用序列级 ratio。EP 的 all-to-all 是 throughput 问题，见 `sys-expert-parallel`，和 advantage 公式无关。GSPO、CISPO、SAPO 是别家的 clip 改法，除非对方拿的是 Qwen 或 MiniMax 的论文，别安到 DeepSeek 头上。

至于 V4，截至 2026-08，还没有一份把 RL 配方写清楚的官方 V4 报告。把 DSA、Keep Routing 或者内部传闻说成 V4 的内容，就是在编。

## 追问

**V3.2-Speciale 是另一种算法吗？**
公开的说法是同一套协议，堆了更多 RL 算力，损失（loss） 没换名字。

**Keep Routing 和 GSPO 谁先上？**
先对齐路由，再谈 ratio 的粒度。路由都错了，序列级的 $\rho$ 也是在错的专家上算出来的。

**和 ProRL 的长训怎么一起讲？**
V3.2 给的是在 MoE 上能 scale 的 GRPO 稳定办法；ProRL 讲的是临界区数据 × 探索 × 步数，见 `pt-prorl-scale-boundary`。
