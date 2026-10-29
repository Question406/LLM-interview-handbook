---
id: fund-js-vs-kl
section: fundamentals
order: 143
level: A
title: JS 散度和 KL 散度差在哪？为什么 GAN 早期爱提 JS？
quick: >-
  JS 是对称的：$\mathrm{JS}(p,q)=\frac12 D_{\mathrm{KL}}(p\|m)+\frac12 D_{\mathrm{KL}}(q\|m)$，$m=(p+q)/2$，有上界 $\log 2$；KL 不对称，一端为 0 时可以到无穷。GAN 早期提 JS，是因为最优判别器下生成器目标等价于最小化 JS，两分布支撑不交时它饱和、梯度消失；后训练默认仍用 KL，因为要的是有方向的约束。
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
JS 是把两个分布都和它们的平均 $m$ 比，所以对称、有界；KL 是单向的，度量「用 $q$ 编码 $p$ 多付的码长」，$D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)$，也就不是距离。GAN 早期爱提 JS，是因为原始 GAN 的目标在判别器最优时恰好等价于 JS，这段是生成模型的历史，并不说明 JS 是「更好的 KL」，LLM 对齐也没有理由改用 JS。后训练先问方向，再谈对称。方向性见 `fund-kl-directions`、`pdd-forward-reverse-kl`，非负性见 `fund-kl-nonneg`，SFTforward KL、RLHFreverse KL 见 `pt-sft-fwd-kl-vs-rlhf-rev-kl`。

## 定义与有界性

我会先写 KL 定义，再写混合分布 $m$：

$$
m=\frac{p+q}{2},\qquad
\mathrm{JS}(p,q)=\frac12 D_{\mathrm{KL}}(p\|m)+\frac12 D_{\mathrm{KL}}(q\|m).
$$

$m$ 在 $p$ 或 $q$ 有质量的地方都大于 $0$，所以两项 KL 都有限，对称性也一眼可见。用 $\log 2$ 为底时 $\mathrm{JS}\in[0,\log 2]$。换成熵来写：

$$
\mathrm{JS}(p,q)=H(m)-\frac12 H(p)-\frac12 H(q),
$$

意思是「混合之后多出来的不确定性」。KL 在 $q(x)=0$ 且 $p(x)\gt 0$ 时可以是 $+\infty$，JS 没有这个问题，但饱和以后梯度一样会消失。

## 为什么 GAN 早期提它

原始 GAN（Goodfellow et al., 2014）在判别器最优时，生成器的目标等价于最小化 $p_{\mathrm{data}}$ 和 $p_g$ 之间的 JS。高维图像上两个分布的支撑几乎不相交很常见，这时 JS 已经饱和在上界附近，梯度消失，生成器学不动，后来才有 WGAN 等改用别的 divergence / IPM。

LLM 的情况不一样。token 分布在 vocabulary 上几乎处处有质量，支撑不交不是主要矛盾，主要矛盾是正向和 reverse KL 在覆盖和寻求之间的取舍。2014 年给生成模型开的药方，不要直接开给 2025 年的 GRPO。

## 接到后训练：要的是方向性

后训练默认仍用 KL。SFT 最小化的是 forward KL / cross entropy loss（CE），也就是 $\mathbb{E}_{p_{\mathrm{data}}}[\log\pi]$，模式覆盖（mode-covering），容易把多峰数据抹成平均答案，CE 和 KL 的关系见 `fund-ce-kl`。RLHF / DPO 用 reverse KL，把 $\pi$ 拉向高奖励且靠近 $\pi_{\mathrm{ref}}$ 的峰，模式寻求（mode-seeking），容易变尖。JS 把两个方向各接一半到 $m$ 上，对称、有界，于是既不特别覆盖也不特别寻求。

所以 GKD 和部分 distillation 会拿 JS 当折中，避免纯正向太糊、纯反向太尖，让 student model 的分布既不过于平坦也不过度集中。那是拟合教师分布的损失设计，跟 PPO 默认的约束项无关。

如果被追问「为什么不用对称散度来约束策略」，我会答：对齐要的是相对 reference policy 的单向惩罚，用对称的散度，会把「不许偏离」和「必须覆盖」混进一个标量里，调 $\beta$ 时都不知道自己在压哪一侧。

常见的失败模式有两种：把「JS 有上界」说成「一定更好优化」；把 GAN 里 JS 的梯度消失直接套到 token 级 RL 上，却不提支撑不交这个前提。

白板顺序是：KL 定义与非负性 → $D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)$ → 写出 $m$ 和 JS → 上界 $\log 2$ → 对齐先问方向。

## 追问

**JS 是距离吗？**
开方后的 $\sqrt{\mathrm{JS}}$ 才满足三角不等式。面试里说「对称、有界」就够了，不必硬说它是 metric。

**支撑不交时 KL 会怎样？**
正向、反向至少有一侧会爆到无穷；JS 有限但饱和，两者都可能学不动。

**对齐为什么还用 KL？**
要的是相对 $\pi_{\mathrm{ref}}$ 的单向惩罚，它和变分、maximum likelihood 是同一套工具，跟缺不缺对称性没关系。

**JS 有上界，是不是更容易训？**
有界不代表梯度好。饱和在上界附近时梯度照样没了，这正是早期 GAN 的问题。

**GKD 用 JS、RLHF 用 KL，冲突吗？**
不冲突。一个在 distillation 里拟合 teacher，一个在约束相对 ref 的偏移，目标和数据都不同。
