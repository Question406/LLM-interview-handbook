---
id: dt-frontier-science
section: frontier-release
order: 2
level: S
title: GPQA、HLE、FrontierMath、AIME 怎么造，卡的是哪项能力？
quick: "GPQA Diamond 用 198 道经博士出题、复核的四选题考科学推理；HLE 用 2500 道专家题覆盖更多学科，收集时先筛掉当时模型能答对的题；FrontierMath 考研究级数学；AIME 是每年的数学竞赛新题。报分必须注明子集、年份与工具，允许搜索和无工具是不同实验。"
companies:
  - openai
  - anthropic
  - google
  - meta
tags:
  - Evaluation
  - GPQA
  - Math
  - Reasoning
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "GPQA: A Graduate-Level Google-Proof Q&A Benchmark"
    url: https://arxiv.org/abs/2311.12022
    type: primary
  - title: Humanity's Last Exam
    url: https://arxiv.org/abs/2501.14249
    type: primary
  - title: FrontierMath
    url: https://arxiv.org/abs/2411.04872
    type: primary
  - title: Gemini 3.1 Pro Model Card
    url: https://deepmind.google/models/model-cards/gemini-3-1-pro/
    type: primary
  - title: Introducing GPT-5
    url: https://openai.com/index/introducing-gpt-5/
    type: primary
  - title: Claude Opus 4.5 System Card
    url: https://www.anthropic.com/claude-opus-4-5-system-card
    type: primary
  - title: Llama 4 model card
    url: https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md
    type: primary
---

这几套题都强调推理，设计上都难以靠在题面之外找到现成答案来解决，但学科、答案形式和筛题方式不同：GPQA Diamond 考研究生水平的生物、物理、化学；HLE 学科更广，而且专门保留了当时模型答不出的题；FrontierMath 是研究级数学；AIME 是每年的竞赛新题。所以听到「GPQA 提高了两个点」，先确认是否允许工具、是否用的 Diamond 子集。「GPQA + 搜索」和「GPQA 无工具」必须分开报告。

要训练对应的能力，可以考虑有可验证答案的理科题和规则奖励，见 `dt-rlvr-data`。单纯增加网页百科数据，或让模型记住 MMLU，并没有直接覆盖这些题需要的推理。

## GPQA Diamond

GPQA 考查研究生水平的科学知识和推理，设计时就要求仅靠 Google 搜索也难以解答。Rein 等做了 448 道主集，覆盖生物、物理、化学，四选一。出题人是在读或已完成相应领域 PhD 的承包者（Upwork，61 人）。流水线是：专家写题，同领域专家先答并改题，作者修订，第二位同领域专家再答，另有三位其他领域的博士在可以不受限使用网页（不许用 LLM）的条件下作答。非专家平均花 30 分钟以上。论文报告专家正确率约 65%（扣掉专家事后自己指出的明显失误后约 74%），非专家 34%，当时的 GPT-4 在给出少量示例并要求分步推理（few-shot CoT）的设定下是 39%。四选一随机猜的正确率是 25%。

Diamond 是最高质量的子集，198 题。筛选规则写在论文表 2：两位专家都答对（或第二位答错但能清楚指出自己的失误），并且非专家答对的不超过 1/3。三个规模是扩展集 546、主集 448、Diamond 198。作者要求不要把例题明文贴到网上，数据集里带 canary 字符串，方便训练集过滤。

## HLE

HLE 评估模型解答学术题的能力与人类专家之间的差距。它由 Center for AI Safety 和 Scale 制作，有 2500 道公开题，另留私有集用来检查过拟合。学科超过一百个，数学占比高，也有人文和自然科学。约 14% 的题带图。24% 是多选题（五个或更多选项），其余是短答案 exact match。题目来自近千名专家、500 多家机构的投稿。奖金池 50 万美元：前 50 题每题 5000 美元，其后 500 题每题 500 美元，录用的题可以署名。

造法的关键一步在人工评审之前：每道题先拿当时的前沿模型试，模型能答对就退回。他们记录了超过 7 万次尝试，约 1.3 万道把模型难住的题才进入专家评审。评审有两轮，评审人要有研究生学历。题目必须原创，或者是对已发表信息的非平凡综合，不能靠检索秒答；答案要短，可以自动判分。公开集用 LLM judge 对齐等价写法（比如小数和分数）。

