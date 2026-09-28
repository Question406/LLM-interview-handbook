---
id: tesla-autolabel
section: xai
order: 10
level: A
title: Tesla：自动标注质量门禁，人在环抽查比例怎么定
quick: >-
  先定事故代价，再定可容忍错误率，用分层抽样和置信区间算人审条数。高严重度近乎全审，高速公路常规帧低比例。不要编 Tesla
  内部抽查百分比。
tags:
  - Tesla
  - Auto Labeling
  - Quality Gate
  - Human-in-the-loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Tesla AI Day 2021
    url: https://www.youtube.com/watch?v=j0z4FweCy4M
    type: primary
  - title: Tesla AI Day 2022
    url: https://www.youtube.com/watch?v=ODSJsviD_SU
    type: primary
  - title: Tesla AI
    url: https://www.tesla.com/AI
    type: primary
  - title: Tesla's data engine — the road to full self-driving
    url: https://www.taivo.ai/tesla-data-engine/
    type: secondary
---

## 题怎么来的

数据 / 标注平台岗会问：离线自动标注已经很快，人还看多少、怎么保证没把系统误差写进训练集。公开叙事是 AI Day 的向量空间自动标注：多相机、时序、未来帧，人从改错而不是从零画。抽查比例 Tesla 没有公布，面试要讲怎么定，不要假装知道车内是 1% 还是 10%。闭环位置见 `tesla-data-engine`。

## 质量门：协议、金标、分层

先钉三件事，再谈比例：

1. 标注协议。占用、框、车道各自什么叫错。墙后行人算占用还是 unknown，必须写死，否则人和模型永远吵。Occupancy 的可见 mask 见 `tesla-occupancy-net`。
2. 冻结金标集。双人标 + 仲裁的一小撮 clip，自动标注先过这套门：IoU、漏检、假阳、时序跳动。金标不能用当前自动标注刷新。
3. 按风险分层。施工、行人、加塞、夜间、自动标注低置信、多模型互不一致，这些层的抽查密度远高于空旷高速；不要 i.i.d. 抽帧。

人在环是审计和改错，不是产能瓶颈上的画框。自动标注过门的大批量可以低比例抽；没过门的要么全改，要么丢掉不上训练。丢掉比脏标签便宜。

## 抽查比例：用错误率和置信区间

设某层真实错误率为 $p$，要在置信度 $1-\alpha$ 下把估计误差控制在 $e$ 内。正态近似：

$$
n \approx \frac{z_{1-\alpha/2}^2\, p(1-p)}{e^2}.
$$

$p$ 未知时用 $p=0.5$ 最保守，或用金标上的试点 $\hat p$。例：某层试点 $\hat p=0.02$，想 $e=0.01$、$z=1.96$，则 $n \sim 750$ 量级。这是该层要审的条数，不是全局百分比。流量 10 万 clip 时，这一层看起来像 0.75%；流量 1000 时就是 75%。所以面试说「比例随流量和风险走」，不说「Tesla 抽 2%」。

Wilson 区间比正态更适合小 $p$，跟面试官提一句就够。双重标不一致率是另一道门：人和自动标、人和人。不一致高说明协议烂或模型系统偏，应停扩规模，先修协议。

严重度我会显式分层（示意，不是内部规定）：

- 安全关键（行人、反向来车、交通灯）：自动标只做预填，人审接近全覆盖，直到金标错误率掉到协议以下。
- 几何常规（高速车道线）：低比例抽查 + 触发式全审（模型互搏、低置信）。
- 新域（新城市、新天气）：临时拉高抽查，直到 $\hat p$ 稳定再降。

时序检查可以自动做门禁：相邻帧框跳变、占用体积闪烁、多相机投影对不上。这类规则过滤不占人时，放在人审前面。人只看规则过不了或规则不确定的。

错法：报一个全球固定百分比；用训练 loss 当标注质量；让自动标注刷新评测集；声称「模型同意率高所以不用人」。同意率高可能是共同偏差。车上延迟不允许把人审搬到车上，见 `tesla-latency-slo`。

## 追问

- **抽查过了就能上训练集？** 还要看该层的漏检代价。行人漏检和多画一条车道，同样 2% 错误不可互换。
- **人太贵怎么降？** 先提高自动标注召回门槛、加几何规则门、把人集中在高严重度层。不是把比例从 5% 改成 1% 完事。
- **双模型一致能否替代人？** 能当触发和预过滤，不能当金标。相关误差会一起错。金标仍要独立协议。
- **和 Hydra 多头的关系？** 某个头的自动标脏了，共享骨干会把脏梯度传给别的头。质量门是按任务的，见 `tesla-hydra-nets`。
