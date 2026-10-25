---
id: google-cot-reason
section: google
order: 22
level: A
title: Google：chain-of-thought 和推理时计算，面试怎么讲不神化
quick: "CoT 把中间步骤写成 token，用额外生成计算换取答对的机会。推理时还可延长链或多采样投票，但收益取决于模型、任务和预算，要同时报正确率、token 成本、延迟与步骤忠实性。"
tags:
  - Google
  - Chain-of-Thought
  - Reasoning
  - Test-time compute
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
    url: https://arxiv.org/abs/2201.11903
    type: primary
  - title: Self-Consistency Improves Chain of Thought Reasoning in Language Models
    url: https://arxiv.org/abs/2203.11171
    type: primary
  - title: PaLM — Scaling Language Modeling with Pathways
    url: https://arxiv.org/abs/2204.02311
    type: primary
---

CoT 是让模型先生成中间步骤，再生成答案，因此增加了自回归计算。它在一些任务上能提高正确率，收益却取决于规模、数据和预算。比如同样一句“Let's think step by step”，PaLM 小模型做数学题可能更差，到 540B 才明显拉开效果；这是经验观察，不是所有模型都适用的定理。

普通解码在条件 $x$ 下直接生成 $y$，CoT 先生成中间 token $z$ 再生成 $y$，即 $p(z,y\mid x)$。Prompt、预训练里的解题文本或监督微调（SFT）让 $z$ 呈现步骤，机制上则多走 $|z|$ 次自回归前向。Wei et al. 的 CoT 和 Wang et al. 的 self-consistency 都是 Google 的公开工作。

要增加推理时计算，可以延长 $z$，允许自查、多轮改错，也可以对同一 prompt 采 $N$ 条链，对最终答案投多数票。Self-consistency 在 PaLM 上比贪心单链更稳，代价是约 $N$ 倍 decode。投机解码则是在同一轨迹上减少大模型调用，两者增加或节省的计算不同。更高一层搜索还会用过程奖励、MCTS，让额外模型或规则给分支打分；多数产品仍以采样和投票为主，不能把未公开 Gemini 内部搜索当事实。

延长链时 prefill 只做一次，后续主要是 decode，实际耗时随生成长度增加。TPU 上 $B$ 小时 MXU 也可能吃不满。产品应该画准确率随 token 预算的曲线，分别报最终正确率、平均 $|z|$ 和每 1k token 的正确率增量；只说 CoT 涨了 4 个点，无法判断是不是花了十倍成本。

步骤文本不保证忠实呈现内部计算，模型可能先猜答案再编理由，也可能过程正确、最后一行抄错。评测既看最终答案，也抽查 $z$ 是否有证据支持。长链增加可检查文本，同时扩大越狱表面，安全两面都要测。算术、代码、检索可交给工具，CoT 主要规划，工具执行更便于检查。

分类、短事实、格式敏感抽取可能因额外步骤引入噪声。温度和 $N$ 是超参，增加 $N$ 的收益会饱和，P99 延迟却随之线性增长。GSM8K 的效果不能直接套到客服，日常助手未必适合默认 $N=32$。数学整数答案便于投票，开放生成则需验证器或测试；若错误答案形成众数，多数票同样会错。

蒸馏可把长 $z$ 的能力压进小模型，若学生只学最终答案，教师推理时计算的收益未必传递。训练中用步骤、SFT 或蒸馏教格式，与推理时只加一句 prompt 的效果也不同，后者便宜但更依赖模型已有能力。产品名与“推理神经元”不能代替机制解释，带 CoT 的 MMLU 也应和 0-shot 分开报协议。

相关：`google-eval-mmlu`、`google-spec-decode`、`google-tpu-llm`、`google-distill-llm`
