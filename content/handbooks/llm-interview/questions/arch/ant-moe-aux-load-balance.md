---
id: ant-moe-aux-load-balance
section: arch
order: 141
level: S
title: 蚂蚁：MoE 专家负载不均衡怎么解决，损失函数怎么改？
quick: >-
  我会先看每专家的 token 占比和溢出率，再用辅助负载损失、噪声门控、容量约束或专家分组把流量拉开。损失项一般罚的是门控概率和实际分配两边的不均；系数拧太大，主任务会跟着掉。
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

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：原帖未披露；二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“MoE 模型专家的负载不均衡问题如何解决？”**；**“如何通过修改损失函数来解决负载均衡问题？”**

错法：一张口就背 $\lambda\mathcal{L}_{\mathrm{aux}}$，却说不清罚的是门控概率还是实际分配，也不提容量和 drop。负载不均看起来就是少数专家吃掉大部分 token，其余专家饿死，all-to-all 也跟着歪。我会先看每层每专家的 token 份额、drop 率和容量利用率，确认是路由塌缩还是容量设太小，再改损失。

## 辅助损失在惩罚什么

Switch Transformer 一类 aux loss 让 batch 内各专家的平均门控概率靠近均匀。记 $N$ 个专家，$P_i$ 为专家 $i$ 上的平均门控概率，$\bar f_i$ 为实际被分到的 token 比例，常见形式

$$
\mathcal{L}_{\mathrm{aux}}=\alpha N\sum_{i=1}^{N}\bar f_i P_i.
$$

$\bar f$ 与 $P$ 都均匀时这项最小。也可以只罚实际频率的方差、对过热专家加 routed noise，或改成 sequence-level / expert-choice 路由，让竞争轴从 token 换成专家。DeepSeek-V3 把均衡挪到不进主梯度的 expert bias，主 CE 少被「必须均匀」污染；面试讲清「罚的是哪一个统计量」就够，不必编造系数。

## 工程旋钮，不能只改 $\lambda$

容量因子 $C$ 给出每专家可接 token 上限 $\approx C\cdot T\cdot k/N$。$C$ 太小热点被 drop，$C$ 太大通信和算力浪费。噪声门控在 logits 上加 Gumbel / 高斯，训练期去探冷专家。专家分组、共享专家则把一部分容量固定下来。aux 过强会变成「为均衡而均衡」，主 CE / RL 掉点；应和 capacity、drop 策略一起调，并以下游任务和溢出率一起验收。

路由本身仍是 $g(x)=\mathrm{softmax}(xW_g)$ 再 top-$k$，和 Dense FFN、SwiGLU 专家内部结构正交。均衡解决的是「谁被点到」，不是专家内部非线性。

## 追问

- **$\alpha$ 怎么选？** 先看热点专家份额和 overflow；$\alpha$ 太大主任务掉点，太小塌缩还在。报监控曲线，不要报一个虚构常数。
- **和 DeepSeek 无辅助损失差在哪？** Aux 把均匀写进可反传项；bias 只改 top-$k$ 门槛、不进 gates。见 `arch-moe-noaux`。
- **推理还加 aux 吗？** 不加。推理只执行训练好的 router；训推路由不一致是另一道系统题。
