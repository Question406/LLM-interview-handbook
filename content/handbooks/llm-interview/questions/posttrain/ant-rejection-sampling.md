---
id: ant-rejection-sampling
section: posttrain
order: 160
level: A
title: 蚂蚁：rejection sampling 是怎么做的？真实 sampling 数一定等于 rollout.n 吗？
quick: >-
  rejection sampling 是对同一输入生成多条回答，用奖励、规则或验证器筛掉低分的，把通过的拿去做 SFT 或当正例。`rollout.n`
  只是尝试次数，不等于有效更新条数，过滤、超时、解析失败和 drop-last 都会让真实样本更少，账本要分开报。
tags:
  - Ant Group
  - Rejection Sampling
  - RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: 'https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339'
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“提到了 rejection sampling，详细讲一下”**；**“真实 sampling 数量一定等于 rollout 数量吗？”**

rejection sampling 就是先生成、再筛、再学：对同一个输入生成多条回答，用规则、reward model 或单测留下高分的，拿去做 SFT 或当正例。真实参与训练的样本数一般不等于配置里的 `rollout.n`，过滤、超时、drop-last 这些步骤都会把它削掉。

流程写成三步：$\pi$ 对 $x$ 采 $n$ 条 $\to$ 验证器给出分数或结构化的判定原因 $\to$ 通过阈值的样本写成 $(x,y^+)$。它便宜、稳定，不需要价值评估模型（critic），适合 SFT 冷启动，也就是 R1 叙事里中间穿插的那步「自己生成再学」。它不构造组相对优势，也不更新被丢掉的负例，所以能力上限被当前 sampling 分布和过滤器卡住。把它说成「便宜版 GRPO」就混了。

失败模式要主动讲。过滤器有洞，比如只跑样例测试、测试文件模型读得到，利用规则漏洞的样本就会被写进训练集。阈值太严，有效样本趋近于零，账上看起来采了很多，其实没更新。生成分布仍是当前 $\pi$，过滤器没见过的路径它探不到。所以 RS 替代不了 online RL：后者用相对优势把失败轨迹变成更新，前者直接把失败轨迹扔掉。

和 GRPO 的差别写在公式上就清楚了。GRPO 全组都进优势：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon},
$$

错的那几条拿到 $\hat A\lt 0$，提供往下压的信号；RS 只留正例，负例的信息量是零。整组全错时，RS 得到空集，GRPO 得到零梯度，两种情况不一样，都要报，也都不是加学习率能修好的。RS 的结果要是再拿去当 DPO 的 chosen，还得另造 rejected，不然又退化成单边 SFT。另外 GRPO 里的 $n$ 还是优势的定义域，$n=1$ 就没有组内均值，见 `sys-rl-group-n`，这和 RS 里的「尝试次数」是两个意思。

再说条数。`rollout.n` 只是每个 prompt 的生成上限。比如配置每题生成若干条，有的超时，有的解析失败，再被 packing 的 drop-last 切掉几条，真正进训练的就少了一截。未完成、超时、解析失败、packing drop-last、全组同奖励被丢、DAPO 动态丢掉全对全错组，都会削掉有效样本。所以账本要同时报尝试次数、有效轨迹、有效 token 数，必要时再报有效组比例。原帖还问了 rollout、batch 和卡数的关系：每张卡的 micro-batch 负责的是有效样本，和配置的 $n$ 不是一回事。GRPO 里同一 prompt 的 $n$ 条必须进同一次 advantage estimation，drop-last 把组切开，组均值就不是那 $n$ 条的了，估计器直接坏掉，见 `sys-rl-group-n`。Off-policy 复用旧轨迹时，过滤器和当前 $\pi$ 还会错位，那是 CISPO 这类权重问题，见 `pt-cispo`，把 $n$ 再开大也修不了。

## 追问

**RS 和 Best-of-N 有什么区别？**
Best-of-N 是推理时挑一条交差；RS 把挑中的写回训练集，训练分布会被过滤器塑造。评测要是还用同一个过滤器，结果会偏乐观。

**有效组是 0 怎么办？**
降难度、升温、放宽过滤或者开动态 sampling。别先加学习率，也别一上来把 $n$ 加到 64。

**有了 RS 为什么还要 RL？**
RS 不更新负例，也不探索过滤器以外的轨迹；GRPO / PPO 才能把失败轨迹变成梯度。

**和 CISPO 有关系吗？**
没关系。CISPO 改的是 off-policy IS 权重的截断，见 `pt-cispo`；RS 是数据过滤器。

**真实 sampling 数什么时候会大于 $n$？**
动态 sampling over-sample 时，名义尝试次数会超过配置的 $n$，但有效更新条数仍可能更少，两本账都要报。
