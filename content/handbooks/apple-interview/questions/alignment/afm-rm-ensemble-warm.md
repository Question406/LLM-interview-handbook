---
id: afm-rm-ensemble-warm
section: alignment
order: 112
level: A
title: 有四个 RM，怎样更可靠、又更省计算地选出好回答？
quick: 四个 RM 都打分再平均，需要跑四个模型；WARM 先合并参数，之后只跑一个模型；保守奖励会给评分分歧大的回答扣分。最终都要检查选出的回答是否更好。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 'WARM: On the Benefits of Weight Averaged Reward Models'
    url: 'https://arxiv.org/abs/2401.12187'
    type: primary
  - title: Helping or Herding? Reward Model Ensembles Mitigate but do not Eliminate Reward Hacking
    url: 'https://arxiv.org/abs/2312.09244'
    type: primary
---

## 这道题在解决什么问题？

同一个 prompt，语言模型生成了 A、B 等几个候选回答。**Reward model（RM）接收 prompt 与一个回答，输出 scalar score，用来帮助排序；它不负责生成回答。** 这些 scores 也可以用作 RL training 的 reward。

单个 RM 可能把“很长、很自信但错误”的回答打成高分。你已经训练了四个 RM，想利用它们改善回答选择，但部署时还要考虑评分成本。本题要求你比较三种方案，说明它们的计算方式、适用条件，以及如何确认选择质量确实变好了。

这是基于公开研究的设计讨论，不是编程题，也不要求背 WARM 的实验数字。

## 面试官可能这样问

1. 如果每个候选回答都可以让四个 RM 打分，直接平均四个 scores 有什么收益和风险？
2. 现在生产预算只允许**每个候选回答跑一个 RM**。WARM 能怎样使用这四个模型？为什么不能把任意 checkpoints 直接平均？
3. 如果仍能获得四个 scores，有人建议用“平均分减去分歧惩罚”选择回答。这和单纯求平均有什么不同？是否能称为可靠的 confidence lower bound？
4. 你会用什么数据和对照实验，在这三种方案之间作出选择？

## 可以这样回答

假设同一个问题有 A、B 两个候选回答，我要决定保留哪一个。RM 就是给“问题＋回答”打分的模型。我有四个 RM，想让它们帮我选得更准，但还得考虑打分需要多少计算。

如果预算允许，我会先试 score averaging：让四个 RM 都打分，再取平均。例如 A 得到 8、8、8、0，平均是 6；B 得到 5、5、5、5，平均是 5，所以这个规则会选 A。分数要先放到可比较的尺度，一个模型打 0–1 分、另一个打 0–100 分，不能直接平均。

但 A 的分数也说明，四个模型对它意见差得很大。如果我想谨慎一点，可以试 conservative reward：在平均分上减去一个与分歧大小有关的惩罚。还是这个例子，用 mean−std，A 大约是 2.54，B 还是 5，就会改选 B。这表示我们更偏好模型意见一致的回答，不代表 B 已经被证明更好。如果四个 RM 都被同一类错误骗过，分歧小也没用。

如果每条回答的预算只够跑一个 RM，前面两种方法就太贵了。这时可以尝试 WARM：假设四个 RM 来自共同的 pre-trained model，模型结构相同、参数能够一一对应，先把它们的 weights 平均，得到一个新的 RM，部署时只跑这个模型。注意，平均 weights 后的模型，不等于四个模型输出分数的平均，所以必须重新测它选出的回答好不好。

最后，我会固定一批问题和候选回答，用独立的人工评价，或代码测试这类正确性检查，比较各方案实际选中了什么，同时测 latency 和成本。预算够时可以比较多模型打分；预算只够一个模型时，就比较单 RM 与 WARM。不会因为方法名字叫 ensemble，就默认它一定更可靠。

## 技术备查

### 三种方案到底平均什么？

给 prompt x 与候选回答 y，第 i 个 RM 的参数为 $\theta_i$，输出为 $r_{\theta_i}(x,y)$。

