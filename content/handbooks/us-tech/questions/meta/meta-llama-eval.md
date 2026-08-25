---
id: meta-llama-eval
section: meta
order: 23
level: A
title: Meta：Llama 评测套件——别只报 MMLU，污染和套餐
quick: >-
  MMLU 只是知识选择题的一个点。Herd 把能力拆成知识、推理、代码、指令、多语言、长窗、工具，再加人评。污染用 8-gram
  重叠估增益；后训练对 prompt 做 exact match。数据团队和组织隔离写进论文，不是口头「我们去重了」。
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

Llama 岗听「我们 MMLU $80$」会追问：几 shot、要不要 CoT、污染怎么测、人评谁有权看。Herd 第 5 节和后训练章节把套餐摊开了。通用污染手法见 `align-eval-contam`；本题收 Meta 公开怎么做。

## 不要只报 MMLU

MMLU 是 $57$ 科 5-shot 选择题，Herd 报宏平均、**不用 CoT**。它测的是知识检索 + 选项格式，不是推理链。同一篇论文自己就加了：

- **更难知识 / 推理：** MMLU-Pro（更多选项、偏推理，5-shot CoT）、GPQA、BBH、ARC；
- **数学：** GSM8k、MATH，明确区分有没有把训练集塞进退火（`meta-llama3-pretrain`）；
- **代码：** HumanEval、MBPP 及加严变体、MultiPL-E；
- **指令：** IFEval；
- **多语言：** MGSM、内部翻译版 MMLU（指令留英语）；
- **工具 / 长窗：** Nexus、BFCL；ZeroSCROLLS、haystack、InfiniteBench；
- **人评：** 按能力 taxonomy 收约 $7000$ prompt，难度偏硬，**建模同学不能碰题面**。

Llama 2 时代就同时报 MMLU、代码、人评 win rate。只刷 MMLU 过不了「有没有读论文」这关。选择题还要做格式鲁棒：换选项顺序、换标签字母、换 prompt 模板。Herd 专门画了 MMLU 对这些扰动的敏感性。数字随模板抖，就不要把 $0.5$ 个点的涨当能力。

实现要对齐：shot 数、是否 CoT、是 logprob 选选项还是生成后再 parse。Herd 说评测配置放在 GitHub / Hugging Face。现场说「跟他们仓库同一套 harness」，比自己口头 5-shot 更像做过。OpenAI 侧「公开榜不当唯一选模信号」见 `openai-eval-harness`。

## 污染：8-gram 和 exact match

预训练：Herd 跟 Singh et al. 2024，用 **8-gram 重叠**。一条评测样本，若其中比例 $\mathcal{T}_D$ 的 token 属于训练集里出现过的 8-gram，就算污染。$\mathcal{T}_D$ 按数据集选，让「干净子集 vs 全集」的分数差（估计增益）最大。结果因榜而异：有的榜污染率高且增益高（论文举 PiQA、HellaSwag）；有的污染率看起来高但增益几乎为零（Natural Questions）。所以**不要报一个全局污染百分比**，要分榜：污染率、估计增益、干净子集分数。

后训练：对每个 benchmark 的 **prompt 做 exact match** 去污染。合成 SFT 特别容易把题面洗进来，见 `meta-synth-sft`。退火实验把 GSM8k / MATH 训练集加进去，8B 大涨、405B 几乎不涨——这是「背题」和「真会」的对照，面试要主动讲。

组织措施论文写得很硬：预训练数据由**单独团队**采和洗，激励就是挡住外部 benchmark；人评只有不参与训练的一小撮人能碰。这不是 HR 废话，是防建模同学用测试集调 mix。

## 套餐怎么呈

我会三列：公开榜、去污染后、内部 / 人评。长窗单独一列：短任务有没有回归 + haystack，不要用 haystack 代替推理。安全单独一列：Guard 的 FPR / 拒答，见 `meta-llama-guard`，不要和 MMLU 加总成一个「综合分」。

错法：用训练中的验证 PPL 代替下游。PPL 跌、MMLU 不动，可能是格式或污染。错法二：在同一套合成数据上既训又测。错法三：只报 instruct 模型的 MMLU，不报 base——后训练会改选择题行为，两套都要。

## 追问

- **8-gram 会不会误杀？** 会。短题、公式、代码样板假阳性高。所以他们用「估计增益」校准阈值，而不是全局一个 cutoff。误杀会让干净子集变难，分数偏低。
- **人评能代替榜吗？** 不能。人评覆盖指令和对话，覆盖不了数学代码的回归密度。两套都要，且人评题要对建模隔离。
- **MMLU-Pro 替代 MMLU 吗？** 补集。Pro 更偏推理、选项更多，格式仍是题。套餐里两者都留。
- **内部翻译 MMLU 算不算新榜？** 论文标明是内部、Google Translate、指令留英。拿去对外打「多语言 SOTA」要非常小心，现场当成诊断工具。
