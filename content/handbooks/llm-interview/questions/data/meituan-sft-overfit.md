---
id: meituan-sft-overfit
section: data
order: 160
level: A
title: 美团：SFT 阶段如何防止过拟合？
quick: "控制轮数和有效重复、混合通用锚点、completion-only mask、早停看 holdout 业务分而不是训练 交叉熵损失（CE）。数据去重和降权模板比再加 dropout 更关键。"
tags:
  - Meituan
  - SFT
  - Overfitting
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法；二面
- 届别 / 流程：原帖未披露；二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“微调阶段防止模型过拟合的常用方案与实操技巧”**

监督微调（SFT） 过拟合表现为训练 交叉熵损失（CE） 很低、更换模板或轻微改写后表现明显下降、通用能力掉。二面不要先背 dropout / weight decay。业务数据上，重复模板和过多 epoch 才是主因。先减少近重复数据，再限制有效重复，再谈容量约束。难易配比（`meituan-easy-hard-sft-balance`）拧过头，等于把同一撮难例抄很多遍，过拟合会更快。面试官要听的是你怎么发现过拟合（换皮 holdout、未见门店），不是正则名词表。业务 SFT 轮数通常很少，数据没去重时 epoch=2 已经在背模板。

## 数据侧先于正则

先做 exact / 模板族 / 语义近重（`pdd-sft-template-dedup`、`data-semantic-dedup`），模板改写降权。难例可以升采样，但同一条不要抄十遍；设每条最大有效次数。保留通用指令与短格式锚，防止垂域 SFT 后只会填本店 JSON。train/holdout 按题面和答案指纹切开，避免 holdout 被同模板污染后「看起来没过拟合」。

训练技巧：只对回答计 损失（loss）（completion-only mask），避免背 输入提示（prompt）；学习率偏小并预热；LoRA 本身是容量约束，全量微调更要少轮。早停看分层 holdout 和格式合法率，不看 CE 是否到 0。Thinking 开着时防背很长的推理过程套话：对 rationale 做压缩或只监督答案，见 `data-strong-weak` 的可学性。

## 怎么证明没过拟合

对照：多 epoch vs 早停、去重前后、有无通用锚。报告训练 CE、holdout 业务分、换模板/改写鲁棒、通用能力是否掉。CE 下降，但改写后的同类题表现下降，就是过拟合的信号。线上头部短查询和未见门店/未见句式要单列。不要用「加了 dropout」交差，先给出去重率和有效 epoch。

实操上先算「有效重复」：同一模板族在一个 epoch 里出现多少次，而不是只看数据集行数。模板族过大时，即使 epoch=1 也会过拟合。早停的监控集必须换皮：同意图不同句式、不同门店名、不同字段顺序；用训练同模板的 holdout 会让你停太晚。若必须多看几遍难例，用升采样上限 + 通用锚混入，而不是加 epoch。过拟合先查数据重复和错误 holdout，其次才是容量和正则；dropout 可以提，但不能当第一句话。

## 追问

- **为什么 CE 低不一定好？** CE 可以靠背模板降到接近 0；换皮或 分布外数据（OOD，即与训练数据明显不同的数据） 才反映泛化。
- **LoRA 能防过拟合吗？** 能降低容量，但去不掉重复梯度。数据近重不处理，LoRA 一样背。
- **难例升采样会不会加重过拟合？** 会。必须设重复上限，并和早停、锚点数据一起做。
- **和配比题怎么衔接？** 过拟合常是简单模板占满或难例抄多；两题共用分层 holdout，不要各讲一套故事。
