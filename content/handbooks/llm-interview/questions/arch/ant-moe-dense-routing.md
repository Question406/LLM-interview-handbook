---
id: ant-moe-dense-routing
section: arch
order: 140
level: A
title: 蚂蚁实习：Dense 和 MoE 有何区别，路由怎么做？
quick: >-
  Dense 每层所有参数都参与每个 token；MoE 只激活少数专家，用路由器按 token 选 top-$k$。路由常见 softmax
  门控再配负载均衡，不然专家会塌到少数热门上。
tags:
  - Ant Group
  - MoE
  - Routing
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁 实习大模型算法一面 1h
    url: https://www.nowcoder.com/feed/main/detail/46dc3bfc070a4128bb63cfc91003f509
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“分别讲一下 Dense 模型和 MoE 模型以及二者的区别”**；**“讲一下MoE的 路由机制是如何做的”**

错法：把 MoE 说成「就是更大的 Dense」，或把路由讲成随便 argmax 一个专家。Dense Transformer 的 FFN 对每个 token 用同一套权重，容量和计算一起涨。MoE 把 FFN 换成一组专家，路由器只激活 top-$k$，总参数可以很大，但每 token 激活参数接近 Dense 的一小部分。

## 路由怎么算

对 token 隐状态 $x\in\mathbb{R}^{d}$，线性投影得到专家 logits，再 softmax 成门控：

$$
g(x)=\mathrm{softmax}(xW_g),\qquad y=\sum_{i\in\mathrm{top}k(g)} g_i(x)\,E_i(x).
$$

$E_i$ 通常仍是 SwiGLU 一类 FFN：$\mathrm{SwiGLU}(u)=(\mathrm{SiLU}(uW_1)\odot uW_2)W_3$。训练还要处理 capacity factor、token drop / overflow 和专家并行的 all-to-all。推理时同一 batch 专家分布不均会造成气泡：有的卡等热点专家，有的专家空转。

位置编码（RoPE）在注意力侧，和 MoE 路由正交：$\langle R_m q, R_n k\rangle$ 只依赖相对位移 $n-m$，不参与选专家。别把「MoE 怎么外推」答成改 RoPE。

## Dense vs MoE 要对哪几轴

Dense 与 MoE 要对几轴，不能只说「MoE 更大」：激活参数（每 token 算力）、总参数（容量）、通信（all-to-all）、负载不均、训推路由是否一致。Dense 没有路由塌缩，但也没有「加专家不加倍 FLOPs」这条杠杆。蚂蚁后续面常追负载均衡损失，准备时把本卡和 `ant-moe-aux-load-balance` 连起来讲。

## 追问

- **为什么常用 $k=1$ 或 $k=2$？** $k$ 大则更接近 Dense，省算力的理由变弱；$k=1$ 最省，但路由一错就没有后备专家。
- **共享专家是什么？** 一部分专家对所有 token 常开，其余仍 top-$k$，用来兜底通用变换、减轻路由压力。
- **专家并行挂了怎么表现？** 某专家 rank 超时，整层 all-to-all 卡住，看起来像训练 hang，要和数据 loader 卡住区分。
