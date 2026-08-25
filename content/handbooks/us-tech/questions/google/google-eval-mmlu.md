---
id: google-eval-mmlu
section: google
order: 21
level: A
title: Google：MMLU 等学术榜的坑，污染、prompt、多语言
quick: >-
  MMLU 涨了先问是能力还是背题。污染用 n-gram / 搜索 / 答案指纹分层查，不要只 hash。分数对 prompt、选项顺序、是否
  CoT 极敏感。多语言翻译题不是原题的能力平移。公开榜当回归，产品结论用私有变体。
tags:
  - Google
  - MMLU
  - Evaluation
  - Contamination
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Measuring Massive Multitask Language Understanding
    url: https://arxiv.org/abs/2009.03300
    type: primary
  - title: PaLM — Scaling Language Modeling with Pathways
    url: https://arxiv.org/abs/2204.02311
    type: primary
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: primary
  - title: Time Travel in LLMs — Tracing Data Contamination
    url: https://arxiv.org/abs/2308.08493
    type: secondary
---

PaLM / Gemini 技术报告都把 MMLU 当头条能力数。Google 研究岗问这题，不是让你背 57 个科目，而是问：这个数能不能当训练目标、会不会被污染和 prompt 把戏抬起来。CoT 怎么用见 `google-cot-reason`。别把「我们 MMLU +1.2」说成产品赢了。

## 污染：公开题早就在网上

MMLU 来自真题、教材、网页。预训练抓 Common Crawl、书籍、GitHub，SFT 抓博客和题解，都可能把题面或答案吃进去。PaLM 论文用 n-gram 做过去污染；后来发现只去题面不够，答案和解析页一样能泄漏。

我会分层查，不要只做全文哈希：

1. 规范化 exact：去空白、大小写、标点再哈希。
2. n-gram / MinHash：GPT-3 / PaLM 用 13-gram 一类重叠当候选。题短时阈值要按长度调。
3. 搜索：把题面当 query 搜训练索引或外网。能抓住「训练没存原题、但存了几乎同样的博客」。
4. 答案指纹：选择题正确选项、标准解析、思维链模板都要建索引。只吃到解答也算污染。
5. 生成式探针：给题目前缀，看会不会续出原选项或原解析。成功加嫌疑；失败不能证明干净。

语义近邻不能当自动删除：同主题不同数字的题会误杀，能力被压低。命中进隔离桶人工复核。对照至少三列：公开榜、去掉重叠后的分数、私有变体（改数字、改选项顺序、换包装语言）。公开榜远高于私有变体，优先怀疑泄漏。发现了还继续报旧榜，是评测诚信问题。

## prompt：同一个模型能差好几个点

MMLU 是四选一。分数对下面这些东西敏感，敏感程度经常大于一次架构小改：

- 0-shot vs 5-shot。5-shot 从 dev 抽示范，示范科目和格式都在泄露「这是考试」。
- 答案提取：对 A/B/C/D 算 logprob，还是让模型自由生成再正则抽「The answer is C」。两者不可比。
- 选项顺序。正确项总在 A，或总在模型爱选的位置，分数虚高。要轮换。
- 是否 CoT。Gemini Ultra 公开数字用了 CoT；和 0-shot 直接选字母不是同一项测试。报数时必须写清协议。
- 宏平均 vs 微平均。MMLU 官方是科目宏平均。题量大的科目被微平均放大。

面试我会说：内部对比锁死 prompt、解码、抽取脚本，存在 git 里。换了 decoding 或「加一句 let's think」就不是同一张表。MMLU-Pro 把选项加到十个、题更硬，能减轻一点「会考试格式」。它仍然是公开集，污染逻辑不变。

## 多语言：翻译题不是能力平移

把 MMLU 译成中文 / 印地语再测，看起来像多语言能力。坑：

- 翻译质量。术语译错，模型答错不一定是语言差。
- Tokenization。同一题在 SentencePiece 下长度差一截，长上下文和 batch packing 都不一样。
- 文化题。美国司法、美国历史译过去仍是美国知识，不是目标语能力。
- 污染不对称。英文题解满网都是，低资源语言可能更干净，分数差不能直接当「英文更强」。

PaLM / Gemini 报多语言时，要问是原语料、专业翻译、还是模型自己译的。MMMLU 一类人工翻译集比「我们用模型翻了一遍」可信，但协议仍要钉死。

错法：把 MMLU 当训练损失的代理去刷；只报一个总分、不报污染率和 prompt；用英文 5-shot CoT 的数和别人 0-shot 比。

## 追问

- **n-gram 和搜索哪个够？** 单独都不够。n-gram 抓局部重叠；搜索抓改写和题解页；答案指纹是第三层。
- **泄漏后怎么办？** 隔离该源、重报去污染分数、换私有变体。不要靠 prompt 说「请不要背题」。
- **MMLU 还能用吗？** 能，当实现回归和粗能力曲线。发论文 / 定级用私有集和更新的难榜（GPQA、MMLU-Pro）并排。
- **和内部产品评测怎么排？** 学术榜不替代任务评测。搜索、代码、长文档各有切片，见 `google-gemini-longctx`。MMLU 涨了而产品切片不动，信产品。
