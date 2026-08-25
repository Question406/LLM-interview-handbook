---
id: meituan-lora-not-after-ln
section: arch
order: 120
level: A
title: 美团 26 校招：LoRA 能否插在 LayerNorm 之后？对稳定性有何影响？
quick: >-
  实务上 LoRA 挂在 Linear 权重上；若在 Norm 后乱加可训练残差，会破坏已校准的激活尺度，容易初期梯度爆炸 /
  发散。合并 adapter 时也要检查 $\alpha/r$、是否重复 merge 与 dtype。
tags:
  - Meituan
  - LoRA
  - 2026 Campus
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 26校招-美团大模型应用算法一面
    url: https://www.nowcoder.com/feed/main/detail/ae849dc9cdc9463782b266b2ca616ac7
    type: candidate-first-hand
  - title: LoRA
    url: https://arxiv.org/abs/2106.09685
    type: primary-paper
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型应用算法
- 届别 / 流程：26 校招；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位与轮次明确）
- 原始措辞：**“LoRA 是不是只能在 Linear 层插？为什么不能插在 LayerNorm 之后？这会对训练稳定性造成什么影响”**；另问 rank 选择与合并时梯度爆炸

这块容易把「不能插在 LN 后」说成数学禁令。标准 LoRA 改的是线性层

$$
W'=W+\frac{\alpha}{r}BA,
$$

Norm 继续负责稳定激活尺度。Attention / FFN（含 SwiGLU 的 $W_1,W_2,W_3$）投影、输出和 embedding 是常见挂载点。LayerNorm / RMSNorm 本身几乎没有值得低秩近似的大矩阵，也不是残差分支假设的可训练乘法器。

## 为什么 LN 后乱挂容易炸

RMSNorm / LN 之后的激活已经被校准到稳定尺度，后面的 $W$ 是按这个尺度学的。若在 Norm 输出上再挂未约束的可训练变换，等于重写分布：学习率稍大就容易初期梯度爆炸、loss 尖刺，或与残差分支的尺度假设冲突。RoPE 加在 $q,k$ 上也不该被一个额外 LN 后 adapter 拧掉相对旋转 $q^\top R_{n-m}k$。这不是绝对禁令，而是稳定性与可合并性很差，生产上几乎不这么做。

rank 从 $8/16$ 扫起，看过拟合与下游增益，不是越大越好。合并爆炸时检查 $\alpha/r$、是否重复 merge、dtype，以及是否在错误模块上挂了过大学习率。初始化仍应保证起步 $\Delta W=0$，见 `kuaishou-lora-ab-init`。

## 和 QLoRA 的关系

若追问 QLoRA：NF4 存冻结基座 + 低秩适配，激活仍较高精度，从而降显存。它不改变「挂在 Linear 上」这条；量化的是 $W$ 的存储，不是批准你在 LN 后加一层。MoE 专家也可以挂 LoRA，但冷专家更新少，不要误判为「插错位置」。

## 追问

- **Adapter 插在 FFN 后算不算「LN 后」？** 要看计算图。挂在 Linear 权重上可以合并；挂在 Norm 输出上的自由仿射通常不能干净 merge 回 $W$。
- **Pre-Norm 和 Post-Norm 结论一样吗？** 一样：LoRA 目标是低秩改 $W$，不是改 Norm 的 $\gamma$。
- **合并后数值对不齐怎么办？** 先对同一输入比合并 / 不合并的 logits，再查 $\alpha$ 是否被应用了两次。