| 方案 | 做什么 | 部署时每条回答的评分计算 | 主要目的 |
| --- | --- | --- | --- |
| Score averaging | $\bar r=\frac{1}{K}\sum_i r_{\theta_i}(x,y)$ | 运行 K 个 RM，再汇总 scores | 尝试减少成员不一致的错误 |
| WARM / weight averaging | 先得到 $\bar\theta=\frac{1}{K}\sum_i\theta_i$，再算 $r_{\bar\theta}(x,y)$ | 运行一个合并后的 RM | 尝试以单模型成本获得更可靠的打分 |
| Conservative reward | $r_{cons}=\bar r-\lambda s$，s 是该回答的成员分数 standard deviation | 此例仍需运行 K 个 RM | 避免偏好成员分歧较大的高分回答 |

这里的“一个 RM”是每个候选回答的一次模型评分，允许正常 batching；不是说一个 forward 就能无条件给所有长度、所有候选免费打分。Weight averaging 在部署前执行，成员训练成本仍然存在。

非线性模型一般不满足 $r_{\bar\theta}(x,y)=\bar r(x,y)$。因此 WARM 不是把 prediction ensemble 无损压缩成一个完全等价的模型。

### 用具体分数理解 conservative reward

假设四个 RM 的 scores 已经调整到可比较的尺度；分数只是 ranking scores，不是概率。以下使用 population standard deviation：

| 候选回答 | 四个 RM 的 scores | Mean | Standard deviation | Mean − 1×std |
| --- | --- | --- | --- | --- |
| A | 8、8、8、0 | 6 | 约 3.464 | 约 2.536 |
| B | 5、5、5、5 | 5 | 0 | 5 |

只按 mean，选 A；按这个 conservative reward，选 B。区别在于是否惩罚 disagreement。**这个表不能证明 B 的真实质量更好**，它只展示了两种选择规则。四个 RM 一致打错时，standard deviation 也可能为零。

“Mean − 2×std”在本题是待验证的 heuristic，不是 WARM 的定义，也不会因为系数等于 2 就自动成为 95% confidence bound。若要给统计保证，必须另外说明 probability model、成员依赖、calibration 与实际 coverage；这里不假设这些条件已经成立。

### WARM 的适用前提

[WARM 论文](https://proceedings.mlr.press/v235/rame24a.html)研究从共同 pre-trained 来源得到的 fine-tuned RMs 的 weight averaging。实际应用至少需要相同的架构、对应参数的 shape 与语义一致，以及兼容的 tokenizer、输入格式和训练路径。不能把不同架构或独立从头训练的模型，仅因为参数数组尺寸凑得上就平均。

这些条件支持尝试，不保证收益。仍要在 held-out tasks 上检查合并模型；更换 fine-tuning data、hyperparameters 或 checkpoint selection 后需要重新验证。

### 应该怎样评价？

先固定一组 prompts 和候选回答，保证各方案比较的是相同 candidates。以单 RM 为 baseline，分别比较：

- 独立 human preference、verifiable correctness 和安全要求下的选择质量；不要只报告待评价 RM 自己的 reward。
- 当前 policy 与新 policy 产生的 candidates，以及与训练不同的 task types。
- 长度、风格、label noise 和共同 failure modes；测量成员错误的相关性。
- 每条回答的评分 latency、总计算量、显存和 batching 后的 throughput。

用 development set 决定 score normalization、成员组合和 lambda，再用独立 held-out set 验收。不能反复根据最终验收结果选择成员，然后继续把那套数据称为未见测试。

### 追问

**WARM 还保留逐成员 disagreement 吗？** 不直接保留。部署成一个平均权重模型后，单次输出不会同时给出原来 K 个成员的分数与 standard deviation。

**多训练几个相似 RM 一定有用吗？** 不一定。共同的数据偏差或相似训练过程可能造成 correlated errors。[Helping or Herding](https://arxiv.org/abs/2312.09244)也研究了 ensemble 对 reward hacking 的缓解与局限。

**当前只有一个 forward 的预算，能直接使用四成员的 mean−std 吗？** 不能。上面的计算需要成员 scores；若不运行成员，就缺少该输入。需要改预算、使用经过验证的其他 uncertainty estimator，或接受单模型方案的能力范围。
