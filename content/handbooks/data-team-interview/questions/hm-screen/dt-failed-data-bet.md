---
id: dt-failed-data-bet
section: hm-screen
order: 3
level: A
title: HM：讲一次数据干预失败了，你怎么知道失败、后来改了什么？
quick: >-
  挑一个对照实验推翻了原先假说的数据实验：算力和 evaluation set
  不变、只改数据，结果目标任务没涨，或者别的能力掉了。接着讲判断错在哪、后来怎么改过滤标准或配额。训练 loss 降了，证明不了数据方案成功。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: FineWeb-Edu
    url: 'https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu'
    type: primary
  - title: Data Mixing Laws
    url: 'https://arxiv.org/abs/2403.16952'
    type: primary
  - title: The Curse of Recursion / Model Collapse
    url: 'https://arxiv.org/abs/2305.17493'
    type: primary
---

我会挑一个对照实验推翻了我原先判断的数据实验。算力和 evaluation set 不变，只改数据，结果目标任务没涨，或者别的能力掉了。训练 loss 降了也一样算失败，目标任务没改善就是没成。

HM 常在你讲完成功故事后紧接着问这个，拿不出来会显得只报喜。数据工作里失败本来就常见，过滤能带来收益，也可能滤过头，FineWeb 一类工作的公开教训就是这个，AFM 2025 也写过启发式过猛会扔掉好的 token。

讲法沿用 `dt-data-story` 的顺序，只是这次指标说明假说没成立。比如我以为论坛答疑能补 multilingual 指令，加了 8% 进去，结果该语言的 IFEval 没动，英语摘要 human evaluation 还掉了一档。和 token 数相同的旧 mix 在冻结集上一比，就确认不是波动。抽查一看，过滤器把代码块当低质扔了，留下来的是短闲聊。后来我把代码和数学拆成单独的桶，论坛配额收到 3%，再用一份 summarization regression set 保住已有能力。回头看，错在我默认「这个语言的任何文本都有用」。这里的数字都是示意，〔填：你自己的假说、对照结果、attribution 和改动。〕没有线上 human evaluation，用冻结 evaluation slices 加抽查也行。

假说可以很简单，比如「再加 200 万条 teacher CoT，MGSM 会涨」，结果 target evaluation slices 持平，英语指令或安全指标掉了，或者只有合成 holdout 涨了。attribution 也可能是覆盖其实已经够了、teacher 给的推理过程是假的，或者评测被你自己的生成器 contamination 了。最好挑过滤阈值、teacher 质量或 data mix 导致的失败，集群故障说明不了你的数据判断。

收尾要落在数据动作上：关掉那一桶，加一道过程检查，把配额从 15% 收回到 5%，或者换掉 held-out evaluation examples。「后来换了更大的模型才好」不算数据失败的收场，那等于换了一道题。

## 追问

**还有哪几种失败值得提前准备？**
有四种比较典型。合成 holdout 暴涨、真实来源的评测不动，说明模型在背生成器的输出，evaluation gate 只用真实来源的题，synthetic data 当 development set，见 `dt-contamination`。目标指标涨了、regression tasks 掉了，是 negative transfer，保留 regression data quota 来维持已有能力，再做 leave-one-source-out 找来源，见 `dt-neg-transfer`。human evaluation 喜欢、任务核验却下降，模型学到的是长度或客套，做分层 human evaluation、把 rule-based reward 单独列出来，见 `dt-length-hack-data`。加了 hard examples 后 RL 出现空组，是难度超出了 pass@$k$ 能覆盖的范围，降难度或先用 SFT 冷启动，见 `dt-self-improve`。

**当时为什么没先做 small model sweep？**
没做就承认。现在的规矩是先用 1B 模型或短训看 $\Delta$，再放到目标模型上。

**失败会不会让人觉得你判断差？**
不会。判断差的表现是没有对照、没有停损，拿得出证伪指标、及时止损，正是数据团队该做的事。

**这和 See Around Corners 冲突吗？**
不冲突。提前做的判断也可以被证伪，证伪了关掉就行，见 `dt-see-around-corners`。
