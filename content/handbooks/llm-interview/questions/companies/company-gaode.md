---
id: company-gaode
section: companies
order: 19
level: A
title: 高德 / 阿里出行：大模型算法应重点准备什么？
quick: >-
  出行场景强调可验证奖励与地图约束：DAPO 为何能弱化显式 KL、GRPO 后期收益衰减怎么救、以及路线 / POI
  类任务如何避免奖励黑客。对照阿里系 Post-Training 卡，再补一张出行特有的约束评测故事。
tags:
  - Amap
  - Alibaba
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 高德大模型算法岗二面面经（相关推荐收录于百度面经页）
    url: https://www.nowcoder.com/discuss/863890669662674944
    type: secondary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

高德题常落在「有 verifier 的推理 RL」，陷阱是空泛聊 Agent / 导航话术，却说不清动态采样、全对/全错组、以及路线几何约束如何进奖励。准备时把路线规划、POI 问答做成**可自动打分**任务：对了什么、错了什么、哪一步违反交通规则，都能写进 rubric。对照阿里系 DAPO / GRPO 卡，再补一条出行特有的约束评测，不要只背论文标题。

## 准备主线

1. **DAPO vs GRPO**：动态采样丢掉全对/全错组、token 级策略、clip-higher；解释为何可以减弱显式 $\beta\mathrm{KL}$。见 `gaode-dapo-no-kl`、`pt-dapo`、`ali-dapo-allcorrect`。
2. **后期衰减**：奖励饱和、熵塌缩、过易 prompt、verifier 泄漏。GRPO 后期收益掉下来时，先查组内优势是否全零、再查难度与泄漏，而不是加大 $\beta$。相关机制见 `pt-grpo-variance`、`data-entropy-collapse`。
3. **出行约束**：几何可行、交通规则、用户硬约束（途经点、禁行、ETA 上限）不能被「说得像对了」绕过。奖励应拆成 hard gate（不可行直接 0）+ 过程分（违规步数）+ 结果分（是否到达）。评测要有对抗绕路、伪造 ETA 的 hacking case。

## 本手册真题卡

点击下面每条即可跳到对应题。

- `gaode-dapo-no-kl`：高德大模型：DAPO 为什么可以不额外加 KL 惩罚？GRPO 后期收益衰减怎么优化？
- `pt-dapo`：DAPO 动态采样与 clip-higher
- `ali-dapo-allcorrect`：全对组怎么处理
- `pt-grpo`：GRPO 组内优势与零优势
- `data-entropy-collapse`：熵塌缩时数据侧怎么救

## 追问

- **为什么 DAPO 可以弱化显式 KL？** 动态采样提高组内区分度，clip-higher 限制过大更新；KL 不再是唯一防塌缩手段。仍要监控熵和偏离，不是「删了 KL 就完事」。
- **路线任务如何防奖励黑客？** 只看「到达」会被绕禁行或虚报；硬约束用地图引擎验，过程步用规则打分。
- **后期衰减先改算法还是先改题？** 先看 prompt 是否过易、verifier 是否泄漏；全对组优势为 0，加大步数无效。按 id 把实验讲成对照，不要背出行口号。
