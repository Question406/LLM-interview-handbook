---
id: snorkel-iterative-dpo
section: posttrain
order: 3
level: S
title: Snorkel：五条回复取最好和最差，做三轮 DPO
quick: >-
  只用 UltraFeedback 的 prompt，Mistral-7B 自己生成 5 条，PairRM 排序，最好对最差做 DPO，重复三轮。
  AlpacaEval 2.0 从 14.72 到 30.22。他们写明裁判偏长回答，奖励模型可能把这个偏差学进去了。
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

## 题怎么来的

这不是一则候选人复盘。Snorkel 把配方写在模型卡和两篇博客里，RL Training 的科研岗位则点名 GRPO、RLHF、RLAIF、DPO、奖励模型和 credit assignment。面他们的后训练岗，这套循环就是他们自己的例子。`realInterview: false`。

模型卡上的循环：

1. 从 UltraFeedback 取 prompt，不用里面别人生成的回答。子集大约 2 万条。
2. 当前模型为每条 prompt 生成 5 个回答。起点是 Mistral-7B-Instruct-v0.2。
3. 用 PairRM 排序。
4. 最高分当 chosen，最低分当 rejected，做 DPO。
5. 把更新后的模型当成下一轮的生成模型，一共三轮。

数据格式走 Hugging Face 的 Zephyr 配方。AlpacaEval 2.0 上基座 14.72，三轮之后 30.22。再用 PairRM 做 best-of-16，到 34.86。裁判是 gpt-4-turbo。

## 为什么丢掉的是最差，不是随机一条

博客写了消融。第一版把最高分当 chosen，其余几条里随机抽一条当 rejected。后来改成丢掉最低分，榜上的数更好。随机负例经常和正例差不多，DPO 的间隔推不动。最差的那条把间隔拉大，梯度才明显。

平局要丢。五条分数如果一样，硬拆 chosen / rejected 是在教模型噪声。

```python
def pair_from_scores(texts, scores):
    order = sorted(range(len(texts)), key=lambda i: scores[i])
    worst, best = order[0], order[-1]
    if scores[best] == scores[worst]:
        return None
    return texts[best], texts[worst]
```

他们还写了直接做 RLHF 时 loss 炸过，输出变重复。同一批偏好改走 DPO 之后曲线稳定。算力是他们选 DPO 的理由，不是「DPO 在所有目标上都更强」。要探索、要细到步骤的 credit 时，岗位文本把 GRPO 和 RLHF 放回来，见 `scale-process-outcome`。

## 长度

模型卡自己写了：AlpacaEval 2.0 的裁判偏向更长的回答，PairRM 可能带同样的偏向，DPO 几轮之后回答变长，名次里有这一份。所以 30.22 不能当成「指令跟随变好了」的唯一证据。我会同时报长度中位数、截断到相同长度后的胜率，以及一个不看文风的任务集。

企业场景他们的结论相反：通用 PairRM 不够，任务奖励模型要由业务专家定轴。Self-rewarding（让同一个 LLM 给自己打分）他们点名不适合这种场景。

## 追问

**五条都来自当前模型，和人标的偏好对有什么不同？** 负例是模型自己的坏样本，分布贴着当前策略。人标的负例常常来自另一个模型，DPO 的 $\pi_{\mathrm{ref}}$ 对不上。贴着当前策略的对，更接近 on-policy，也更容易把奖励模型的毛病放大，因为没有人把「长但空」从最高分里拿掉。

**为什么不拿第 1 名对第 2 名？** 相邻名次的分差小，标签噪声占比大。最好对最差是他们选的间隔。若业务上「能用」和「不能用」的边界在中间，应该按阈值切，而不是按名次极端切。

**三轮之后还用最初的参考模型吗？** 模型卡写每一轮的基座是上一轮更新后的模型。参考模型若一直钉在最初的 Mistral 上，后面几轮的 KL 会把策略拽回去。参考模型应跟着当前轮的起点走。这个细节模型卡没有写死，我会在面试里主动说这是未公开的选择。
