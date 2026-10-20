---
id: openai-eval-harness
section: openai
order: 16
level: S
title: OpenAI：怎么设计内部 eval 避免污染和「刷榜」
quick: "训练数据、开发决策、对外数字要三套分离。公开榜只能沟通，不能当唯一选模型信号。固定 prompt 和数据划分，扫 n-gram / canary，留从未调过的 holdout。simple-evals 的立场是 zero-shot 思维链（CoT，即分步推理过程）、实现公开、不靠刷 few-shot。"
tags:
  - OpenAI
  - Evals
  - Contamination
  - Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: openai/simple-evals
    url: https://github.com/openai/simple-evals
    type: primary
  - title: Introducing SimpleQA
    url: https://openai.com/index/introducing-simpleqa
    type: primary
  - title: GPT-4 Technical Report
    url: https://arxiv.org/abs/2303.08774
    type: primary
  - title: Language Models are Few-Shot Learners
    url: https://arxiv.org/abs/2005.14165
    type: primary
---

## 题怎么来的

OpenAI 把评测当产品：simple-evals 公开了他们发数字时用的 输入提示（prompt） 设定；GPT-3 / GPT-4 报告写了污染检查；SimpleQA 是后来补的短事实集。对齐岗和研究岗都会问「你怎么知道分数提升是真的」。我按内部 harness 设计答，不编造未公开的内部集名字。强化学习（RL） 刷 奖励模型（RM） 见 `openai-instructgpt-kl`，那是另一类 hacking。

## 污染从哪来

三件事常被混成一个词：

1. **训练见过题面。** 网页、GitHub、教材把 MMLU / HumanEval 题干收进去。GPT-3 用 n-gram 重叠做 decontamination；GPT-4 报告继续讨论泄漏。内部 harness 要对训练集和 eval 做重叠扫描，命中就隔离或作废该条。
2. **开发见过标签。** 团队对着同一张公开测试表调 prompt、选 checkpoint、改解码。数字涨了是「刷榜」，不是泛化。这和数据泄漏一样致命，但 n-gram 扫不出来。
3. **评测协议漂。** 别人 zero-shot，你 few-shot 还从测试集抽示范；别人禁工具，你开了检索。simple-evals 写明他们用 zero-shot 思维链（CoT，即分步推理过程）、简单指令，就是为了让数字可比。

Canary 字符串可以埋进私有集：一旦出现在外部模型或日志里，就知道这包数据漏了。Holdout 必须从未用来选超参或改 prompt，否则它会慢慢变成第二张测试表。

刷榜在实验室里的样子通常很普通：同一张 MMLU 上换五套 system prompt，留最高的那次；或者看了 holdout 的错题再去改训练混合。过程没有泄漏文件，但决策已经用了测试信息。Harness 要记录「这组数字用了哪次 prompt、是否允许看过 case」。没有审计日志，过三个月没人能复现。

## 内部 harness 我会怎么拆

- **Dev eval：** 小、快、允许看 case。用来日常回归。默认怀疑它已经被过拟合。
- **Frozen eval：** 题目、划分、prompt、解码参数、判分器版本全部打标签。涨点必须在同一版本上比。改 prompt 算新实验，不是同一条曲线。
- **Private holdout：** 人写或外采、不上网、不进训练。发布和升 checkpoint 看它。SimpleQA / GPQA 一类难搜、难背的题，用来降低「背榜」；仍不能替代私有集。
- **判分。** 多项选择要对齐选项顺序；生成式用明确的 grader prompt，并抽人审。模型当法官时，法官模型和被测模型要隔版本，避免偏好被测模型自身文风。
- **切片。** 总平均之外看领域、长度、语言。刷榜最爱藏在平均里。

不要把 eval 当训练损失的一部分去反传，除非你在做明确的 RL，并且接受它会被 hack。Harness 的职责是检测 hacking，不是再提供一个可优化接口。和 `openai-dpo-loss` 的偏好集、RM 分数是另一条曲线，不要和能力 holdout 画在一张「总平均」里充数。

方差也要进 harness：温度采样、判分器抖动、题目子集。只报一个点估计，0.5 分的「新高」可能是噪声。

simple-evals 把实现公开，就是让外部能按同一协议复跑，减少「我们内部另一种 prompt 更高」的无依据说法。

公开榜只沟通；内部 frozen 管回归；private holdout 管决策。三者共用一张表，就容易让测试信息进入开发决策。内部集可以比公开榜容易，但那只是回归信号；用容易的内部集对外讲故事，也是刷榜。

## 追问

- **n-gram 扫干净就安全吗？** 不够。释义、翻译、拆题仍能漏。私有新题和人审抽样补盲区。
- **为什么 simple-evals 不用 few-shot？** 指令模型不该靠从测试分布里偷示范；few-shot 还把协议空间撑大，更好刷。
- **Agent eval 多了什么？** 工具输出和网页会变。要固定工具桩或存回放，否则过一周数字不可复现。
- **和 直接偏好优化（DPO） 偏好集重叠？** 对齐数据不能混进能力 holdout。否则你在测「会不会讨好这批标注员」。
