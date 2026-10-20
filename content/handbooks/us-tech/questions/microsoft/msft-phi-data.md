---
id: msft-phi-data
section: microsoft
order: 11
level: S
title: Microsoft：Phi「教科书数据」质量 vs 规模，污染和评测切片
quick: >-
  Phi 不是「小模型魔法」，是把数据质量当成缩放轴：过滤网文、合成教材、课程式加码。面试要能讲污染（n-gram、教师泄漏、改写）和评测切片（公开榜 / 新鲜题 / 去污后），不要背一组 MMLU 当结案。
tags:
  - Microsoft
  - Phi
  - Data Quality
  - Contamination
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Textbooks Are All You Need
    url: https://arxiv.org/abs/2306.11644
    type: primary
  - title: Textbooks Are All You Need II
    url: https://arxiv.org/abs/2309.05463
    type: primary
  - title: Phi-3 Technical Report
    url: https://arxiv.org/abs/2404.14219
    type: primary
  - title: Phi-4 Technical Report
    url: https://arxiv.org/abs/2412.08905
    type: primary
---

## 题怎么来的

微软研究 / SLM / 数据岗会把 Phi 问成：**质量这条轴你怎么操作、怎么证明没把考题背进去**。`msft-phi-slm` 收产品叙事（小参数、端侧、不是只堆层）；本题收数据配方。公开锚点是 Phi-1 / Phi-1.5 的「教科书」、Phi-3 把过滤网文扩到约 $3.3\mathrm{T}$ token、Phi-4 把合成贯穿预训练并加严去污。不是某场能点名的逐字面经。`realInterview: false`。

## 质量是轴，规模没有被取消

Phi-1 的公开故事很具体：约 $1.3\mathrm{B}$ 模型，高质量代码语料大约 $7\mathrm{B}$ token 量级：过滤后的 The Stack / StackOverflow（CodeTextbook）再加 GPT-3.5 合成的教材，然后用约 $180\mathrm{M}$ token 的 CodeExercises 做习题微调。HumanEval 上打过用脏得多语料训的更大代码模型。这不是「token 越少越好」，是 **脏网页的有效 $N$ 远小于计数**。

后面代际把规模加回来了，但轴没换。Phi-3-mini 仍讲两阶段：先用「有教育价值」的过滤网文打世界知识和语言，再用更狠的过滤子集加合成补推理。Phi-4 更把合成从「微调补丁」变成预训练主料之一。面试我会主动拆开，免得评委以为你还停在「只用 7B token」：

1. **过滤。** 分类器打教育价值 / 代码正确性，扔模板、重复、有害。过滤会引入风格偏差，要留未过滤对照。
2. **合成。** 大模型写章节、习题、带步骤的证明。能补长尾，也会复制教师幻觉和榜上题。
3. **课程。** 先基础后难题；Orca 那套「先学轨迹再学口吻」仍然适用，见 `msft-phi-slm`。

白板一句话：Chinchilla 管的是计算、参数、token **数量**；Phi 加的是 token **密度**。质量和规模该一起加，不是互相替代。算力够时，同一套高密度数据喂 70B 通常更好。Phi 的主张是单位参数的回报，不是「大数据只配小模型」。

## 污染：比「我们去重了」多三层

小模型在公开代码 / 学科榜上「打过 70B」，评委默认怀疑泄漏。Phi-1 自己也做了过激实验：按 embedding 和 AST 编辑距离，把 CodeExercises 里像 HumanEval 的题砍掉一大截（论文写过约 40% 量级），再训仍然领先。这是在回答指控，不是证明永远干净。我会把污染分成三层，评测协议跟 `align-eval-contam` 对齐，但数据源换成 Phi 的：

- **网文直接撞题。** n-gram / MinHash 对 HumanEval、MBPP、MMLU 题面。只做 exact hash 会漏空白和标点变体。
- **教师间接泄漏。** 合成教师（GPT-3.5 / GPT-4）见过考题，学生学的是「改写后的考题」。n-gram 对教师输出往往不够，要用 embedding 近邻、答案指纹，以及 **教师没见过的私有切片**。
- **改写绕过滤。** Phi-4 也承认：标准 n-gram 去污挡不住 paraphrase。所以公开榜只能当回归，不能当唯一验收。

常见误区是：把「过滤了教育价值」说成已经去污；把合成当免费数据（其实把教师的推理账单和泄漏风险搬到了数据阶段）。

## 评测怎么切，别只报一个 MMLU

我会按 **失败模式** 出表，不合成一个「Phi 分」。和长上下文切片同一纪律，见 `msft-long-context`。

| 切片 | 测什么 | 为什么 Phi 特别怕 |
| --- | --- | --- |
| 公开榜 | HumanEval / MMLU / GSM8K | 合成和网文最容易撞 |
| 去污后公开榜 | 同一套但去掉 n-gram 命中的题 | 看分数是掉一点还是塌 |
| 新鲜 / 私有 | 日期在训练截止之后的竞赛、内部题 | 教师也没见过才算能力 |
| 能力轴 | 代码执行、多步数学、世界知识、指令 | 教科书强在讲解，弱在长尾事实 |
| 对照轴 | 同计算脏数据 vs 过滤数据 | 没有这组，质量故事无法证伪 |

产品验收再加：端侧延迟、拒答、引用（有检索时）。流畅散文在纪要 / 仓库问答上不够用。Phi-3 把窗口拉到 128k，评测仍要按长度桶和证据位置切，不要用「能跑 needle」代替切片。

面试讲清楚：Phi 改的是帕累托前沿（同样参数下推理基准更像样），不是取消规模。世界知识、今年的内部 API、对抗鲁棒，还是更大模型或 检索增强生成（RAG）。数据岗要能画出过滤 / 合成 / 去污的预算，而不是背「教科书」三个字。

## 追问

- **合成数据算不算蒸馏？** 算手段之一。Phi-1 还有过滤后的人类代码语料；Phi-4 试图在部分 STEM 上超过教师，那要靠可校验的合成（执行代码、符号推导）和新鲜题，不是口头「我们超越了 GPT-4」。
- **为什么不把同样数据喂给大模型？** 应该喂。质量轴和参数轴正交。小模型故事是部署约束，不是数据只对 3.8B 有效。
- **内部评测会不会也脏？** 会。要时间切片、与训练检索隔离、人写新题。把 HuggingFace 上的「新榜」当私有，常常只是旧题换皮。
- **过滤会不会把方言 / 低资源语言洗掉？** 会。教育价值分类器偏正式英文和竞赛数学。产品若要多语言或企业黑话，过滤阈值和召回要单独切，不能只用 HumanEval 调数据。
