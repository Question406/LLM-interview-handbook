---
id: pdd-sft-template-dedup
section: data
order: 104
level: A
title: 拼多多大模型算法：SFT 数据怎样避免模板化，并做 train / test 去重？
quick: >-
  模板化和去重放在一起答：sampling 时按意图、约束、领域、表达方式和答案策略卡配额，同一模板的改写只算表达多样，不算新样本；切分前做
  lexical、semantic 和 split leakage 检查，「相似但约束不同」的 hard case 人工核验后保留。最后看新鲜业务 slice
  和换模板鲁棒性，去重率只是过程指标。
tags:
  - PDD
  - SFT Data
  - Data Deduplication
  - Evaluation Leakage
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 拼多多日常实习 大模型算法一面分享（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/ba50ad3b3777443da540fcd9cfaf7377'
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型算法
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-15
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“SFT 数据如何更贴近业务：如何避免过度模板化？如何做基础的 train/test 去重来避免评测失真？”**

这两问我会放在一起答：模板化是训练信号太单一，去重是防止评测被同一道题记住，两件事都在 sampling 和切分时管住，最后看新鲜业务 slice，去重率只是过程指标。用「换个说法」冒充多样性，再从同一批改写里切出评测集，holdout 总分会很高，可那只是在背题。最廉价的改写会把同一条决策路径抄满。

拼多多这类业务 SFT 最容易出的情况，是拿后台字段做填空，比如「商品 {名称} 的发货地是 {城市}」，填出一大批，看起来量很大，决策路径其实只有一条。评测再从这批里切，分数会虚高到没法上线。所以我先把业务目标拆成 intent、输入约束、上下文、决策路径、输出格式和风险等级，按覆盖缺口主动 sampling。可以用不同作者或生成器、反事实扰动、错误修复样本来补，但每条都要留质量判定和血缘。GPT 改写（`minimax-data-quality-gpt`）只能补表达，算不上新意图。

配额在 sampling 时就卡住：每个 intent × 输出 schema 设上限，模板族要记账，同一个 schema 的填空样本超过配额就降权，超出来的改写进「表达池」，不进「新样本池」。贴近业务靠的是真实日志里的约束和失败修复，把后台字段名换成人话重复一百遍没有用。语义去重（`data-semantic-dedup`）判断的是是不是同一个 training signal，同一题的多种解法可以留 $k$ 条。

train / test 去重在 split 之前做：先 exact / normalized match，再 n-gram / MinHash（`data-minhash`），再对 embedding 近邻或同一 source document 做语义泄漏检查（`data-contamination`）。删的时候别机械删，题面高度相似、但约束、答案或工具 state 不同的样本，要人工抽检后留下，删掉会伤处理 borderline cases 的能力。评测集本身要按时间切分，并且和 train 出一张重叠表（`pdd-offline-eval-coverage`），否则「贴近业务」的 SFT 会把评测洗进训练。

验证的对照做四档：未去重、只 lexical、lexical 加 semantic、再加人工 hard case，看 holdout、换模板后的鲁棒性和新 query slice。只有去重率在升、新鲜 slice 不升，说明要么在删多样性，要么评测还在泄漏。给面试官看两张图就够：跨 split 最近邻相似度的直方图，和按模板族拆开的 holdout。某个模板族接近满分、换个皮就掉到零，就是泄漏或者在背模板。

## 追问

**改写算多样性吗？**
算表达多样，决策路径重复的不算。按答案策略分族，超了配额就降权。

**「相似但要留」的 hard case 是什么样的？**
题意很近，但约束或工具状态不同，需要不同的决策。机械删掉会影响 borderline-case performance。

**去重率能当 KPI 吗？**
不行。KPI 是新鲜业务 slice 和换模板鲁棒性，去重率只是过程量。

**这题和 contamination 题怎么区分？**
这题讲 SFT 的 split 和贴近业务；contamination 讲评测被预训练语料看见。两边的指纹可以共用。
