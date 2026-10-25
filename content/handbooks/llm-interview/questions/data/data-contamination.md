---
id: data-contamination
section: data
order: 8
level: A
title: 怎么做 Benchmark Contamination 检测？
quick: "按泄漏形态分层查：原文和规范化后的精确重叠、n-gram/MinHash 近重复、语义相似，再给答案和解析单独建指纹，因为训练里常常只有解法。最后用时间戳、来源追踪和私有变体兜底，报公开榜、去重叠后、私有变体三列分数。"
tags:
  - Data
  - Eval
  - Contamination
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Time Travel in LLMs — Tracing Data Contamination
    url: https://arxiv.org/abs/2308.08493
    type: primary
---

我会按泄漏形态分层查，再用来源追踪和时间切分兜底，exact string 只是第一层。训练语料里更常见的是改写过的题面、只出现答案或解析的页面，或者把评测博客当普通网页一起抓进来，这些 exact hash 全会漏掉。

比如一道数学题，训练集里没有题面，却有一篇把它一步步解完的博客。模型在榜上答对了，题面匹配查不出任何重叠，可它其实见过解法。这和合成自污染（`data-synthetic-self-contamination`）是两件事：这题是评测被训练看见，那题是模型自己的错误被当成下一轮的真数据。

## 四层重叠，外加答案泄漏

第一层是 exact hash，把空白规范化后算全文哈希，抓镜像拷贝。第二层是 normalized exact，去掉标点、大小写、代码空白后再比；数学和代码还要规范化变量名和数字格式。第三层用 n-gram / MinHash / LSH，抓局部改写、拼接、挖空填空，阈值按题长校准，见 `data-minhash`。第四层是 semantic retrieve，用 embedding 找近邻，再由交叉编码器或人工复核是不是同一道题。

只比 question 不够。训练里可能只有 solution blog、GitHub issue、教材答案，所以答案模板、解析段落、标准输出要单独建索引。落地时我会按评测集建三张表：题面指纹、答案指纹、解析指纹，训练流水线每次入库都扫一遍，命中就进隔离桶，别默默丢掉。隔离桶要能复盘是哪个源、哪次抓取带进来的。train/test 去重（`pdd-sft-template-dedup`）用的是同一套指纹，只是对象从监督微调（SFT）的数据划分换成了评测集。

## 怎么报才算做过检测

至少对照三列：公开榜分数、去重叠后分数、私有扰动或时间切分变体的分数。公开榜远高于私有变体，先怀疑泄漏，再谈能力。还要报 n-gram 重叠率、近邻命中率，以及「只有答案重叠」的占比，光说一句「做过 decontamination」不算数，报一个相似度阈值交差也不算。

生成式 probe，就是给题目前缀、看模型能不能续出原答案，只能当辅助：续不出来证明不了干净，续出来了才提高嫌疑。最终的门禁靠时间切分、源站黑名单和私有 held-out，单靠某一个相似度阈值撑不住。高风险的榜还要另备 canary 和私有变体，免得公开题面被「洗干净」后分数还是虚高。

动态榜或者定期换皮的题能降低背公开题的收益，但替代不了静态检测：换皮之后旧的重叠还留在训练集里，只是你看不见了。面试里如果对方只说「用过 embedding」，我会追问有没有报「只答案重叠」和公私榜差，这两列没有，就不算做过 contamination 检测。

## 追问

**语义近邻都删掉会误杀吗？**
会。题意相近但数字、约束、答案不同的要人工复核。误杀会让能力评估偏低，漏杀会让榜虚高。

**代码和数学为什么更难查？**
变量重命名、格式化、等价变换都能躲过字符串匹配，要先规范化 AST 或答案模板再比。

**和 self-contamination 怎么一句话区分？**
泄漏是评测被看见；自污染是训练分布被模型自己的输出喂胖。两种都要查，门禁不一样。

**发现重叠之后怎么处理？**
先隔离那个源、重报去污染后的分数，再决定要不要从训练里删。藏起重叠率继续报公开榜，在面试里是减分项。
