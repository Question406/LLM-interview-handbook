---
id: ant-moe-aux-load-balance
section: arch
order: 141
level: S
title: 蚂蚁：MoE 专家负载不均衡怎么解决，损失函数怎么改？
quick: "先看每个专家收到的 token 占比和溢出率，分清是路由塌缩还是容量设小了，再用辅助负载损失、噪声门控、容量约束或专家分组平衡流量。损失项通常同时乘上实际分配的 token 比例和平均门控概率；系数过大时，主任务效果会下降。"
tags:
  - Ant Group
  - MoE
  - Load Balancing
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型面经
    url: https://www.nowcoder.com/feed/main/detail/2b27dfe1f1ab4efa87eb0aea70ffdc20
    type: candidate-first-hand
---

我会先看监控再改损失：每层每个专家拿到的 token 份额、drop 率和容量利用率，确认是路由塌缩还是容量设得太小。改损失时用一个同时看实际分配比例和平均门控概率的辅助项，再配合容量、噪声门控一起调。

负载不均的样子是少数专家接走大部分 token，其余专家很少得到训练，专家并行的 all-to-all 通信负载也跟着不均。比如一层里某个专家吃掉了大半 token，那张卡的计算和通信就成了整层的瓶颈。面试里常见的失分是张口就背 $\lambda\mathcal{L}_{\mathrm{aux}}$，却说不清罚的是门控概率还是实际分配，也不提容量和 drop。

## 辅助损失在惩罚什么

Switch Transformer 一类的 aux loss 让 batch 内各专家的负载靠近均匀。记 $N$ 个专家，$P_i$ 为专家 $i$ 上的平均门控概率，$\bar f_i$ 为实际被分到的 token 比例，常见形式是

$$
\mathcal{L}_{\mathrm{aux}}=\alpha N\sum_{i=1}^{N}\bar f_i P_i.
$$

$\bar f$ 与 $P$ 都均匀时这项最小。也可以只罚实际频率的方差、给过热专家加 routed noise，或者改成 sequence-level / expert-choice 路由，让竞争的一方从 token 换成专家。DeepSeek-V3 把均衡挪到不进主梯度的 expert bias 上，主交叉熵损失（CE）少受「必须均匀」的干扰。面试讲清「罚的是哪一个统计量」就够了，不必编系数。

## 容量和路由要一起调

容量因子 $C$ 给出每个专家能接的 token 上限，约为 $C\cdot T\cdot k/N$。$C$ 太小，热点专家的 token 被 drop；$C$ 太大，通信和算力白白浪费。噪声门控在 logits 上加 Gumbel 或高斯噪声，训练时让低负载专家有更多机会被选中。专家分组和共享专家则把一部分容量固定下来。

只拧 $\lambda$ 容易变成「为均衡而均衡」，aux 过强时主 CE 或强化学习（RL）的指标会掉点。所以它要和 capacity、drop 策略一起调，验收时下游任务和溢出率一起看。

路由本身仍然是 $g(x)=\mathrm{softmax}(xW_g)$ 再取 top-$k$，和 Dense FFN、SwiGLU 专家的内部结构无关。均衡管的是「谁被点到」，专家内部的非线性它不碰。

## 追问

**$\alpha$ 怎么选？**
看热点专家份额和 overflow 来定。$\alpha$ 太大主任务掉点，太小塌缩还在。汇报时给监控曲线，别报一个虚构的常数。

**和 DeepSeek 的无辅助损失方案差在哪？**
Aux 把「均匀」写进了可反传的损失项；bias 方案只改 top-$k$ 的门槛，不进 gates。见 `arch-moe-noaux`。

**推理时还加 aux 吗？**
不加。推理只执行训练好的 router，训推路由不一致是另一道系统题。

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：原帖未披露；二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“MoE 模型专家的负载不均衡问题如何解决？”**；**“如何通过修改损失函数来解决负载均衡问题？”**
