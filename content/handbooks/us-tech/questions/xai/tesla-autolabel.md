---
id: tesla-autolabel
section: xai
order: 10
level: A
title: Tesla：自动标注 data quality checks，人在环抽查比例怎么定
quick: >-
  先按错误严重度定 data quality checks，再用分层抽样和 confidence interval
  算人审条数，比例会随流量变化。安全关键层接近全审，常规几何低比例抽查并加触发式审核；Tesla 没有公布内部抽查比例，示意数不能当内部规定。
tags:
  - Tesla
  - Auto Labeling
  - Quality Gate
  - Human-in-the-loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Tesla AI Day 2021
    url: 'https://www.youtube.com/watch?v=j0z4FweCy4M'
    type: primary
  - title: Tesla AI Day 2022
    url: 'https://www.youtube.com/watch?v=ODSJsviD_SU'
    type: primary
  - title: Tesla AI
    url: 'https://www.tesla.com/AI'
    type: primary
  - title: Tesla's data engine — the road to full self-driving
    url: 'https://www.taivo.ai/tesla-data-engine/'
    type: secondary
---

人审比例要从可容忍错误率和风险算出来：先把标签协议和独立金标固定，再分层估计需要审多少条。比如同样的错误率，漏行人和多画车道的后果不同，就应采用不同的审核强度。

这是一道数据 / 标注平台的设计题。AI Day 公开介绍了向量空间自动标注，会结合多相机、时序和未来帧，让人主要改错。Tesla 未公布抽查比例，1% 或 10% 都不能当作内部数字；它在数据引擎里的位置见 `tesla-data-engine`。

确定比例前，先把质量标准固定下来：

1. 标注协议。占用、框、车道各自什么叫错。墙后行人算占用还是 unknown，必须写死，否则人和模型永远吵。Occupancy 的可见 mask 见 `tesla-occupancy-net`。
2. 冻结金标集。双人标 + 仲裁的一小撮 clip，自动标注先通过这些 quality checks：交并比（IoU，即两个区域的交集与并集之比）、漏检、假阳、时序跳动。金标不能用当前自动标注刷新。
3. 按风险分层。施工、行人、加塞、夜间、自动标注低置信、多模型互不一致，这些层的抽查密度远高于空旷高速；不要 i.i.d. 抽帧。

人主要负责审计和改错。自动标注通过 data quality checks 后可以低比例抽查；没通过的要全部修正，或不进训练集，避免把系统误差规模化。

设某层真实错误率为 $p$，要在置信度 $1-\alpha$ 下把估计误差控制在 $e$ 内。正态近似：

$$
n \approx \frac{z_{1-\alpha/2}^2\, p(1-p)}{e^2}.
$$

$p$ 未知时用 $p=0.5$ 最保守，或用金标上的试点 $\hat p$。例：某层试点 $\hat p=0.02$，想 $e=0.01$、$z=1.96$，则 $n \sim 750$ 量级。这是该层要审的条数，不是全局百分比。流量 10 万 clip 时，这一层看起来像 0.75%；流量 1000 时就是 75%。所以面试说「比例随流量和风险走」，不说「Tesla 抽 2%」。

小 $p$ 时可以用比正态近似更合适的 Wilson 区间。另外还要比较人和自动标、人和人之间的不一致率。差异高时，先检查协议与模型系统偏差，再扩大标注规模。

下面是按严重度分层的示意，不代表 Tesla 内部规定：

- 安全关键（行人、反向来车、交通灯）：自动标只做预填，人审接近全覆盖，直到金标错误率掉到协议以下。
- 几何常规（高速车道线）：低比例抽查 + 触发式全审（模型之间判断不一致、低置信）。
- 新域（新城市、新天气）：临时拉高抽查，直到 $\hat p$ 稳定再降。

时序检查可以自动做 acceptance checks：相邻帧框跳变、占用体积闪烁、多相机投影对不上。这类规则过滤不占人时，放在人审前面。人只看规则过不了或规则不确定的。

验收应使用独立金标，训练 loss 和模型之间的同意率都不能替代标签质量。两个模型可能共同犯错，因此也不能用自动标注刷新评测集。人审发生在离线链路，车上延迟不允许等待人工确认，见 `tesla-latency-slo`。

## 追问

**抽查过了就能上训练集？**
还要看该层的漏检代价。行人漏检和多画一条车道，同样 2% 错误不可互换。
**人太贵怎么降？**
先提高自动标注召回 threshold、加几何规则门、把人集中在高严重度层。不是把比例从 5% 改成 1% 完事。
**双模型一致能否替代人？**
能当触发和预过滤，不能当金标。相关误差会一起错。金标仍要独立协议。
**和 Hydra 多头的关系？**
某个头的自动标脏了，共享骨干会把脏梯度传给别的头。data quality checks 是按任务的，见 `tesla-hydra-nets`。
