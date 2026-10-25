---
id: google-eval-mmlu
section: google
order: 21
level: A
title: Google：MMLU 等学术榜的坑，污染、prompt、多语言
quick: "MMLU 适合做能力回归，报分前要查污染并固定 prompt、选项、解码和答案抽取协议。用去重后的分数与私有变体交叉验证，多语言还要单独检查翻译和知识背景；产品效果则回到实际任务切片。"
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

MMLU 可以做粗能力曲线和实现回归，但涨分后要先排除污染与协议变化，再判断能力是否提高。比如英文 5-shot CoT 的成绩，无法直接和 0-shot 选字母比较，更不能从“涨了 1.2 分”直接推出产品更好。PaLM / Gemini 报告都重视它，研究问题却是这个分数是否可信。

MMLU 的 57 个科目来自真题、教材和网页。预训练里的 Common Crawl、书籍、GitHub，以及 SFT 里的博客和题解，都可能带入题目、答案或解析。PaLM 用 n-gram 做过去污染，但只去题面不够。我会先规范化空白、大小写、标点做 exact 哈希，再用 n-gram / MinHash 找局部重叠，像 GPT-3 / PaLM 的 13-gram 一类阈值要按题长调整。

接着把题面当 query 搜训练索引或外网，捕捉改写后的博客；给正确选项、标准解析和 CoT 模板建答案指纹。还可用题目前缀做生成探针，看模型是否续出原选项或解析，命中增加嫌疑，未命中却不能证明干净。语义近邻只用于候选隔离和人工复核，同主题不同数字的题不应自动删除，否则会误伤正常能力。

至少并排报公开榜、去掉重叠后的分数、私有变体。变体可以改数字、换选项顺序和包装语言，公开榜远高于变体时先查泄漏。确认泄漏后隔离来源，重报去污染分数，更新私有测试；让模型在 prompt 中承诺不背题解决不了问题。

协议也要锁定：0-shot / 5-shot、dev 示范科目和格式、A/B/C/D 的 logprob 打分还是自由生成后正则抽 “The answer is C”、选项轮换、是否 CoT、解码设置与答案脚本，都存在 git 里。Gemini Ultra 公开数字用了 CoT，应明确标注。MMLU 官方采用科目宏平均，微平均会放大题量多的科目。MMLU-Pro 增到十个选项、难度更高，能缓解考试格式的影响，仍是需要去污染的公开集。

多语言翻译也不能直接视作能力平移。术语译错会改变题意，SentencePiece 下长度不同又影响上下文和 packing，美国司法、历史翻译后仍是美国知识；英文解析多、低资源语言较干净，也会造成污染不对称。报告应说明是原语料、专业翻译还是模型翻译，MMMLU 一类人工翻译通常比直接模型翻译更可信，协议仍须固定。

发论文或定级时，把私有集与 GPQA、MMLU-Pro 等难榜并排；产品则按搜索、代码、长文档分别验收。MMLU 涨而产品切片不动，应依据产品切片判断实际价值，避免把公开榜当训练 loss 的代理持续刷分。

相关：`google-cot-reason`、`google-gemini-longctx`
