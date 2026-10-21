---
id: dt-failed-data-bet
section: hm-screen
order: 3
level: A
title: HM：讲一次数据干预失败了，你怎么知道失败、后来改了什么？
quick: "选一个对照实验否定了原先假说的数据实验：算力和评测集不变、只改数据，结果目标任务没改善，或者其他能力退步了。再讲原来的判断错在哪里，后来怎样调整过滤标准或配额。训练 loss 降低本身，不能证明数据方案成功。"
companies:
  - apple
tags:
  - Apple
  - Hiring Manager
  - Data Intervention
  - Failure
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
  - title: The Curse of Recursion / Model Collapse
    url: https://arxiv.org/abs/2305.17493
    type: primary
---

我会选一个结果不支持原先假说的数据实验。实验保持算力和评测集不变、只改训练数据，这样才能判断数据本身有没有用。训练 loss 降了，但目标任务没有改善，仍然算失败。

HM 常在你讲完成功故事后，紧接着问失败。拿不出失败的例子，会显得你只报喜。数据工作里失败很常见：FineWeb 一类工作的公开教训是，过滤可以带来收益，也可能滤过头；AFM 2025 也写过，启发式过猛会扔掉好的 token。

## 失败要能指回假说

可以沿用 `dt-data-story` 的讲述顺序，只是这一次，指标说明假说没有成立：

1. 先说假说，例如「再加 200 万条教师 CoT，MGSM 会涨」。
2. 再说对照：token 数相同的旧 mix 和新 mix，在冻结集上比较。
3. 然后说结果：目标切片持平，英语指令或安全指标下降；或者只有合成 holdout 上涨。
4. 接着归因：覆盖其实已经够了，教师给的推理过程是假的，过滤器误杀了相邻内容，或者评测被你自己的生成器污染了。
5. 最后说改动：关掉那一桶数据，加一道过程检查，把配额从 15% 收回到 5%，或换掉门禁题。

最好选过滤阈值、教师质量或数据配比导致的失败；集群故障说明不了你的数据判断。收尾也要落在数据动作上。「我们后来换了更大的模型才好」不算数据失败的收场，那等于换了题目。

## 一个例子

「我以为论坛答疑能补多语指令。加了 8% 之后该语言 IFEval 平，英语摘要人评掉了 1 档。抽查看：过滤器把代码块当低质扔了，留下的是短闲聊。我把代码 / 数学拆出单独桶，论坛配额收到 3%，锚点摘要集托底。假说错在『该语言的任何文本都有用』。」

数字换成你自己有的。没有线上人评，用冻结切片和抽查也可以。

## 几种值得准备的失败

- 合成 holdout 暴涨，真实来源上的评测不动。这说明模型在背生成器的输出。处理方法是门禁只用真实来源的题，合成数据只当开发集，见 `dt-contamination`。
- 目标指标涨了，锚点掉了。这是负迁移。用锚点配额托底，再做 leave-one-source-out 定位来源，见 `dt-neg-transfer`。
- 人评喜欢，任务核验却下降。模型学到的是长度或客套。做分层人评，把规则奖励单独列出来，见 `dt-length-hack-data`。
- 加了难例之后，强化学习（RL）出现空组。难度超出了 pass@$k$ 能覆盖的范围。降低难度，或者先用监督微调（SFT）冷启动，见 `dt-self-improve`。

## 追问

- **当时为什么没先做小模型 sweep？** 承认没做。现在的规矩是先用 1B 模型或短训看 $\Delta$，再放到目标模型上。
- **失败会不会让人觉得你判断差？** 判断差的表现是没有对照、没有停损。能拿出证伪指标、及时止损，正是 data team 该有的做法。
- **和 See Around Corners 冲突吗？** 两者可以并存。提前做的判断也可以被证伪，证伪后关掉就行，见 `dt-see-around-corners`。
