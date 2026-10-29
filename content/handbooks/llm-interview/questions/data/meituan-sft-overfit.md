---
id: meituan-sft-overfit
section: data
order: 160
level: A
title: 美团：SFT 阶段如何防止 overfitting？
quick: >-
  业务 SFT overfitting 主要来自重复模板和轮数过多，所以先做数据去重、给模板降权、限制有效重复，再控制轮数、混入
  general-capability regression data、用 completion-only mask。早停看换皮 holdout
  上的业务分，训练 cross entropy loss（CE）降到多低说明不了泛化。
tags:
  - Meituan
  - SFT
  - Overfitting
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: 'https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981'
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法；二面
- 届别 / 流程：原帖未披露；二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“微调阶段防止模型 overfitting 的常用方案与实操技巧”**

业务数据上，SFToverfitting 的主因是重复模板和 epoch 太多，所以我会先减少近重复、限制有效重复，然后才谈容量约束和正则。二面别先背 dropout、weight decay，面试官想听的是你怎么发现 overfitting，比如用换皮的 holdout、没见过的门店去测。

overfitting 的样子是训练 cross entropy loss（CE）很低，换个模板或者轻微改写一下表现就明显下降，通用能力也在掉。业务 SFT 的轮数通常很少，数据没去重的话，epoch=2 就已经在背模板了。举个例子，「帮我改一下收货地址」这个意图有几百种写法，但都出自同一个模板族，训完以后换一种说法、换个没见过的门店名，模型就填错字段。难易配比（`meituan-easy-hard-sft-balance`）拧过头也一样，等于把同一撮难例抄了很多遍，overfitting 来得更快。

## 先处理数据，再谈正则

实操上先算「有效重复」：同一个模板族在一个 epoch 里出现多少次，光看数据集有多少行看不出来。模板族太大的话，epoch=1 也会 overfitting。然后做 exact、模板族和语义近重复的去重（`pdd-sft-template-dedup`、`data-semantic-dedup`），模板改写降权。难例可以升 sampling，但同一条别抄十遍，给每条设一个最大有效次数。如果确实要多看几遍难例，用升 sampling 上限加通用锚混入，别靠加 epoch。保留通用指令和短格式的 regression data，防止垂域 SFT 以后只会填本店的 JSON。train 和 holdout 要按题面和答案指纹切开，否则 holdout 被同模板污染，看起来就像没 overfitting。

训练上的技巧有这几个。只对回答计损失（loss）（completion-only mask），免得模型去背 prompt。学习率偏小并做预热。LoRA 本身就是容量约束，全量微调更要少跑几轮。Thinking 开着的时候，要防模型背超长推理里的套话，可以压缩 rationale 或者只监督答案，见 `data-strong-weak` 里讲的可学性。

## 怎么证明没 overfitting

早停看分层 holdout 和格式合法率，别等 CE 降到 0。监控集一定要换皮：同一个意图、不同句式、不同门店名、不同字段顺序。用和训练同模板的 holdout，会停得太晚。对照组有多 epoch 对早停、去重前对去重后、有没有通用锚。报告训练 CE、holdout 业务分、换模板和改写后的鲁棒性、通用能力有没有掉。CE 在降，改写后的同类题却在掉，就是 overfitting 的信号。线上头部的短查询、没见过的门店和句式要单独列出来。

所以回答的顺序是：先查数据重复和 holdout 有没有切错，其次才是容量和正则。dropout 可以提，但别当第一句话，先给出去重率和有效 epoch。

## 追问

**为什么 CE 低不一定好？**
CE 可以靠背模板降到接近 0。换皮测试或 out-of-distribution 数据（OOD，即与训练数据明显不同的数据）才反映泛化。

**LoRA 能防 overfitting 吗？**
能降低容量，但去不掉重复的梯度。近重复数据不处理，LoRA 一样会背。

**难例升 sampling 会不会加重 overfitting？**
会。必须设重复上限，并且和早停、regression data 一起做。

**和配比题怎么衔接？**
overfitting 常常是简单模板占满了，或者难例抄多了。两题共用分层 holdout，讲成同一套逻辑。
