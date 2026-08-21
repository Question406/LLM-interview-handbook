---
id: sys-specdecode
section: systems
order: 11
level: S
title: Speculative Decoding 为什么能保持 Target Distribution？
quick: >-
  Draft model 便宜提出多个 tokens，target model 并行验证，并通过 acceptance/rejection
  correction 使最终采样分布等价于 target policy；速度来自一次 target forward 接受多个 token。
tags:
  - Speculative Decoding
  - Inference
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
---

陷阱是把投机解码讲成「小模型先写、大模型同意就收下」。Greedy 可以对齐前缀，**带温度的采样不能这样**：若只在 $q$ 与 $p$ 相等时接受，输出分布既不是 $p$ 也不是 $q$。正确做法是对 draft 提议做一次带残差的拒绝采样，使接受后的 token **精确服从 target** $p$。

## 1. Greedy：先建立直觉

Draft 提出 $\tilde{x}_1,\ldots,\tilde{x}_k$。Target 在这些位置上做一次 teacher-forcing 前向，同时得到各步 logits。从左到右比较：与 target 的 greedy 选择一致则接受，第一处分歧改写为 target 自己的 token，其后作废。分布退化成 $\delta_{x^*}$，谈不上「保持 $p$」，但实现简单，能说明**一次 target 调用换多个 token**。

## 2. Sampling：接受率与残差

设 draft 为 $q(\cdot\mid x_{<t})$，target 为 $p(\cdot\mid x_{<t})$，draft 抽到 $\tilde{x}$。接受概率

$$
\alpha(\tilde{x})=\min\Big(1,\ \frac{p(\tilde{x})}{q(\tilde{x})}\Big).
$$

若拒绝，从残差分布再抽一个：

$$
p_{\mathrm{res}}(x)\;\propto\;\max\big(0,\ p(x)-q(x)\big).
$$

这是标准 rejection sampling 校正：当 $q$ 在 $\tilde{x}$ 上高于 $p$ 时，只按比例收下，多出来的质量丢给残差，补 $p$ 有而 $q$ 不够的 token。对任意 $q$，只要能点算 $p,q$，输出边缘就是 $p$。与 $q$ 是否「像」$p$ 无关——不像只降低 $\mathbb{E}[\alpha]$，不破坏正确性。

多步时对 draft 前缀逐个验证：连续接受直到第一次拒绝，再在该位置用 $p_{\mathrm{res}}$（或直接用 target 采样，视实现）写出一个保证服从 $p$ 的 token，然后结束本轮 speculative。下轮以新前缀重新 draft。

两词词表例子：$q=(0.8,0.2)$，$p=(0.5,0.5)$，draft 抽到词 $1$。$\alpha=0.5/0.8=0.625$；若拒，残差 $\propto(0,0.3)$，只能出词 $2$。长期频率仍是 $p$，不会变成「只收 $q$ 的众数」。

## 3. 速度从哪来，tradeoff 是什么

Target 是大模型，decode 偏读权重。一次验证前向摊到 $k$ 个位置，等于用较大的「有效 batch」提高算术强度。加速比大约

$$
\frac{\text{每轮接受的 token 数}}{1 + c_{\mathrm{draft}}/c_{\mathrm{target}}}.
$$

Draft 越强，$\alpha$ 越高，但 $c_{\mathrm{draft}}$ 也越高。一个接近 target 的 draft 会把节省吃光。$k$ 太大则尾部更容易被拒，浪费验证算力。

EAGLE / MTP 把 draft head 或下一 token 特征预测做进同一套权重，少一份独立小模型，但要额外训练，acceptance 变成新的指标。Medusa 等多头也是同一思想：用便宜提议换一次大模型带宽。

## 追问

- **为什么很强的 draft 不一定最快？** Acceptance 高，但自身 FLOPs / 带宽接近 target，净加速接近 $1$。通常要明显更小或共享主干。
- **为什么 target 能并行验证未来多个 token？** 给定 draft 前缀，自回归条件概率 $p(x_t\mid x_{<t})$ 在这些 $t$ 上可一次算完，等价于 teacher forcing，不是「模型真的一次采样了未来」。
- **和普通拒绝采样差在哪？** 提议来自便宜自回归 $q$，验证用一次并行 target 前向；正确性仍来自 $\min(1,p/q)$ 加残差，不是来自启发式「看起来差不多就收」。
