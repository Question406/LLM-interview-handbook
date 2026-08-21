---
id: ant-rejection-sampling
section: posttrain
order: 160
level: A
title: 蚂蚁：拒绝采样是怎么做的？真实采样数一定等于 rollout.n 吗？
quick: >-
  拒绝采样按奖励或 verifier 丢掉低分轨迹，只把通过的样本再 SFT / 当正例。`rollout.n` 是尝试次数，不等于有效更新条数；过滤、超时和
  drop-last 都会让真实样本更少。
tags:
  - Ant Group
  - Rejection Sampling
  - RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“提到了拒绝采样，详细讲一下”**；**“真实采样数量一定等于rollout数量吗？”**

陷阱是把配置里的 `rollout.n` 当成会计数字，或把拒绝采样说成「便宜版 GRPO」。拒绝采样是 **先滤再克隆**：同一 prompt 生成多条，用规则、RM 或单测留下高分，再拿去 SFT 或当正例。它不构造组相对优势，也不更新被丢掉的负例，能力被当前采样分布和过滤器上限卡住。`n` 在 GRPO 里还是优势的定义域——$n=1$ 没有组内均值，见 `sys-rl-group-n`——和 RS 的「尝试次数」不要记成同一本账。原帖连问真实采样数是否等于 rollout 数，标准答案是：一定不等于。

## 拒绝采样做什么、不做什么

流程写成三步：$\pi$ 对 $x$ 采 $n$ 条 $\to$ verifier 打标量或结构化原因 $\to$ 过阈的写成 $(x,y^+)$。它便宜、稳定、省 critic，适合 SFT 冷启动和 R1 叙事里中间穿插的「自己生成再学」。失败模式要主动讲：过滤器有洞（样例测试、可读测试文件）就会把 hack 克隆进训练集；阈值过严则有效样本趋零，账上看起来「采了很多」其实没更新；生成分布仍是当前 $\pi$，探不到过滤器没见过的路径。所以 RS **不能替代** online RL：后者用相对优势更新失败轨迹，前者直接扔掉它们。

和 GRPO 的差别写在公式上。GRPO 全组都进

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon},
$$

错的那几条提供 $\hat A\lt 0$。RS 只留正例，负例的信息量为零。整组全错时 RS 得到空集，GRPO 得到零梯度，病状不同、都要报，都不能靠加学习率修好。RS 若再拿去当 DPO 的 chosen，还要另造 rejected，否则又退化成单边 SFT。

## 真实条数 $\neq$ 配置里的 $n$

`rollout.n` 只是每 prompt 的生成上限。未完成、超时、解析失败、packing drop-last、全组同奖励被丢、DAPO 动态丢掉全对全错组，都会把有效样本削下去。账本要同时报 **尝试次数、有效轨迹、有效 token**，必要时再报有效组比例。原帖还问 rollout、batch 和卡数的关系：对每卡 micro-batch 负责的是有效样本，不是配置 $n$。GRPO 场景里同一 prompt 的 $n$ 条必须进同一次优势估计，drop-last 把组切开，组均值就不是那 $n$ 条，估计器坏了，见 `sys-rl-group-n`。Off-policy 复用旧轨迹时，过滤器和当前 $\pi$ 还会错位，那是 CISPO 一类权重问题，见 `pt-cispo`，不是把 $n$ 再开大能修的。

## 追问

- **RS 和 Best-of-N 呢？** Best-of-N 是推理时选一条交差；RS 把选中的写回训练集，训练分布会被过滤器塑造，评测若用同一过滤器会乐观。
- **有效组为 0 怎么办？** 降难度、升温、放宽过滤或开动态采样，不要先加学习率，也不要先加 $n$ 到 64。
- **为什么还要 RL？** RS 不更新负例，也不探索过滤器外的轨迹；GRPO / PPO 才能把失败轨迹变成梯度。
- **和 CISPO 有关吗？** 无关。CISPO 改的是 off-policy IS 权重截断，见 `pt-cispo`；RS 是数据过滤器。
- **真实采样数什么时候会大于 $n$？** 动态采样 over-sample 时名义尝试会超过配置 $n$，但有效更新条数仍可能更少，两本账都要报。
