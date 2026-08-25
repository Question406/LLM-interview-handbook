---
id: openai-test-time
section: openai
order: 29
level: S
title: OpenAI：test-time compute / 推理时搜索，公开层怎么讲，不编内部
quick: >-
  推理时算力是同一条链写长、或并行走多条再挑。公开杠杆是 CoT、self-consistency、Best-of-N、过程奖励打分；o1 博客只保证「多想涨点、RL
  训思考」，没给搜索器图纸。可验证题用测试/多数票，开放生成用 RM 会 overoptimize。别把隐藏思维当产品日志。
tags:
  - OpenAI
  - Test-time compute
  - Search
  - Reasoning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Learning to reason with LLMs
    url: https://openai.com/index/learning-to-reason-with-llms/
    type: primary
  - title: Let's Verify Step by Step
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: Scaling LLM Test-Time Compute Optimally
    url: https://arxiv.org/abs/2408.03314
    type: primary
  - title: Self-Consistency Improves Chain of Thought Reasoning
    url: https://arxiv.org/abs/2203.11171
    type: primary
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
---

## 题怎么来的

o1 的公开叙事是：用大规模 RL 教模型在回答前写一长段内部思维链；**训练算力**和 **思考时间** 两条轴都能涨分。OpenAI 没公布搜索算法、树宽、是否 MCTS。研究岗要听你把推理时计算讲成预算，用已发表的方法举例，并主动画边界。CoT 机制见 `google-cot-reason`；BoN 的 RM 分叉见 `align-best-of-n`。这不是隐藏面经。

我会先拆串行 / 并行两条，再讲怎么花 token，最后说哪些话不能说。

## 两条公开杠杆：写长，或采样再挑

令题目 $x$，答案 $y$，中间 token $z$。普通解码直接抽 $y$。推理时计算是在 $z$ 或候选 $y$ 上多花钱：

1. **串行加长。** 允许更长的 $z$：逐步推、回改、自我检查。墙钟跟生成长度走，prefill 一次，后面全是 decode，形态见 `openai-prefill-decode`。产品表现是 TTFT 变差——用户在等第一段可见输出。o1 博客把「多想」画成光滑曲线，但没说 $z$ 的采样器内部是 greedy 还是树。面试就说到「自回归多走了 $|z|$ 步」。
2. **并行多条。** Self-consistency：采 $N$ 条 CoT，对最终答案多数票。Best-of-N：同一 $\pi$ 抽 $N$ 条，用 RM / 测试 / 过程分挑一条。Let's Verify Step by Step 用过程奖励模型（PRM）给每一步打对错，再按步骤分搜或挑完整解；MATH 上过程监督明显好于只看最终对错的 ORM。这是 **已发表** 的 OpenAI 搜索，不要把它说成 o1 内部。

Snell 等人把预算在「把模型训大」和「同一模型多想」之间切开：简单题早停更划算，难题才该加采样。面试用这句话收：test-time 不是无脑 $N\to\infty$。

IOI 公开段落：他们采很多候选程序，用公开测试、模型自己生成的测试、以及一个学过的打分函数挑 50 个提交；随机提交会低一大截。这证明 **验证器 + 选择** 是推理时计算的一部分。仍然不是 MCTS 图纸。

$$
\hat y=\arg\max_{y_i,\; i\le N} s(x,y_i),\qquad
s\in\{\text{多数票},\; r_{\mathrm{ORM}},\; \prod_k r_{\mathrm{PRM}}(z_k)\}.
$$

可验证任务（数学最终数、单测）$s$ 接近真目标。开放对话只有 proxy RM，$N$ 大时 Gao 的 overoptimize：proxy 涨、gold 掉。长度偏差几乎一定出现。

## 预算、隐藏链、不要编的部分

计量分开报：准确率、平均 $|z|$、候选数 $N$、p95 延迟。只报「开了思考涨 4 点」是在藏十倍 decode。前缀 KV 可以在 $N$ 路之间共享，见 `openai-continuous-batching`；分叉后的 decode 仍近线性。

隐藏 CoT：o1 类产品不把原始思维给用户。评测和安全都按 **可见答案** 和内部探针，不要把摘要当黄金 SFT 标签。可见文本可以错、可以事后编理由；Let's Verify 才是对着步骤标签训的公开方法。

明确不讲：o1 的层数、是否过程 RM、树搜索宽度、思维链是否对用户策略梯度可见。评委追内部，就说「公开材料到 RL + 更长思考 + 竞赛里的候选选择为止」。把 DeepSeek R1、Tree-of-Thoughts 当 **对照文献** 可以，当 OpenAI 实现不行。

错法：说「推理时搜索就是 beam search」——beam 优化的是模型 logp，不是验证器；说 CoT 解锁了推理神经元；用带长思考的数字和别人的 0-shot 比还不声明预算。

工具循环是另一种 test-time：每步把环境观察买回来，见 `openai-tool-loop`、`openai-agent-rl`。那是和环境交互，不是纯在 token 树上搜。两者可以叠，别并成一个词。

## 追问

- **$N$ 和 $|z|$ 谁先加？** 答案空间离散、容易投票：先加 $N$。需要长证明、单条链会中途改主意：先加 $|z|$ 或过程分。Snell 的曲线按难度切，不要全局一个 $N$。
- **PRM 会不会也被 hack？** 会。步骤标签是人的过程监督，模型仍可写「看起来对」的步骤。要抽查步骤，不要只看最终准确率。
- **和训练算力怎么比？** o1 博客说两条都能涨。流量大、同一类题反复来，把能力训进权重更便宜；长尾竞赛题更适合推理时多花。
- **温度怎么办？** 要多样性才能让 $N$ 有意义；温度 0 的 64 路近重复。多数票题用采样，最终提交可以再 greedy 一遍干净格式。
