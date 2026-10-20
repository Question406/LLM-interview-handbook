---
id: arch-longcontext
section: arch
order: 5
level: A
title: Position Interpolation、NTK-aware scaling、YaRN 大致在做什么？
quick: >-
  它们都在调整 RoPE 长位置的 position/frequency 映射：PI 把位置压进训练区间，NTK-aware 按频率更细地缩放，YaRN
  对不同频率与温度做更平滑的扩展。
tags:
  - Long Context
  - RoPE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Extending Context Window of Large Language Models via Positional Interpolation
    url: https://arxiv.org/abs/2306.15595
    type: primary
  - title: YaRN
    url: https://arxiv.org/abs/2309.00071
    type: primary
---

常见误区是：只把 `max_position_embeddings` 改大。RoPE 在训练时只见过 $[0,L)$ 的位置，直接把 index 接到 $t\gt L$，旋转角进入从未见过的相位，注意力分数会崩。Position Interpolation、NTK-aware scaling、YaRN 都在重新定义长位置下的频率，让外推时的旋转仍落在模型见过的动态范围附近。面试要能讲清：为什么改配置项无效，以及三种方法分别牺牲了什么。PI 把长位置压缩进训练区间，近处分辨率下降；NTK-aware 按频率区别缩放，尽量保住高频局部信息；YaRN 分段更平滑并调节注意力温度。它们改的是 RoPE 的 $t\theta_i$ 映射。长依赖任务和 KV 成本仍要单独评。

## 为什么直接外推 RoPE 会坏

RoPE 把位置 $t$ 编码成一对对频率 $\theta_i$ 上的旋转。低频分量管远距离相对位置，高频管近邻 文本处理单位（token） 的精细相位。训练长度 $L$ 内，$t\theta_i$ 有界；推理时 $t'=8L$ 会让高频转很多圈，相对位置编码跑出训练分布。于是长距离依赖先坏，严重时短距离注意力也不稳。这是位置编码的 分布外数据（OOD，即与训练数据明显不同的数据），不是窗口数字写小了。

这些长度扩展方法都在修改 $t\mapsto t\cdot\theta_i$ 这条映射，不能只改 config。是否还要少量长文本微调，决定能扩多狠；纯测试时外推更脆。RoPE 的频率是几何级数：越靠后的维度 $\theta_i$ 越小、波长越长。长上下文外推时，短波长维度先转出训练见过的圈数，所以高频更怕直接外推。低频维度还没转到训练范围之外，却会在 PI 的统一压缩里被不必要地压扁。后面两种方法都在利用这张频谱图，位置不能当成一个标量 index。把 `max_position_embeddings` 改大只增加可写的下标，频谱仍按旧 $\theta_i$ 转。

## PI：把长 index 压回训练区间

Position Interpolation 最直接：推理位置 $t$ 映射为 $t\cdot L/L'$，把 $[0,L')$ 压进 $[0,L)$。相位不再 OOD，原训练过的旋转角还能对上。代价是近距离分辨率被压缩：本来差 1 个 token 的相位差，现在只有 $L/L'$。短程模式（局部语法、括号匹配）可能变钝，需要一点微调来适应新的「每步更小的旋转」。

PI 的直觉好讲：所有频率统一按长度比缩放。它不管「高频更怕外推、低频更怕被压」，所以在很大扩展倍数上往往不够用，才有后续的按频率区别对待。微调可以部分找回近邻分辨率，因为网络能学会「现在每一步旋转更小」。纯零样本 PI 在中等倍数上常能续得动 perplexity，但长依赖任务（找远距离论据、全书问答）仍可能掉。口述不要停在「PI 就是压缩位置」：要补上牺牲了局部分辨率、以及所有 $\theta_i$ 同一比例，才能接到 NTK-aware。

## NTK-aware 与 YaRN：不要所有频率一视同仁

NTK-aware scaling 的观察是：网络对高频更敏感于外推失真，对低频更敏感于被插值压缩。于是不按统一比例缩放所有 $\theta_i$，而是让高频少改（保住邻域分辨率）、低频多改（把超长距离仍然编进可表示的相位）。它比 PI 更细，但仍是一条全局规则，极端倍数上会在某些频段留下突变。

YaRN 进一步按频率分段：一部分维度接近 PI，一部分接近 NTK-aware，中间插值，并引入 attention temperature，缓解扩展后注意力过尖或过平。目标是在「近处仍然分得清、远处仍然有相对位置」之间做更平滑的折中，并用比全量长上下文预训练少得多的 token 做适配。细节公式以论文为准，现场能画出「低频 / 高频不同策略 + 可能的温度」就够。

三者都不是免费的无限窗口：KV cache、延迟、以及「中间位置利用率差」仍然在。长度扩展解决的是位置编码 OOD，不自动解决 Lost-in-the-Middle。评测应看真实长依赖任务，不能只看 perplexity 能否接着往下算。YaRN 论文把 PI 和 NTK-aware 放在同一框架里比较，现场可以记成「PI 一刀切、NTK 按频、YaRN 分段再加温度」，不必背具体超参表。若已经用了 ALiBi 等非 RoPE 方案，这三套招不适用。RoPE 模型上，要讲清频率映射怎么改，以及近处 / 远处各自牺牲了什么。

## 追问

- **只改 `max_position_embeddings` 为什么不行？** 那只放大可索引范围，不改变 RoPE 频率，长位置的相位仍是训练时没见过的。必须改 $t\theta_i$ 映射。改配置不等于做了长度扩展。
- **PI 牺牲了什么？** 把长 index 压回去，近距离相位差变小，局部分辨率下降。所有频率同一比例，大倍数上通常不够。
- **NTK-aware 相对 PI 改了什么？** 按频率区别缩放，尽量保住高频局部信息，把扩展主要交给低频。它仍是一条全局规则，极端倍数上可能有频段突变。
- **YaRN 还多了什么？** 分段 / 插值更平滑，并考虑 attention 温度；常用少量长数据适配。它仍是改 RoPE 映射，不是换一套注意力算法。ALiBi 等非 RoPE 方案不走这三招。位置编码 OOD 和窗口数字是两件事：先讲为什么改配置不够，再比较三种频率策略。
