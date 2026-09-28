---
id: google-cot-reason
section: google
order: 22
level: A
title: Google：chain-of-thought 和推理时计算，面试怎么讲不神化
quick: >-
  CoT 是把中间步骤写成 token，用串行计算换正确率。PaLM 上它随规模出现，不是小模型突然会思考。推理时计算是多采样、多数票、更长短链，付的是
  token 和延迟。别说成模型在脑子里想；要讲分布、成本和忠实性。
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

Wei et al. 的 CoT 和 Wang et al. 的 self-consistency 都是 Google 的工作；PaLM 540B 把「规模上来之后 CoT 才明显」写进报告。Gemini 岗问这题，要把推理讲成计算，别讲成人格。学术榜上 CoT 怎么抬 MMLU 见 `google-eval-mmlu`。别把「思考模型」说成不可分析的魔法。

## CoT 是额外 token

普通解码：条件 $x$，直接抽答案 $y$。CoT：先抽中间 token $z$，再抽 $y$，即 $p(z,y\mid x)$。训练或 prompt 让 $z$ 看起来像步骤。机制上就是自回归多走了 $|z|$ 步，每步一次前向。

PaLM 的关键观察：小模型硬写「Let's think step by step」，数学题经常更差；到 540B，同样 prompt 才拉开。所以面试别说「CoT 是一种算法，任何模型打开就变强」。它是规模 + 数据里已经有步骤文本之后，被 prompt 或 SFT 引出来的行为。

写在纸上的步骤不必等于内部计算。模型可以先猜答案再编理由，也可以理由对、最后一行抄错。评测要看最终答案，也要抽查 $z$ 是否能在证据里定位。把 $z$ 当可审计的思考过程，产品上会踩忠实性。

## 推理时计算：同一条链加长，或并行走多条

Self-consistency：同一 prompt 采 $N$ 条 CoT，对最终答案多数票。PaLM 上这比贪心一条链稳。付的是 $N$ 倍 decode。这和投机解码不是一回事：投机是同一条轨迹上少跑大模型步数，见 `google-spec-decode`；这里是真的多花采样。

还可以把串行做长：允许更长 $z$、自我检查、多轮改错。墙钟跟生成长度走，prefill 只做一次，后面全是 decode。TPU 上 $B$ 小、MXU 吃不饱，见 `google-tpu-llm`。产品要画准确率对 token 预算的曲线，不要只报「开了思考」。

搜索式（对中间步打分再展开）是再往上的一层：过程奖励、MCTS。Google 面试能说到「那是用额外模型或规则买分支」，并承认多数产品还停在采样 + 投票，就够了。不要把未公开的 Gemini 内部搜索当事实讲。

蒸馏：把长 $z$ 压进小模型，见 `google-distill-llm`。学生若只学最终答案，推理时计算的红利留在教师那边。

计量上我会分开报：最终答案对不对、平均 $|z|$、每 1k token 的正确率增量。只报「开了 CoT 涨了 4 个点」，不报多花了多少 decode，评委不知道你是不是用十倍钱买的。

## 怎么讲才不像神化

边界：

- 多出来的是 token 和 FLOPs。
- 有的题 CoT 有害：分类、短事实、格式敏感的抽取，中间步骤引入噪声。
- 温度和 $N$ 是超参。$N$ 增大收益饱和，P99 延迟线性涨。
- 数学竞赛和日常助手不是同一条曲线。GSM8K 上 self-consistency 很香，不等于客服对话该默认 $N=32$。
- 安全：更长的 $z$ 给了更多越狱表面，也给了更多可检查的文本。两面都要测。

错法：说 CoT「解锁了推理神经元」；把 o1 / Gemini 思考版的产品名当论文机制；用带 CoT 的 MMLU 和别人的 0-shot 比，还不声明。

## 追问

- **训练时就写步骤，还是只在推理写？** 都可以。预训练语料里已经有解题过程；SFT / 蒸馏可以专门教格式。只在推理塞一句 prompt，便宜，但弱于在数据里见过步骤的模型。
- **为什么小模型 CoT 会掉点？** 步骤本身是新的生成任务，容量不够时 $z$ 先错，再把 $y$ 带错。PaLM 的规模拐点是经验观察，不是定理。
- **多数票会不会把错法投成对？** 会，如果错法众数。要看答案空间：整数题投票有效；开放生成没有干净票箱，要用验证器或测试。
- **和工具调用的关系？** 算术、代码、检索该走工具，不必全写在 $z$ 里。CoT 负责规划；工具负责可检查的执行。
