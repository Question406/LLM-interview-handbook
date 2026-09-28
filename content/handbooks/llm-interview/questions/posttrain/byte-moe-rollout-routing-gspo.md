---
id: byte-moe-rollout-routing-gspo
section: posttrain
order: 101
level: S
title: 字节 27 暑期：MoE 的 rollout / 训练专家路由为何不一致？GSPO 怎么缓解？
quick: >-
  行为策略和训练策略的参数、精度、batching / 并行和随机性不同，都可能改掉 router top-k；token 级 ratio 再相乘会把这种
  mismatch 放大。GSPO 把重要性比和 clip 提到序列级，减轻 token 级路由漂移带来的不稳，但不替代版本对齐和路由诊断。
tags:
  - ByteDance
  - 2027 Summer Intern
  - MoE
  - GSPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节27暑期 大模型算法一面凉经分享（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/28b254940eb940189188d795f4606c52?urlSource=home-api
    type: candidate-first-hand
  - title: 'GSPO: Towards Scalable Reinforcement Learning for Language Models'
    url: https://arxiv.org/abs/2507.18071
    type: primary-paper
---
## 真题记录

- 公司：字节跳动
- 团队 / 岗位：大模型算法
- 届别 / 流程：27 届暑期实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GRPO在训练moe模型时候，出现rollout和训练的专家路由不一样的原因是什么，这个问题的解决方案有什么”**；追问：**“GSPO具体采取了什么方案缓解这个问题”**

这块容易把 GSPO 说成「强制 rollout 与训练走同一组专家」。GSPO 并不对齐路由；它降低的是 token 级重要性比在路由漂移下的爆炸。根因仍要先查版本、数值路径和并行拓扑。路由诊断全红时先修基建，再谈换算法，否则只是换一种方式把错误的 $\log\pi$ 平均进序列。

## 1. 路由为什么会对不上

MoE 的 top-$k$ 对 router logits 的微小扰动极度敏感。Rollout 引擎（推理）与 learner（训练）只要有一项不同，同一表面 token 就可能进不同 expert，进而 $\log\pi(y_t\mid x,y_{\lt t})$ 已经不是同一条计算图：

- checkpoint、tokenizer、router 配置不同步，典型是异步 RL 的 policy lag；
- BF16 与 FP8、不同 kernel、不同 batch 形状，改变 router 的数值；
- expert-parallel 拓扑、capacity overflow、drop / 重路由；训练侧有容量约束，推理侧没有，或反过来；
- sampling seed、dropout、非确定性交错。

任一差异都会让「行为策略」和「用于算 $\rho$ 的训练策略」名不副实。GRPO 假设 $\pi_{\mathrm{old}}$ 就是采样那条政策；路由一变，这个假设在 token 级先碎。先记录并对比两次前向的 router top-$k$、expert load、overflow 率，不要一上来就改 clip。

## 2. Token 级 ratio 如何把 mismatch 放大

GRPO 沿用 PPO 的逐 token 重要性比 $\rho_t=\pi_\theta(y_t\mid\cdot)/\pi_{\mathrm{old}}(y_t\mid\cdot)$，再与整段共享的 $\hat{A}$ 相乘。长序列上即使每步只偏一点，乘积

$$
\prod_t\rho_t=\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{old}}(y\mid x)}
$$

会漂得很远。个别 token 因路由切换出现极端 $\rho_t$，clip 只能事后削目标函数，梯度仍可能被少数位置主导。MoE 上这比 dense 更常见：失败表现是 KL 与 clip fraction 乱跳、训练 reward 涨但 router load 失衡、偶发 NaN。

优先修复仍是缩短 policy lag、统一路由实现和数值路径、固定容量与 drop 策略。能对齐当然应该对齐。GSPO 是在「推理与训练数值路径无法完美一致」时的算法层缓解，不是替代诊断。不要把 GSPO 当成「MoE RL 的开关」。

## 3. GSPO：序列级重要性比和序列级 clip

GSPO 用序列似然定义长度归一的重要性比，例如

$$
s(y)=\exp\Big(\frac1{|y|}\sum_t\log\frac{\pi_\theta(y_t\mid\cdot)}{\pi_{\mathrm{old}}(y_t\mid\cdot)}\Big),
$$

再对 $s(y)$ 做 sequence-level clip 后乘组优势。单个 token 的路由抖动被平均进整段，极端 $\rho_t$ 不再单独支配更新。它缓解的是 IS 估计在 token 级过脆，不是让两次前向的 expert 集合变相同。长度归一也减轻「越长乘积越炸」的偏置，但过长回复仍要用显式长度惩罚，不要指望 $1/|y|$ 自动解决灌水。

方法失败的场景：序列平均会掩盖局部灾难性路由错误，整段 $s(y)$ 看起来还好，个别关键 token 已经走错 expert。此时仍要 token 级诊断。对齐完全做不到、overflow 很严重时，先减并发、降量化，GSPO 救不了系统性算错的 logprob。

验收看 held-out reward、KL、router load 均衡和训练稳定性，四项一起看。只报「换了 GSPO 更稳」而给不出路由对比，面试官会认为你没做根因。

## 追问

- **强制两次路由相同行不行？** 推理与训练数值路径完全对齐成本很高，能做则做；但不能当唯一答案，因为异步和量化差往往消不掉。工程上对应 Keep Routing / Rollout Routing Replay，见 `pt-r3-routing-replay`。GSPO 不能替代这条。
- **GSPO 还要不要 token clip？** 论文卖点是序列级 clip；落地以实现为准。面试说清 clip 作用在 $\rho_t$ 还是 $s(y)$，不要混。
- **Dense 模型要不要 GSPO？** 长 CoT 上 token 级 ratio 同样会累积，MoE 只是更痛。不要把 GSPO 说成 MoE 专用补丁。
- **和 DAPO 什么关系？** DAPO 管动态采样和 clip 形状；GSPO 管 IS 的粒度。可以同时存在，解决的不是同一个失败。
