---
id: arch-shared-expert
section: arch
order: 203
level: A
title: Shared expert 和 routed expert 怎么分工？什么时候必须留 shared？
quick: "Shared expert 对每个 token 都常开，承接大家都要的公共变换；routed expert 走 top-$k$，承接长尾专长。专家又多又小、$k/N$ 很小的细粒度 MoE 必须留 shared，否则公共知识要么被复制进所有专家，要么挤进少数热点。算账时总参数按全部专家计，激活 FLOPs 只算 shared $+k$ 路。"
tags:
  - MoE
  - DeepSeek
  - Shared Expert
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMoE
    url: https://arxiv.org/abs/2401.06066
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

Shared expert 对每个 token 都常开，负责公共变换；routed expert 由 router 选 top-$k$，负责领域、语种、格式这些长尾。专家切得越细、越稀疏，越离不开 shared。DeepSeekMoE / V3 就是这样把 FFN 拆成常开的共享专家和稀疏的路由专家。这里只讲分工，以及什么时候不能省掉 shared；负载怎么均衡见 `arch-moe-balance`、`arch-moe-noaux`，专家怎么切卡见 `sys-expert-parallel`。

举个例子，一个再普通不过的 token，也要经过句法、通用语义这类稠密变换。如果没有共享通道，每个 routed expert 都得先把这套公共映射各学一遍，容量就浪费了；router 也很容易把这些「普通 token」全打给同一个万金油专家，均衡更难做。

## 分工：公共通道加长尾专家

记 token 隐状态为 $x$。输出是共享支路加稀疏支路：

$$
y=\sum_{s=1}^{n_{\mathrm{s}}}E_{s}^{\mathrm{shared}}(x)+\sum_{i\in\mathrm{top}k}g_{i}\,E_{i}^{\mathrm{routed}}(x).
$$

$E^{\mathrm{shared}}$ 每个 token 都算，没有门控，也不参加 top-$k$ 竞选。只有 $E^{\mathrm{routed}}$ 由 router 打分，V3 用 sigmoid 亲和度选出 $k$ 个，门控权重用未加 bias 的分数归一化，见 `arch-moe-noaux`。直觉上，共享支路学「大家都要的」变换（句法、通用语义、残差式的稠密 FFN），路由专家学领域、语种、格式里的长尾。

DeepSeekMoE 还做了细粒度切分：把原来一个大 FFN 切成很多小专家，增加专家的组合数。切得越碎，越需要一条常开通道把公共计算拿走，不然 $k$ 路小专家拼不出稳定的稠密变换。V3 的量级是 1 个共享加 256 个路由，每个 token 再激活 8 个路由专家，所以激活的 FFN 是 $9$ 路，$257$ 个专家里只有这 9 个参与计算。

## 什么时候必须留 shared

细粒度加高稀疏时必须留。专家数 $N$ 很大、$k/N$ 很小、单个专家容量也小，公共知识要么被复制 $N$ 份，浪费参数，要么被 router 塞进少数热点，负载崩掉。共享专家把这部分从路由里隔离出去，routed 才有余地专精。DeepSeekMoE 把「细粒度切分」和「共享隔离」当成一套设计，两者是配合着用的，不能随便拆掉一个。

路由还不稳定，或者训练和推理的路由会漂的时候，shared 也是一层缓冲。推理的 top-$k$ 和训练不完全一致时，纯 routed 模型的公共能力会跟着抖；常开支路不依赖这一次选了谁。它替代不了训推对齐，但能避免「换一次路由，公共语言建模就塌了」。

也有可以不留的情况。Mixtral 一类粗粒度模型，专家大、$k$ 相对没那么极端，常见做法就是纯 routed、没有 shared。稠密 FFN 也可以看成「全都是 shared、没有 routed」。所以面试别说「MoE 必须有共享专家」，只有细粒度稀疏才几乎必须。省掉 shared 的代价是 router 要同时承担公共计算和专长，aux / bias 要用得更狠，热点也更常见。

## 参数账和 FLOP 账要分开算

常见的错是把「671B 总参数」当成每个 token 的 FLOPs。总参数里，所有 shared 和所有 routed 的 FFN 都占显存和 checkpoint；激活 FLOPs 只算 $n_{\mathrm{s}}+k$ 路，再加上注意力和路由的开销。把 256 个 routed 全乘进 $6ND$ 的 $N$，就是把稀疏模型当成稠密模型算了。反过来，只报激活参数、却拿总参数说「世界最大」，是方向相反的同一类错。

EP 的布局也不一样。routed 按专家切卡，token 要做 all-to-all；shared 每个 token 都要用，通常复制在每张卡上（或者只做 TP 切矩阵），不走 dispatch。面试时如果把 shared 也画进 EP 的 all-to-all，通信模式就画错了。通信和计算怎么重叠见 `sys-expert-parallel`。

## 追问

**shared 要不要算进 top-$k$？**
不要。它在 $k$ 之外，激活路数是 $n_{\mathrm{s}}+k$。把「激活 8 个专家」说成含 shared，和 V3 对不上。

**放多个 shared 是干什么？**
给公共部分更大的容量，一般仍远少于 routed 的总数。它们之间不再做稀疏路由。

**shared 会不会变成新的稠密瓶颈？**
会。它每个 token 都要算，逐 token 生成（decode）时带宽和 FLOPs 一直在。做得太大，就退回成稠密 FFN，稀疏的好处被吃掉了。

**和 aux loss 有什么关系？**
公共流量隔离出去之后，routed 的均衡目标更干净。没有 shared 时，aux 往往既要均衡负载、又要保住语言建模，和主损失抢参数，见 `arch-moe-balance`。

**激活 FFN 的参数怎么手算？**
$(n_{\mathrm{s}}+k)\times$（单个专家参数），这里不乘 $N$。总参数才乘 $N$。
