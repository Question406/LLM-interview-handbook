---
id: sys-specdecode
section: systems
order: 11
level: S
title: Speculative Decoding 为什么能保持 Target Distribution？
quick: >-
  Draft model 先提出多个 token，target model 一次前向并行验证，再用接受概率和残差 sampling 校正，使最终分布保持为
  target policy。一次 target forward 能接受多个 token，因此可以提速；收益还要扣掉 draft 的计算成本。
tags:
  - Speculative Decoding
  - Inference
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: 'https://arxiv.org/abs/2211.17192'
    type: primary
---

speculative decoding 靠接受概率和残差 sampling 校正 draft 的提议，最终保持 target 分布 $p$。Draft 先便宜地提出多个 token，target 用一次前向并行验证；只按「大模型同意就收下」处理，带温度 sampling 时分布会变。可以先看 greedy 前缀对齐，再用两词 vocabulary 的例子理解 sampling 校正。

Draft 提出 $\tilde{x}_1,\ldots,\tilde{x}_k$。Target 在这些位置上做一次 teacher-forcing 前向，同时得到各步 logits。从左到右比较：与 target 的 greedy 选择一致则接受，第一处分歧改写为 target 自己的 token，其后作废。分布退化成 $\delta_{x^*}$，谈不上「保持 $p$」，但能说明一次 target 调用换多个 token。

## 接受概率和残差怎样保持分布

设 draft 为 $q(\cdot\mid x_{<t})$，target 为 $p(\cdot\mid x_{<t})$，draft 抽到 $\tilde{x}$。接受概率

$$
\alpha(\tilde{x})=\min\Big(1,\ \frac{p(\tilde{x})}{q(\tilde{x})}\Big).
$$

若拒绝，从残差分布再抽一个：

$$
p_{\mathrm{res}}(x)\;\propto\;\max\big(0,\ p(x)-q(x)\big).
$$

这是标准 rejection sampling 校正：当 $q$ 在 $\tilde{x}$ 上高于 $p$ 时，只按比例收下，多出来的质量丢给残差，补 $p$ 有而 $q$ 不够的 token。对任意 $q$，只要能点算 $p,q$，输出边缘就是 $p$。与 $q$ 是否「像」$p$ 无关。不像只降低 $\mathbb{E}[\alpha]$，不破坏正确性。

多步时对 draft 前缀逐个验证：连续接受直到第一次拒绝，再在该位置用 $p_{\mathrm{res}}$（或直接用 target sampling，视实现）写出一个保证服从 $p$ 的 token，然后结束本轮 speculative。下轮以新前缀重新 draft。

两词 vocabulary 例子：$q=(0.8,0.2)$，$p=(0.5,0.5)$，draft 抽到词 $1$。$\alpha=0.5/0.8=0.625$；若拒，残差 $\propto(0,0.3)$，只能出词 $2$。长期频率仍是 $p$，不会变成「只收 $q$ 的众数」。

## 速度取决于接受率和 draft 成本

Target 是大模型，逐 token 生成（decode） 偏读权重。一次验证前向摊到 $k$ 个位置，等于用较大的「有效 batch」提高算术强度。加速比大约

$$
\frac{\text{每轮接受的 token 数}}{1 + c_{\mathrm{draft}}/c_{\mathrm{target}}}.
$$

Draft 越强，$\alpha$ 越高，但 $c_{\mathrm{draft}}$ 也越高。一个接近 target 的 draft 会把节省吃光。$k$ 太大则尾部更容易被拒，浪费验证算力。

EAGLE / MTP 把 draft head 或下一 token 特征预测做进同一套权重，少一份独立小模型，但要额外训练，acceptance 变成新的指标。Medusa 等多头也是同一思想：用便宜提议换一次大模型带宽。

## 追问

**为什么很强的 draft 不一定最快？**
Acceptance 高，但自身 FLOPs / 带宽接近 target，净加速接近 $1$。通常要明显更小或共享主干。
**为什么 target 能并行验证未来多个 token？**
给定 draft 前缀，autoregressive 条件概率 $p(x_t\mid x_{<t})$ 在这些 $t$ 上可一次算完，等价于 teacher forcing，不是「模型真的一次 sampling 了未来」。
**和普通 rejection sampling 差在哪？**
提议来自便宜 autoregressive $q$，验证用一次并行 target 前向；正确性仍来自 $\min(1,p/q)$ 加残差，不是来自启发式「看起来差不多就收」。