论文强调，收集过程本身就在剔除当时模型会做的题，所以发布时分数低，有一部分是设计出来的，接近 0 的小波动不要当成代际进步。HLE 比 GPQA 学科更广，也更依赖「当时模型答错」这个筛选条件。这个条件会随模型进步失去区分力：下一代模型得分提高时，要记得这些题原本是按上一代模型的弱点挑出来的。

## FrontierMath

FrontierMath 考查研究级数学，任务难度和解题方式与 AIME 竞赛题不同。它由 Epoch AI 组织六十多位数学家写的未发表新题构成，覆盖 MSC2020 的大部分分支。典型题目需要该方向的研究者花数小时，最难的要数天。答案做成可自动验证的形式，既减少人工判分，也减少竞赛题进入预训练的问题。论文发布时，当时最强的模型多次采样仍低于 2%。

数值答案的形式和数学研究的日常写法不一样，Fields 奖得主的访谈里也提到了这一点。发版如果报 FrontierMath，要问是哪一层、有没有工具、是单次还是多次。Gemini 3.1 Pro 模型卡（2026-02）我读到的主表没有这一行。

## AIME 和 ARC-AGI-2

AIME 是美国数学邀请赛，测的是竞赛数学。每年都有新题，答案是 0 到 999 的整数，所以判分便宜，题面日期也可以卡在训练截止之后。但题量很小（一场 15 题），方差大，发版应写明年份和有没有工具。GPT-5 发布博文写 AIME 2025 无工具 94.6%，并注明带工具的结果不能和无工具直接比。

ARC-AGI-2 是抽象视觉谜题，题目不来自教科书，测的是对没见过的变换的推理，不是科学知识。Gemini 3.1 模型卡写的是 ARC Prize Verified、半私有集。私有集的意义和 HLE 的 holdout 一样：公开题一旦被抓取进训练数据，分数就会漂。

## 谁在哪次发布里报了

设定不同，下面几格不能排成一条名次。

| 材料 | 模型 | 数据集 | 设定 | 他们写的数 |
| --- | --- | --- | --- | --- |
| Google 模型卡，2026-02 | Gemini 3.1 Pro Thinking High | GPQA Diamond | 无工具 | 94.3% |
| 同一张卡的对照列 | Gemini 3 Pro / Sonnet 4.6 / Opus 4.6 / GPT-5.2，均为对方思考档 | GPQA Diamond | 无工具 | 91.9% / 89.9% / 91.3% / 92.4% |
| 同一张卡 | Gemini 3.1 Pro | HLE 全文，文本+多模态 | 无工具 | 44.4% |
| 同一张卡 | Gemini 3.1 Pro | HLE | 搜索（带屏蔽名单）+ 代码 | 51.4% |
| 同一张卡 | Opus 4.6 Thinking Max | HLE | 搜索+代码 | 53.1% |
| 同一张卡 | Gemini 3.1 Pro | ARC-AGI-2 | ARC Prize Verified | 77.1% |
| Anthropic system card | Claude Opus 4.5 | GPQA Diamond | 64k thinking，200k 上下文，high，5 次平均 | 86.95% |
| OpenAI GPT-5 博文 | GPT-5 pro | GPQA | 无工具 | 88.4% |
| OpenAI GPT-5 博文 | GPT-5 | AIME 2025 | 无工具 | 94.6% |
| Meta 模型卡，2025-04，指令模型 | Llama 4 Maverick | GPQA Diamond | 0-shot accuracy | 69.8% |
| 同一张卡 | Llama 4 Scout | GPQA Diamond | 0-shot | 57.2% |

Anthropic 的 86.95% 带 64k thinking；Google 表上的 GPQA 列注明无工具。这是两套协议，不要写成「3.1 Pro 比 Opus 4.5 高 7 个点」。Llama 4 是 2025-04 的指令模型，和 2026 年的思考模型不是同一代产品。

## 追问

- **GPQA 涨了，是科学能力涨了还是格式？** 先看无工具和有搜索两种设定的差距。差距很大，说明模型在用检索补知识，闭卷覆盖并没有变。
- **HLE 能当训练集吗？** 公开的 2500 题一旦进入教师的检索库，这张榜就废了，私有集才能当门禁。这和 SWE-bench 是同一条纪律，见 `dt-contam-hold`。
- **AIME 满分了还要不要报？** 要报，并写明年份和工具。达到满分后，这套题就无法继续区分前沿模型，需要补充 FrontierMath 或新一年的竞赛题，并写清评测子集。
