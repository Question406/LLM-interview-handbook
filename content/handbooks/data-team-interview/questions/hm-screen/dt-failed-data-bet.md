---
id: dt-failed-data-bet
section: hm-screen
order: 3
level: A
title: HM：讲一次数据干预失败了，你怎么知道失败、后来改了什么？
quick: "先说对照结果：保持算力和评测集不变，只改数据，目标任务没有改善，或者其他能力退步了。再解释原来的判断错在哪里，以及后来怎样调整过滤标准或配额。训练 loss 降低本身，不能证明数据方案成功。"
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

我会选一个结果不支持原先假说的数据实验。实验保持算力和评测集不变，只改训练数据，这样才能判断数据是否有用。训练 loss 降了，但目标任务没改善，仍然算失败。

不这么选的理由：HM 常在成功故事后面补一刀。没有失败例子会显得你只报成功。FineWeb 一类工作的公开教训是过滤可以赢，也可以滤过头。AFM 2025 写过启发式过猛会扔好 文本处理单位（token）。

## 失败要能指到假说

可以沿用 `dt-data-story` 的讲述顺序，不过这次指标表明假说没有成立：

1. 假说。例如「再加 200 万教师 CoT，MGSM 会涨」。
2. 对照。等 token 的旧 mix vs 新 mix，冻结集。
3. 结果。目标切片平，英语指令或安全掉；或只有合成 holdout 涨。
4. 归因。覆盖其实已经够、教师过程假、过滤器误杀了邻域、评测被自己的生成器污染。
5. 改动。关那一桶、加过程门、把配额从 15% 收回 5%、换门禁题。

最好选过滤阈值、教师质量或数据配比导致的失败。集群故障说明不了你的数据判断。

## 几种值得准备的失败

- 合成 holdout 暴涨、真源不动。在背生成器。处理：门禁用真源，合成只当开发集，见 `dt-contamination`。
- 目标涨、锚点掉。负迁移。处理：锚点配额托底，leave-one-source-out，见 `dt-neg-transfer`。
- 人评爱、任务核验掉。长度或客套。处理：分层人评、规则奖励单列，见 `dt-length-hack-data`。
- 加了难例，强化学习（RL） 空组。难度超出 pass@$k$。处理：降难度或先 监督微调（SFT） 冷启动，见 `dt-self-improve`。

「我们后来换了更大模型才好」不算数据失败的收场，那是换题。要收在数据动作上。

## 举例

「我以为论坛答疑能补多语指令。加了 8% 之后该语言 IFEval 平，英语摘要人评掉了 1 档。抽查看：过滤器把代码块当低质扔了，留下的是短闲聊。我把代码 / 数学拆出单独桶，论坛配额收到 3%，锚点摘要集托底。假说错在『该语言的任何文本都有用』。」

数字换成你有的。没有线上人评，用冻结切片和抽查也可以。

## 追问

- **当时为什么没先做小模型 sweep？** 承认。现在的规矩是先 1B 或短训看 $\Delta$，再放到目标模型。
- **失败会不会让我觉得你判断差？** 判断差的是没有对照、没有停损。有证伪指标反而像 data team。
- **和 See Around Corners 冲突吗？** 不冲突。预见也可以证伪；证伪后关掉，见 `dt-see-around-corners`。
