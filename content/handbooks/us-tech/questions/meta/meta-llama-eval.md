---
id: meta-llama-eval
section: meta
order: 23
level: A
title: Meta：Llama 评测套件——别只报 MMLU，污染和套餐
quick: "Llama 评测要按知识、推理、数学、代码、指令、多语言、工具与长窗分开看，再配隔离的人评和安全指标。Herd 预训练用 8-gram 分榜估污染增益，后训练对 prompt 做 exact match；同时对齐 shot、CoT、解析方式与模板，避免把格式变化当能力。"
tags:
  - Meta
  - Llama
  - Evaluation
  - Contamination
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: Introducing Meta Llama 3
    url: https://ai.meta.com/blog/meta-llama-3/
    type: primary
  - title: Evaluation data contamination in LLMs (Singh et al., 2024)
    url: https://arxiv.org/abs/2404.06664
    type: secondary
---

Llama 的评测要用能力套餐，并把评测协议和污染检查一起报告。只说“MMLU $80$”还不够，至少要知道几 shot、是否 CoT、怎么选答案，以及测试题有没有被训练团队看见。

Herd 第 5 节与后训练章节把这些分开。MMLU 是 $57$ 科、5-shot 选择题，报宏平均且不用 CoT，主要观察知识与选择题行为；MMLU-Pro 更多选项、偏推理，用 5-shot CoT。论文还包括 GPQA、BBH、ARC，数学 GSM8k、MATH，代码 HumanEval、MBPP 及加严变体、MultiPL-E，指令 IFEval，多语言 MGSM 与内部翻译 MMLU，工具 Nexus、BFCL，以及长窗 ZeroSCROLLS、haystack、InfiniteBench。

人评按能力 taxonomy 收约 $7000$ 个偏难 prompt，建模人员不能接触题面。Llama 2 也已同时报告知识、代码和人评胜率。选择题还要换选项顺序、标签字母、prompt 模板，Herd 展示过这类敏感性，模板能带来波动时，$0.5$ 个点不应直接解释为能力变化。

实现需要固定 shot、CoT、logprob 选项打分或生成后 parse。Herd 将配置放在 GitHub / Hugging Face，最好使用同一 harness 再比较，相关公开榜选模原则见 `openai-eval-harness`。

## 污染怎样分榜检查

预训练阶段，Herd 参照 Singh et al. 2024 用 8-gram 重叠。若评测样本中比例 $\mathcal{T}_D$ 的 token 属于训练出现过的 8-gram，就作为污染判定；每个数据集选阈值，使干净子集与全集的估计分差最大。PiQA、HellaSwag 有较高污染率与估计增益，Natural Questions 则可能重叠率高、增益近零，因此要分别报污染率、估计增益、干净子集分数。通用方法见 `align-eval-contam`。

短题、公式、代码样板可能误命中，让干净子集更难、分数偏低，阈值不能全局统一。后训练则对每个 benchmark prompt 做 exact match，合成 SFT 特别容易混入题面，见 `meta-synth-sft`。Herd 退火实验加入 GSM8k / MATH 训练集后，8B 提升大、405B 几乎不涨，见 `meta-llama3-pretrain`，提醒要拆分数据暴露与泛化贡献。

组织隔离也写进论文：独立预训练数据团队采集清洗，职责包括挡外部 benchmark；人评只有不参与训练的少数人可接触，避免拿测试题调 mix。

结果可以并排展示公开榜、去污染结果、内部 / 人评。长窗同时看短任务回归与 haystack，不能用检索 haystack 替代推理；安全单列 Guard FPR 与拒答，见 `meta-llama-guard`，不和 MMLU 加成一个综合分。Base 与 instruct 两套都报，因为后训练会改变选择题行为。训练验证 PPL 下降不能替代下游评测，同一合成集也不能既训又测。

## 追问

**人评能替代公开榜吗？**
不能，它覆盖指令对话，却难以提供数学代码的回归密度，两套都要且人评对建模隔离。

**MMLU-Pro 可以替代 MMLU 吗？**
它是补充，偏重推理但仍是选择题，保留两者更方便判断变化。

**内部翻译 MMLU 能当多语言新榜吗？**
论文注明是内部 Google Translate 翻译、指令仍为英文，更适合诊断，不宜直接据此宣布对外多语言 SOTA。

**污染率高一定虚高吗？**
不一定，要看分榜估计增益和干净子集，Natural Questions 就说明重叠与收益不必一致。
