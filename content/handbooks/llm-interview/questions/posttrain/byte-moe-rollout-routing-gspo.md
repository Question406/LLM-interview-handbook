---
id: byte-moe-rollout-routing-gspo
section: posttrain
order: 101
level: S
title: 字节 27 暑期：MoE 的 rollout / 训练专家路由为何不一致？GSPO 怎么缓解？
quick: >-
  行为策略和训练策略的参数、精度、batching / 并行和随机性只要有一项不同，就可能改掉 router 的 top-k，token 级 ratio
  一连乘又把这种 mismatch 放大。GSPO 把重要性比和 clip 提到序列级并做长度归一，减轻 token
  级路由漂移带来的不稳，但它不对齐路由，替代不了版本对齐和路由诊断。
tags:
  - ByteDance
  - 2027 Summer Intern
  - MoE
  - GSPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节27暑期 大模型算法一面凉经分享（候选人原帖）
    url: >-
      https://www.nowcoder.com/feed/main/detail/28b254940eb940189188d795f4606c52?urlSource=home-api
    type: candidate-first-hand
  - title: 'GSPO: Towards Scalable Reinforcement Learning for Language Models'
    url: 'https://arxiv.org/abs/2507.18071'
    type: primary-paper
---
## 真题记录

- 公司：字节跳动
- 团队 / 岗位：大模型算法
- 届别 / 流程：27 届暑期实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GRPO 在训练 moe 模型时候，出现 rollout 和训练的专家路由不一样的原因是什么，这个问题的解决方案有什么”**；追问：**“GSPO 具体采取了什么方案缓解这个问题”**

路由对不上，是因为 MoE 的 top-$k$ 对 router logits 的微小扰动极其敏感，而 rollout 引擎和训练 learner 在参数版本、数值精度、batching 和并行拓扑、随机性上总有差异；token 级重要性比一连乘，又把这点差异放大成训练不稳。GSPO 把重要性比和 clip 提到序列级，单个 token 的路由抖动被平均进整段，所以更稳。它并没有强制 rollout 和训练走同一组专家，根因仍要先查版本、数值路径和并行拓扑。

先说为什么对不上。推理和训练只要有一项不同，同一个表面 token 就可能进不同的 expert，$\log\pi(y_t\mid x,y_{\lt t})$ 算的已经不是同一条计算图了。常见的差异有这几类：checkpoint、tokenizer、router 配置不同步，典型的是异步 RL 里的 policy lag；BF16 和 FP8、不同的 kernel、不同的 batch 形状，改变了 router 的数值；expert-parallel 拓扑、capacity overflow、drop 和重路由，训练侧有容量约束、推理侧没有，或者反过来；sampling seed、dropout、非确定性的交错执行。任何一项都会让「行为策略」和「用来算 $\rho$ 的训练策略」名不副实。GRPO 假设 $\pi_{\mathrm{old}}$ 就是 sampling 的那个策略，路由一变，这个假设在 token 级就不成立了。所以第一步是记录并对比两次前向的 router top-$k$、expert load 和 overflow 率，别一上来就改 clip。

再说 token 级 ratio 怎么放大问题。GRPO 沿用 PPO 的逐 token 重要性比 $\rho_t=\pi_\theta(y_t\mid\cdot)/\pi_{\mathrm{old}}(y_t\mid\cdot)$，再乘上整段共享的 $\hat{A}$。长序列上就算每一步只偏一点，乘积

$$
\prod_t\rho_t=\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{old}}(y\mid x)}
$$

也会漂得很远。个别 token 因为路由切换出现极端的 $\rho_t$，clip 只能事后削目标函数，梯度仍可能被少数几个位置主导。MoE 上这比 dense 常见，表现是 KL 和 clip fraction 乱跳、训练奖励分数（reward）在涨但 router load 失衡、偶发 NaN。

所以优先修的仍是基建：缩短 policy lag，统一路由实现和数值路径，固定容量和 drop 策略，能对齐就对齐。GSPO 是推理和训练的数值路径没法完美一致时，在算法层做的缓解，别把它当成「MoE RL 的开关」。路由诊断显示严重异常时先修基建，再谈换算法，否则只是换一种方式把错误的 $\log\pi$ 平均进序列。

GSPO 用序列似然定义一个长度归一的重要性比，例如

$$
s(y)=\exp\Big(\frac1{|y|}\sum_t\log\frac{\pi_\theta(y_t\mid\cdot)}{\pi_{\mathrm{old}}(y_t\mid\cdot)}\Big),
$$

再对 $s(y)$ 做 sequence-level clip，然后乘组优势。单个 token 的路由抖动被平均进整段，极端的 $\rho_t$ 不再单独支配更新。它缓解的是 IS 估计在 token 级太脆，两次前向的 expert 集合并没有变得一样。长度归一也减轻了「序列越长、乘积比方差越大」的偏置，但过长回复还是要用显式长度惩罚，别指望 $1/|y|$ 自动解决灌水。

它也有失败的时候。序列平均会掩盖局部的灾难性路由错误：整段 $s(y)$ 看着还好，个别关键 token 已经走错了 expert，这时仍要做 token 级诊断。对齐完全做不到、overflow 又很严重时，先减并发、降量化，GSPO 救不了系统性算错的 logprob。验收要把 held-out reward、KL、router load 均衡和训练稳定性四项一起看。只报「换了 GSPO 更稳」、拿不出路由对比，面试官会认为你没做根因分析。

## 追问

**强制两次路由一样行不行？**
能做就做，但推理和训练的数值路径完全对齐成本很高，异步和量化带来的差异往往消不掉，所以它不能当唯一答案。工程上对应 Keep Routing / Rollout Routing Replay，见 `pt-r3-routing-replay`，GSPO 替代不了这条。

**用了 GSPO 还要 token 级 clip 吗？**
论文的卖点是序列级 clip，落地以实现为准。面试时说清 clip 作用在 $\rho_t$ 上还是 $s(y)$ 上，别混。

**Dense 模型要不要 GSPO？**
长 chain of thought（CoT，即分步推理过程）上 token 级 ratio 一样会累积，MoE 只是更痛。别把 GSPO 说成 MoE 专用补丁。

**和 DAPO 什么关系？**
DAPO 管动态 sampling 和 clip 的形状，GSPO 管 IS 的粒度。两者可以同时用，解决的不是同一个失败。
