---
id: arch-shared-expert
section: arch
order: 203
level: A
title: Shared expert 和 routed expert 怎么分工？什么时候必须留 shared？
quick: >-
  Shared 对每个 token 常开，承接公共变换；routed 走 top-$k$，承接长尾专长。细粒度 MoE（专家又多又小、$k/N$
  很小）必须留 shared，否则公共知识被复制进所有专家或挤进少数热点。总参数按全部专家计，激活 FLOPs 只计
  shared $+k$ 路。
tags:
  - MoE
  - DeepSeek
  - Shared Expert
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: DeepSeekMoE
    url: https://arxiv.org/abs/2401.06066
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

陷阱是把「671B 总参数」当成每 token FLOPs，或把 shared 说成又一个 routed expert。DeepSeekMoE / V3 把 FFN 拆成 **常开的共享专家** 和 **稀疏的路由专家**。负载怎么均见 `arch-moe-balance`、`arch-moe-noaux`；专家怎么切卡见 `sys-expert-parallel`。本题只问分工和「什么时候不能省掉 shared」。

## 分工：公共通道 vs 长尾专家

记 token 隐状态 $x$。输出是共享支路加稀疏支路，而不是「所有专家平等竞选」：

$$
y=\sum_{s=1}^{n_{\mathrm{s}}}E_{s}^{\mathrm{shared}}(x)+\sum_{i\in\mathrm{top}k}g_{i}\,E_{i}^{\mathrm{routed}}(x).
$$

$E^{\mathrm{shared}}$ **每个 token 都算**，没有门控、不进 top-$k$。$E^{\mathrm{routed}}$ 才由 router 打分，V3 用 sigmoid 亲和再选 $k$ 个，门控权重用未加 bias 的分数归一，见 `arch-moe-noaux`。直觉：共享支路学「大家都要的」变换（句法、通用语义、残差式的稠密 FFN）；路由专家学领域、语种、格式里的长尾。没有共享通道时，每个 routed expert 都得先学会同一套公共映射，容量浪费，router 也更容易把「普通 token」全打到同一个万金油专家上，均衡更难。

DeepSeekMoE 还有细粒度切分：把原来一个大 FFN 切成很多小专家，提高专家组合数。切得越碎，越需要一条常开通道把公共计算拿走，否则 $k$ 路小专家拼不出稳定的稠密变换。V3 量级是 **1 个共享 + 256 个路由，每 token 再激活 8 个路由**：激活 FFN 是 $9$ 路，不是 $257$ 路。

## 什么时候必须留 shared

**细粒度 + 高稀疏时必须留。** 专家个数 $N$ 很大、$k/N$ 很小、单个专家容量也小：公共知识要么被复制 $N$ 份（参数浪费），要么被 router 塞进少数热点（负载崩）。共享专家把这部分从路由里隔离出去，routed 才有余地专精。DeepSeekMoE 把「细粒度切分」和「共享隔离」写成一套，不是两个可随便拆掉的开关。

**路由还不稳定、或训推路由会漂时，shared 是缓冲。** 推理 top-$k$ 和训练不完全一致时，纯 routed 的公共能力会抖；常开支路不依赖这次选了谁。它替代不了训推对齐，但能避免「换一次路由公共语言建模就塌」。

**可以不留的情况。** Mixtral 一类粗粒度、专家大、$k$ 相对不那么极端时，常见做法是纯 routed、没有 shared。稠密 FFN 等价于「全部都是 shared、没有 routed」。面试不要说「MoE 必须有共享专家」——要说 **细粒度稀疏才几乎必须**。省掉 shared 的代价是：router 同时承担公共与专长，aux / bias 要更用力，热点更常见。

## 参数账和 FLOP 账必须拆开

总参数：所有 shared + 所有 routed 的 FFN 都占显存和 checkpoint。激活 FLOPs：只计 $n_{\mathrm{s}}+k$ 路，再加注意力与路由开销。把 256 个 routed 全乘进 $6ND$ 的 $N$，是把稀疏模型当成稠密算。反过来，只报激活参数却用总参数报「世界最大」，是同一类错，方向相反。

EP 布局也不同：routed 按专家切卡，token 要 all-to-all；shared 每 token 都要，通常 **复制在每张卡上**（或只做 TP 切矩阵），不走 dispatch。面试若把 shared 也画进 EP all-to-all，通信模式就错了。通信与计算怎么叠见 `sys-expert-parallel`。

口诀：shared 买的是 **与路由无关的稠密底**；routed 买的是 **可扩展的专长容量**。细粒度不留 shared，专长还没长出来，公共能力已经在抢热点。

## 追问

- **shared 要不要进 top-$k$ 计数？** 不要。它在 $k$ 之外，激活路数是 $n_{\mathrm{s}}+k$。把「激活 8 专家」说成含 shared，和 V3 对不上。
- **多条 shared 干什么？** 容量更大的公共底；一般仍远小于 routed 总数。不是再做一次稀疏路由。
- **shared 会不会变成新的稠密瓶颈？** 会。它每 token 都算，decode 时带宽和 FLOPs 都在。过大就退回稠密 FFN，稀疏的好处被吃掉。
- **和 aux loss 的关系？** 隔离公共流量后，routed 的均衡目标更干净。没有 shared 时 aux 往往既要均负载又要保住语言建模，和主损失抢参数，见 `arch-moe-balance`。
- **手算激活 FFN 参数？** $(n_{\mathrm{s}}+k)\times$（单个专家参数），不要乘 $N$。总参数才乘 $N$。
