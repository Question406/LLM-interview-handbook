---
id: meituan-lora-not-after-ln
section: arch
order: 120
level: A
title: 美团 26 校招：LoRA 能否插在 LayerNorm 之后？对稳定性有何影响？
quick: >-
  实际上 LoRA 挂在 Linear 权重上。在 Norm 输出后面随手加一个可训练的残差，会破坏已经 calibration
  好的激活尺度，训练初期容易梯度爆炸或发散。合并 adapter 时也要检查 $\alpha/r$、是否重复 merge 和 dtype。
tags:
  - Meituan
  - LoRA
  - 2026 Campus
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 26校招-美团大模型应用算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/ae849dc9cdc9463782b266b2ca616ac7'
    type: candidate-first-hand
  - title: LoRA
    url: 'https://arxiv.org/abs/2106.09685'
    type: primary-paper
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型应用算法
- 届别 / 流程：26 校招；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位与轮次明确）
- 原始措辞：**“LoRA 是不是只能在 Linear 层插？为什么不能插在 LayerNorm 之后？这会对训练稳定性造成什么影响”**；另问 rank 选择与合并时梯度爆炸

LoRA 实际挂在权重矩阵上：Attention / FFN（含 SwiGLU 的 $W_1,W_2,W_3$）的投影、输出和 embedding 都是常见位置。「不能插在 LN 后」算不上数学禁令，但这么做会改掉 Norm 刚 calibration 好的激活尺度，训练初期容易梯度爆炸、loss 突然升高，也没法干净地合并回 $W$，所以生产上几乎没人这么做。标准 LoRA 改的是线性层

$$
W'=W+\frac{\alpha}{r}BA,
$$

Norm 继续负责稳住激活尺度。LayerNorm / RMSNorm 本身几乎没有值得做低秩近似的大矩阵，也不是残差分支假设里那个可训练的乘法器。

## 为什么在 Norm 输出上加东西会影响稳定性

RMSNorm / LN 之后的激活已经被 calibration 到一个稳定的尺度，后面的 $W$ 就是按这个尺度学出来的。在 Norm 输出上再挂一个不受约束的可训练变换，激活分布就变了：学习率稍大一点，就容易在初期梯度爆炸、loss 突然升高，或者和残差分支的尺度假设冲突。RoPE 加在 $q,k$ 上，也不该被一个额外的 LN 后 adapter 把相对旋转 $q^\top R_{n-m}k$ 拧掉。稳定性差，又不好合并，这就是生产上几乎不这么做的原因。

rank 一般从 $8/16$ 扫起，看 overfitting 和下游增益，越大不一定越好。合并后爆炸时，依次查 $\alpha/r$、是否重复 merge、dtype，以及是不是在错误的模块上挂了过大的学习率。初始化仍要保证起步时 $\Delta W=0$，见 `kuaishou-lora-ab-init`。

## 和 QLoRA 的关系

如果被追问 QLoRA：它用 NF4 存冻结的基座，再挂低秩适配，激活仍保持较高精度，以此降低显存。「挂在 Linear 上」这条照样成立；量化的是 $W$ 的存储，并没有允许你在 LN 后加一层。MoE 专家也可以挂 LoRA，只是冷门专家更新少，别误判成「插错了位置」。

## 追问

**Adapter 插在 FFN 后面，算不算「LN 后」？**
要看计算图。挂在 Linear 权重上的可以合并；挂在 Norm 输出上的自由仿射，通常没法干净地 merge 回 $W$。

**Pre-Norm 和 Post-Norm 的结论一样吗？**
一样。LoRA 的目标是用低秩改 $W$，Norm 的 $\gamma$ 不在它的范围里。

**合并后数值对不齐怎么办？**
先拿同一个输入比较合并和不合并的 logits，再查 $\alpha$ 是不是被乘了两次。
