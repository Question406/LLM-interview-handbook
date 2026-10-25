---
id: company-gaode
section: companies
order: 19
level: A
title: 高德 / 阿里出行：大模型算法应重点准备什么？
quick: "高德题常落在有 verifier 的推理 RL 上，我会强调可验证奖励和地图约束：DAPO 为什么能弱化显式 KL、GRPO 后期收益下降时怎么排查、路线和 POI 类任务怎么防奖励黑客。对照阿里系 Post-Training 卡，再准备一个出行约束评测的具体例子。"
tags:
  - Amap
  - Alibaba
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 高德大模型算法岗二面面经（相关推荐收录于百度面经页）
    url: https://www.nowcoder.com/discuss/863890669662674944
    type: secondary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

高德的题常落在「有 verifier 的推理 RL」上。空泛地聊 Agent 和导航话术不够，面试官会问动态采样、全对或全错组怎么处理，路线的几何约束怎么进奖励。

我准备时会把路线规划、POI 问答做成能自动打分的任务，对了什么、错了什么、哪一步违反了交通规则，都能写进 rubric。比如用户要求经过某个途经点，模型给的路线却绕开了它，回答写得再像样，硬约束这一关也要直接判掉。然后对照阿里系 DAPO、GRPO 卡，再补一条出行特有的约束评测，光背论文标题不够。

## 准备主线

1. DAPO 和 GRPO 的区别在动态采样丢掉全对或全错组、token 级策略和 clip-higher，要能解释为什么可以减弱显式 $\beta\mathrm{KL}$，见 `gaode-dapo-no-kl`、`pt-dapo`、`ali-dapo-allcorrect`。
2. 后期衰减的常见原因是奖励饱和、熵塌缩、输入提示（prompt）过易、验证器（verifier）泄漏。GRPO 后期收益掉下来时，先查组内优势是不是全零，再查难度和泄漏，先别去加大 $\beta$。相关机制见 `pt-grpo-variance`、`data-entropy-collapse`。
3. 出行约束包括几何可行、交通规则和用户硬约束（途经点、禁行、ETA 上限），这些都不能被「说得像对了」绕过。奖励我会拆成三层：硬性条件不满足直接给 0，过程分看违规步数，结果分看是否到达。评测里要有对抗绕路、伪造 ETA 的 hacking case。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `gaode-dapo-no-kl`：高德大模型：DAPO 为什么可以不额外加 KL 惩罚？GRPO 后期收益衰减怎么优化？
- `pt-dapo`：DAPO 动态采样与 clip-higher
- `ali-dapo-allcorrect`：全对组怎么处理
- `pt-grpo`：GRPO 组内优势与零优势
- `data-entropy-collapse`：熵塌缩时数据侧怎么救

## 追问

**为什么 DAPO 可以弱化显式 KL？**
动态采样提高了组内区分度，clip-higher 限制过大的更新，KL 就不再是唯一的防塌缩手段。熵和偏离还是要监控，删了 KL 不等于完事。

**路线任务怎么防奖励黑客？**
只看「到达」，模型会去绕禁行或者虚报。硬约束交给地图引擎验，过程步用规则打分。

**后期衰减先改算法还是先改题？**
先看题。查 prompt 是不是过易、verifier 有没有泄漏；全对组的优势为 0，加大步数也没用。按上面的 id 把实验讲成对照。
