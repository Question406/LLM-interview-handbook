---
id: arch-longcontext
section: arch
order: 5
level: A
title: Position Interpolation、NTK-aware scaling、YaRN 大致在做什么？
quick: >-
  三者都在改 RoPE 的 $t\theta_i$ 映射，让长位置的旋转落回模型见过的范围：PI
  把所有位置按同一比例压进训练区间，近处分辨率下降；NTK-aware 按频率区别缩放，尽量保住高频；YaRN 分段更平滑地插值并调 attention
  温度。只把 max_position_embeddings 改大不起作用。
tags:
  - Long Context
  - RoPE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: >-
      Extending Context Window of Large Language Models via Positional
      Interpolation
    url: 'https://arxiv.org/abs/2306.15595'
    type: primary
  - title: YaRN
    url: 'https://arxiv.org/abs/2309.00071'
    type: primary
---

这三种方法都在重新定义 RoPE 长位置下的频率，让外推时的旋转仍然落在模型见过的范围附近。PI 把长位置统一压缩进训练区间，代价是近处分辨率下降；NTK-aware 按频率区别缩放，尽量保住高频的局部信息；YaRN 按频率分段、插值更平滑，还调节 attention 温度。它们改的都是 $t\theta_i$ 这条映射，长依赖任务和 KV 成本仍要单独评。

面试里我会先讲为什么只把 `max_position_embeddings` 改大没用，再比较三种频率策略各牺牲了什么。

## 为什么直接外推 RoPE 会坏

RoPE 把位置 $t$ 编码成一组频率 $\theta_i$ 上的旋转。频率是几何级数，越靠后的维度 $\theta_i$ 越小、波长越长：低频分量管远距离的相对位置，高频分量管近邻 token 的精细相位。训练长度 $L$ 以内，$t\theta_i$ 有界；推理到 $t'=8L$ 时，高频维度会多转很多圈，相对位置编码跑出训练分布。于是长距离依赖先坏，严重时短距离 attention 也不稳。

这是位置编码的 out-of-distribution 数据（OOD，即与训练数据明显不同的数据）问题，窗口数字写小了并不是原因。把 `max_position_embeddings` 改大，只是多了可写的下标，频谱还按旧的 $\theta_i$ 转。长上下文外推时，短波长的维度先转出训练见过的圈数，所以高频最怕直接外推；低频维度还没转出范围，在统一压缩里却会被不必要地压扁。后面两种方法都在利用这张频谱图，位置不能当成一个标量 index 处理。扩完之后还要不要少量长文本微调，决定了能扩多狠，纯测试时外推更脆。

## PI：把长 index 压回训练区间

Position Interpolation 最直接：推理位置 $t$ 映射成 $t\cdot L/L'$，把 $[0,L')$ 压进 $[0,L)$。相位不再 OOD，训练过的旋转角还能对上。代价是近距离分辨率被压缩，本来相差 1 个 token 的相位差，现在只剩 $L/L'$，局部语法、括号匹配这类短程模式可能变钝，需要一点微调来适应「每一步旋转更小」。微调能部分找回近邻分辨率。纯零样本 PI 在中等倍数上常能续得动 perplexity，但找远距离论据、全书问答这类长依赖任务仍可能掉。

PI 对所有频率一刀切，没区分「高频怕外推、低频怕被压」，所以扩展倍数很大时往往不够用，这才有了按频率区别对待的方法。讲 PI 时要把这两点说出来：牺牲了局部分辨率，所有 $\theta_i$ 用同一比例，后面才好接 NTK-aware。

## NTK-aware 与 YaRN：按频率区别对待

NTK-aware scaling 的观察是：高频对外推失真更敏感，低频对插值压缩更敏感。所以它让高频少改，保住邻域分辨率；低频多改，把超长距离仍编进可表示的相位。它比 PI 更细，但仍是一条全局规则，极端倍数下某些频段会出现突变。

YaRN 再进一步按频率分段：一部分维度接近 PI，一部分接近 NTK-aware，中间插值，并引入 attention temperature，缓解扩展后 attention 过尖或过平。目标是在「近处仍分得清、远处仍有相对位置」之间做更平滑的折中，用的 token 比全量长上下文预训练少得多。YaRN 论文把 PI 和 NTK-aware 放进同一框架比较，现场可以记成「PI 一刀切、NTK 按频、YaRN 分段再加温度」，画出低频 / 高频不 on-policy 再加温度就够，具体公式和超参以论文为准。

三种方法都给不了免费的无限窗口，KV cache、延迟、中间位置利用率差这些问题还在。长度扩展解决的是位置编码 OOD，不会自动解决 Lost-in-the-Middle。评测要看真实的长依赖任务，光看 perplexity 能不能接着往下算不够。用 ALiBi 这类非 RoPE 方案的模型，这三套方法都不适用。

## 追问

**只改 `max_position_embeddings` 为什么不行？**
它只放大了可索引范围，RoPE 频率没变，长位置的相位仍是训练时没见过的。要改的是 $t\theta_i$ 映射。

**PI 牺牲了什么？**
近距离的相位差变小，局部分辨率下降。而且所有频率同一比例，大倍数上通常不够。

**NTK-aware 相对 PI 改了什么？**
按频率区别缩放，尽量保住高频局部信息，把扩展主要交给低频。它仍是一条全局规则，极端倍数上可能有频段突变。

**YaRN 还多了什么？**
分段插值更平滑，并考虑 attention 温度，通常配少量长数据做适配。它改的仍是 RoPE 映射，attention 算法本身没换。
