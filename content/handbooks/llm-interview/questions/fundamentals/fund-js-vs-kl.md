---
id: fund-js-vs-kl
section: fundamentals
order: 143
level: A
title: JS 散度和 KL 散度差在哪？为什么 GAN 早期爱提 JS？
quick: >-
  JS 是对称的：$\mathrm{JS}(p,q)=\frac12 D_{\mathrm{KL}}(p\|m)+\frac12 D_{\mathrm{KL}}(q\|m)$，$m=(p+q)/2$。KL
  不对称、一端为 0 时可以无穷。JS 有上界 $\log 2$，两分布支撑不交时梯度仍可能消失，这是早期 GAN 的经典故事，不是对齐默认目标。
tags:
  - KL
  - JS
  - Probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Jensen–Shannon divergence
    url: https://en.wikipedia.org/wiki/Jensen%E2%80%93Shannon_divergence
    type: primary
  - title: 【三年面试五年模拟】算法工程师的独孤九剑秘籍（第八式）
    url: https://www.nowcoder.com/discuss/390966229664628736
    type: secondary
---

这块容易直接答成 JS 是「更好的 KL」，或者说「LLM 对齐应该用 JS」。KL 度量「用 $q$ 编码 $p$ 多付的码长」，$D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)$，所以不是距离。方向性见 `fund-kl-directions`、`pdd-forward-reverse-kl`；非负性见 `fund-kl-nonneg`。SFT 正向 KL、RLHF 反向 KL 见 `pt-sft-fwd-kl-vs-rlhf-rev-kl`。我会先写 KL 定义，再写混合分布 $m$，最后说：对齐先问方向，不先问对称。

## 定义与有界性

$$
m=\frac{p+q}{2},\qquad
\mathrm{JS}(p,q)=\frac12 D_{\mathrm{KL}}(p\|m)+\frac12 D_{\mathrm{KL}}(q\|m).
$$

因为 $m$ 在 $p$ 或 $q$ 有质量的地方都大于 $0$，两项 KL 都有限。对称性显然。用 $\log 2$ 为底时 $\mathrm{JS}\in[0,\log 2]$。用熵写：

$$
\mathrm{JS}(p,q)=H(m)-\frac12 H(p)-\frac12 H(q),
$$

即「混合之后多出来的不确定性」。KL 在 $q(x)=0$ 且 $p(x)\gt 0$ 时可以是 $+\infty$；JS 没有这个问题，但饱和后梯度照样可以消失。

## 为什么 GAN 早期提它

原始 GAN（Goodfellow et al., 2014）在判别器最优时，生成器目标等价于最小化 $p_{\mathrm{data}}$ 与 $p_g$ 的 JS。两个分布支撑几乎不交时（高维图很常见），JS 已经饱和在上界附近，梯度消失，生成器学不动。后来才有 WGAN 等用别的 divergence / IPM。这是生成模型史，**不是**「LLM 对齐应该用 JS」。

## 接到后训练

默认仍用 KL：SFT 正向（mode-covering，易糊）、RLHF / DPO 反向（mode-seeking，易尖）。CE 与 KL 的关系见 `fund-ce-kl`。GKD / 部分蒸馏会拿 JS 当折中，避免纯正向太糊、纯反向太尖，那是蒸馏损失设计，不是 PPO 默认项。若被问「为什么不用对称散度约束策略」，答：要对齐的是相对参考策略的方向性约束，对称会把「不许偏离」和「必须覆盖」混在一个数里。

失败模式：把 JS 有上界说成「一定更好优化」；把 GAN 的 JS 梯度消失直接套到 token 级 RL，而不提支撑不交这一前提。

## 方向性才是后训练要的性质

SFT 最小化的是正向 KL / CE：$\mathbb{E}_{p_{\mathrm{data}}}[\log\pi]$，模式覆盖，容易把多峰数据抹成平均答案。RLHF 常用反向 KL 把 $\pi$ 拉向高奖励且靠近 $\pi_{\mathrm{ref}}$ 的峰，模式寻求，容易尖。JS 把两个方向各接一半到 $m$ 上，对称、有界，于是既不特别覆盖也不特别寻求。蒸馏里有人用 JS 当折中（避免 student 过于 smear 或过于 collapse），那是 **拟合 teacher 分布** 的损失设计，不是 PPO 的约束项。对齐若被追问「为什么不用对称散度」，答：要对齐的是相对参考策略的单向惩罚，对称会把「不许偏离」和「必须覆盖」混在一个标量里，调 $\beta$ 时不知道在压哪一侧。

GAN 故事的要点是支撑不交导致 JS 饱和、梯度消失，所以后来才有 Wasserstein 等。LLM token 分布在词表上几乎处处有质量，支撑不交不是主矛盾；主矛盾是正向 / 反向 KL 的覆盖 vs 寻求。不要把 2014 生成模型的药方直接开给 2025 的 GRPO。

白板顺序：KL 定义与非负性 → $D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)$ → 写出 $m$ 与 JS → 上界 $\log 2$ → 「对齐先问方向」。

## 追问

- **JS 是不是距离？** 开方后的 $\sqrt{\mathrm{JS}}$ 才满足三角不等式；面试说「对称、有界」即可，不必强称 metric。
- **支撑不交时 KL 呢？** 正向/反向至少一侧可爆到无穷；JS 有限但饱和，两者都可能学不动。
- **对齐为什么仍用 KL？** 要的是相对 $\pi_{\mathrm{ref}}$ 的单向惩罚，和变分/最大似然同一套工具，不是缺对称性。
- **JS 有上界是不是更容易训？** 有界不代表梯度好。饱和在上界附近时梯度照样没了，这正是早期 GAN 的问题。
- **GKD 用 JS 和 RLHF 用 KL 冲突吗？** 不冲突。一个在蒸馏拟合 teacher，一个在约束相对 ref 的偏移，目标和数据都不同。
