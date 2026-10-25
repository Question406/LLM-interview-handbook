---
id: openai-eval-harness
section: openai
order: 16
level: S
title: OpenAI：怎么设计内部 eval 避免污染和「刷榜」
quick: "我会把日常开发集、冻结协议的回归集和从未参与调参的私有 holdout 分开。训练重叠用 n-gram、canary 和人审排查，prompt、解码、grader 版本一起留档；这样才能判断涨分来自泛化还是反复挑测试结果。"
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

我会把能看错题的开发集、协议冻结的回归集、最终决策的私有 holdout 分开，并记录每次实验用过哪些信息。比如在同一份 MMLU 上换五套 system prompt，只报最高一次，虽然没有拷贝测试文件，开发决策已经利用了测试结果；n-gram 扫描抓不到这种过拟合。

评测首先检查训练见题。网页、GitHub 和教材可能收进 MMLU、HumanEval 题干，GPT-3 用 n-gram 做去污，GPT-4 报告也讨论泄漏。训练与 eval 重叠的条目要隔离或作废。私有集可以放 canary，若出现在外部模型或日志，就能发现泄漏；但释义、翻译和拆题仍可能躲过扫描，要用新题和人审抽样补盲区。

然后固定协议：题目、划分、prompt、解码参数、判分器全部打版本标签。别人 zero-shot、你从测试集抽 few-shot，或别人禁工具、你开检索，分数就不可比。simple-evals 公开 zero-shot CoT 和简单指令的实现，便于外部复跑；改 prompt 算新实验，不能继续画成同一条回归曲线。审计还要记录是否看过 case，否则三个月后可能无人能复现。

日常 dev eval 要小而快，可以看 case，但默认可能已被过拟合；frozen eval 控制同版本回归；private holdout 用人写或外采、未上网也未进训练的新题，发布和 checkpoint 决策才看它，且从不用于调超参或改 prompt。看完 holdout 错题再改训练混合，它也会变成另一份开发集。SimpleQA、GPQA 一类难搜难背的题有帮助，仍不能替代私有集。

判分要核对多选题选项顺序，生成题明确 grader prompt 并抽人审。模型作评委时与被测模型隔版本，减少偏爱自身文风。领域、长度、语言切片分别报，另估温度采样、判分抖动、题目子集带来的方差；0.5 分的提升可能只是噪声。

能力 holdout、DPO 偏好集和 RM 分数分别看。除非明确做 RL 并接受会被 hack，否则不要把 eval 接回训练反传。公开榜用于沟通，内部 frozen 检查回归，私有 holdout 支持决策；容易的内部集可以做回归，但用它对外包装能力也会误导。这张卡依据公开 simple-evals、SimpleQA 和报告设计 harness，不编造内部集合名字。

## 追问

**n-gram 扫干净就够了吗？**
不够，释义和翻译也能泄漏，所以需要私有新题与人审抽样。

**为什么 simple-evals 不用 few-shot？**
指令模型用简单指令更易复现，few-shot 增加协议选择，也更容易从测试分布挑示范。

**Agent eval 还要固定什么？**
固定工具桩或保留回放，工具结果和网页变化会让一周后的数字失去可比性。

**DPO 偏好集能进入能力 holdout 吗？**
不能，否则分数会混入对这批标注偏好的拟合。

相关：`openai-instructgpt-kl`（RL 刷 RM）、`openai-dpo-loss`
