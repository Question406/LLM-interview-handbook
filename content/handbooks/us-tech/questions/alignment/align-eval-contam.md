---
id: align-eval-contam
section: alignment
order: 7
level: A
title: 对齐：评测污染，n-gram / 搜索查重，泄漏后怎么办
quick: "评测污染要同时检查题面、答案和解析是否进入预训练、SFT、偏好或合成数据。用规范化 exact、n-gram、搜索和答案指纹交叉定位，命中后隔离来源并复核；确认泄漏要标记旧分数、重报去污染结果，再用私有变体重新评估。"
tags:
  - OpenAI
  - Meta
  - Evaluation
  - Contamination
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Language Models are Few-Shot Learners (GPT-3)
    url: https://arxiv.org/abs/2005.14165
    type: primary
  - title: Time Travel in LLMs — Tracing Data Contamination
    url: https://arxiv.org/abs/2308.08493
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

评测污染要查的不只是题面，也包括答案、解析和合成轨迹有没有进入训练。比如训练只收了一篇 GSM8K 题解博客，题面 hash 没命中，模型仍可能见过解答，这时公开分数就不能直接当作泛化能力。

GPT-3 已经用 n-gram 做去污染，后来对齐数据又增加了 SFT、RLHF、红队与自我蒸馏等入口。训练网页镜像、教材 PDF、GitHub 题解和评测博客都要纳入索引，安全与能力评测也都要检查。

我会先规范化空白、大小写、标点后做 exact，代码也做规范化；再用 n-gram / MinHash 找局部重叠，GPT-3 的 13-gram 是一个公开例子，实际阈值要随题长调整。题面被改写或拆进对话时，用题面搜索训练索引或外网，再索引数学最终答案、选择题选项、标准输出和 CoT 模板，覆盖只存答案的情况。

生成式探针可以让模型续写题目前缀，若续出原题或答案会增加嫌疑，续不出则不能证明干净。语义近邻只作为候选：同主题、数字不同的题可能被误杀，自动全删会压低能力评估。命中进隔离桶人工核实，并记录来源和抓取批次。

## 报告与处理

报告至少并排展示公开榜、去除重叠题后的结果，以及私有变体或时间切分结果，后者可用评测发布日之后的题。公开分远高于私有变体就触发调查，同时报 n-gram 命中率、只答案重叠占比和来源站。选择题、代码、对话要分别说明指纹与误杀复核，不能只报一个 13 的阈值。

私有集里放 canary，训练后探测可抓整包复制，但抓不到改写。动态换数字、选项顺序或包装语言，能降低背题收益，仍不能替代静态检测：旧重叠可能一直留在训练里。XSTest、HarmBench 或公开 jailbreak 被写进拒答 SFT，再在同一集报 ASR 为 0，也是污染，见 `align-red-team`。合成自我蒸馏还可能把评测格式洗入训练，属于自污染，门禁不同但可共用查重工具。

确认泄漏后，先停止使用命中的训练源并保留审计；在干净训练快照重跑，或至少重报剔除重叠题的分数，旧榜标为 contaminated，不继续当 SOTA 宣传。随后更换高风险评测的私有变体，尤其是容易背拒答示范的安全题，并检查同一来源是否同时进入 SFT、RM 和 RL，避免只清预训练。线上模型已训练完，则用私有集重新定级，必要时收窄能力声明，提示一句“不要背题”修复不了已学到的内容。

## 追问

**n-gram 或搜索单独够吗？**
不够。前者查局部重叠，后者查改写与题解页，还要补答案指纹。

**语义近邻能全删吗？**
不能，答案不同的近邻需人工判断，误杀与漏杀会分别压低或抬高分数。

**重新训练让模型忘掉行吗？**
不可靠。先隔离来源、重报和换评测，不能把遗忘当默认修复。

**和红队过拟合有什么关系？**
都会让评测失效。污染是训练见过题，对评测分布反复优化则可能没有直接拷题；都需要隔离与 held-out。
