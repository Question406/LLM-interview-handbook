---
id: data-contamination
section: data
order: 8
level: A
title: 怎么做 Benchmark Contamination 检测？
quick: >-
  不能只查 exact string。要从 exact/normalized overlap、n-gram/MinHash
  near-duplicate、semantic similarity、答案/解析泄漏、时间戳与 source provenance 多层检查。
tags:
  - Data
  - Eval
  - Contamination
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: Time Travel in LLMs — Tracing Data Contamination
    url: https://arxiv.org/abs/2308.08493
    type: primary
---

不能只扫 exact string。训练语料里更常见的是改写题面、只吃到答案/解析、或把评测博客当普通网页吞进去——这些 exact hash 全漏。检测要按泄漏形态分层，并用 provenance 与时间切分卡住「看起来没重叠、其实见过解法」。这和合成自污染（`data-synthetic-self-contamination`）不同：本题是评测被训练看见，那题是模型自己的错误被当成下一轮真数据。面试陷阱是报一个相似度阈值交差；没有公私榜对照和答案指纹，检测等于没做。

## 四层重叠，外加答案泄漏

1. **Exact hash**：规范化空白后的全文哈希，抓镜像拷贝。
2. **Normalized exact**：去标点、大小写、代码空白后再比；数学/代码还要规范化变量名与数字格式。
3. **n-gram / MinHash / LSH**：局部改写、拼接、挖空填空；阈值按题长校准，见 `data-minhash`。
4. **Semantic retrieve**：embedding 近邻 + 交叉编码器/人工复核是否同一题。

只比 question 不够：训练里可能只有 solution blog、GitHub issue、教材答案。要对答案模板、解析段落、标准输出单独建索引。高风险榜应另备 canary 与私有变体，避免公开题面被「洗干净」后分数仍虚高。

## 实验怎么报，才算做过检测

对照至少三列：公开榜分数、去重叠后分数、私有扰动或时间切分变体分数。若公开榜远高于私有变体，优先怀疑泄漏而不是能力。报告 n-gram 重叠率、近邻命中率、以及「只答案重叠」占比，不要只说「做过 decontamination」。

生成式 probe（给题目前缀看能否续出原答案）只能当辅助：失败不能证明干净，成功才提高嫌疑。最终门禁是时间切分 + 源站黑名单 + 私有 held-out，而不是某一个相似度阈值。train/test 去重（`pdd-sft-template-dedup`）是同一套指纹，只是对象从 SFT split 换成评测集。

落地时按评测集建「题面指纹 / 答案指纹 / 解析指纹」三张表，训练流水线每次入库扫一遍，命中就进隔离桶而不是默默丢掉——隔离桶要能复盘是哪个源、哪次抓取带进来的。动态榜或定期换皮题可以降低公开题被背的收益，但不能替代静态检测：换皮之后旧重叠还在训练集里，只是你看不见了。面试里若只说「用过 embedding」，追问他们有没有报「只答案重叠」和公私榜差，没有这两列就不算做过 contamination 检测。

## 追问

- **语义近邻都删会误杀吗？** 会。题意相近但数字、约束、答案不同的要人工复核；误杀会让能力评估偏低，漏杀会让榜虚高。
- **代码/数学为什么更难查？** 变量重命名、格式化、等价变换会躲过字符串匹配，必须规范化 AST / 答案模板再比。
- **和 self-contamination 一句话分？** 泄漏是评测被看见；自污染是训练分布被自己的输出喂胖。两者都要查，门禁不同。
- **发现重叠后怎么处理？** 先隔离该源、重报去污染分数，再决定是否从训练删除；只藏重叠率、继续报公开榜，是面试减分项。
