---
id: snorkel-iterative-dpo
section: posttrain
order: 3
level: S
title: Snorkel：五条回复取最好和最差，做三轮 DPO
quick: "Snorkel 从 UltraFeedback 只取 prompt，让当前 Mistral-7B 为每题生成 5 个回答，用 PairRM 排序，再拿最好和最差的回答做 DPO，重复三轮。AlpacaEval 2.0 从 14.72 涨到 30.22。不过裁判偏爱长回答，奖励模型可能学进了这个偏差，要连同回答长度一起看分数。"
tags:
  - Snorkel
  - DPO
  - Reward Model
  - Post-training
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Snorkel-Mistral-PairRM-DPO model card
    url: https://huggingface.co/snorkelai/Snorkel-Mistral-PairRM-DPO
    type: primary
  - title: How Snorkel topped the AlpacaEval leaderboard
    url: https://snorkel.ai/blog/how-snorkel-topped-the-alpacaeval-leaderboard-and-why-we-re-not-there-anymore/
    type: primary
  - title: Scaling human preferences in AI
    url: https://snorkel.ai/blog/scaling-human-preferences-in-ai-snorkel-s-programmatic-approach/
    type: primary
  - title: Research Scientist, RL Training
    url: https://job-boards.greenhouse.io/snorkelai/jobs/6009496004
    type: primary
---

## 题目描述

本卡原本讨论论文中的偏好数据构造流程；以下编程子题由手册从该流程中提炼，不是已披露的公司面试原题。

### 实现目标

实现 `pair_from_scores(texts, scores)`：从同一个 prompt 的候选回答中选出一对偏好样本。`texts` 是非空字符串列表，`scores` 是相同长度的有限实数列表，一一对应；分数越大越好。输入均合法，且不修改任一输入列表。

若全部分数相等，返回 `None`，表示没有严格偏好。否则返回 `(chosen, rejected)`，分别是最高分和最低分对应的文本。为使结果可重复，最高分并列时选择输入位置最后的回答，最低分并列时选择输入位置最前的回答。这里只有这一固定规则，无需加入阈值、随机采样或模型调用。

### 示例与提交

- `texts=["bad","good","ok"]`、`scores=[1,3,2]`，返回 `("good","bad")`。
- `texts=["a","b"]`、`scores=[2,2]`，返回 `None`。
- `texts=["low1","low2","high1","high2"]`、`scores=[0,0,2,2]`，返回 `("high2","low1")`。

提交函数和使用这些合法输入的简单测试，覆盖单个候选、全等分数和并列最高/最低分。

## 解题思路与参考答案

Snorkel 的配方是让模型自己跟自己比：当前模型对每条 prompt 生成 5 个回答，PairRM 排序，最好的当 chosen、最差的当 rejected 做 DPO，更新后的模型接着生成下一轮，一共三轮。AlpacaEval 2.0 从 14.72 涨到 30.22，不过他们自己也写了，裁判偏长回答，这个分里有长度的份。

这题不是候选人复盘，`realInterview: false`。配方写在 Snorkel 的模型卡和两篇博客里，他们的 RL Training 科研岗位则点名 GRPO、基于人类反馈的强化学习（RLHF）、RLAIF、直接偏好优化（DPO）、奖励模型和 credit assignment。面他们的后训练岗，这套循环就是他们自己的例子。

循环是这样转的。从 UltraFeedback 只取输入提示（prompt），里面别人生成的回答不用，子集大约 2 万条。起点是 Mistral-7B-Instruct-v0.2，当前模型为每条 prompt 生成 5 个回答，用 PairRM 排序，最高分当 chosen、最低分当 rejected 做 DPO，然后把更新后的模型当成下一轮的生成模型，一共三轮。数据格式走 Hugging Face 的 Zephyr 配方。AlpacaEval 2.0 上基座 14.72，三轮之后 30.22，再用 PairRM 做 best-of-16 到 34.86，裁判是 gpt-4-turbo。

选择负例时，要解释为什么用最差的回答，以及为什么不随机挑一条。博客里有消融：第一版把最高分当 chosen，其余几条里随机抽一条当 rejected；后来改成拿最低分，榜上的数更好。随机负例经常和正例差不多，DPO 的间隔推不动；最差那条把间隔拉大，梯度才明显。平局要丢，五条分数要是一样，硬拆 chosen / rejected 等于在教模型噪声：

```python
def pair_from_scores(texts, scores):
    order = sorted(range(len(texts)), key=lambda i: scores[i])
    worst, best = order[0], order[-1]
    if scores[best] == scores[worst]:
        return None
    return texts[best], texts[worst]
```

为什么用 DPO？他们写了直接做 RLHF 时 loss 出现过数值异常，输出变得重复，同一批偏好改走 DPO 之后曲线稳定。他们给的理由是算力，没说 DPO 在所有目标上都更强。要探索、要细到步骤的 credit 时，岗位文本把 GRPO 和 RLHF 放了回来，见 `scale-process-outcome`。

长度这件事我会主动讲。模型卡自己写了：AlpacaEval 2.0 的裁判偏向更长的回答，PairRM 可能带同样的偏向，DPO 几轮之后回答变长，名次里有这一份。所以 30.22 不能当成「指令跟随变好了」的唯一证据，我会同时报长度中位数、截断到相同长度后的胜率，再加一个不看文风的任务集。

企业场景他们的结论正好相反：通用 PairRM 不够，任务奖励模型要由业务专家定轴。Self-rewarding，也就是让同一个 LLM 给自己打分，他们点名说不适合这种场景。

## 追问

**五条都来自当前模型，和人标的偏好对有什么不同？**
负例是模型自己的坏样本，分布贴着当前策略，更接近 on-policy。人标的负例常常来自另一个模型，和 DPO 的 $\pi_{\mathrm{ref}}$ 对不上。代价是更容易把奖励模型的毛病放大，因为没有人把「长但空」从最高分里拿掉。

**为什么不拿第 1 名对第 2 名？**
相邻名次的分差小，标签噪声占比大，最好对最差是他们选的间隔。要是业务上「能用」和「不能用」的边界在中间，就该按阈值切，按名次取两头就不合适了。

**三轮之后还用最初的参考模型吗？**
我会让参考模型跟着当前轮的起点走。模型卡写的是每一轮的基座是上一轮更新后的模型，参考模型要是一直钉在最初的 Mistral 上，后面几轮的 KL 会把策略拽回去。这个细节模型卡没有写死，面试里我会主动说这是未公开的选择。
