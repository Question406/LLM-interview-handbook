---
id: baidu-grpo-loss-agg
section: posttrain
order: 228
level: A
title: 百度后训练一面：GRPO 序列级损失怎么落到每个 token？按序列平均还是按 batch 平均？
quick: "先把序列优势 $\\hat A_i$ 广播到这条回复的每个 response token，再选 reduction：`seq-mean-token-mean` 每条回复等权，接近论文 GRPO；`token-mean` 每个有效 token 等权，是 veRL 默认，长 CoT 上通常更稳。没有绝对对错，要声明你用的长度权重。"
tags:
  - Baidu
  - GRPO
  - VeRL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度 大模型后训练 一面
    url: https://www.nowcoder.com/discuss/863890669662674944
    type: candidate-first-hand
  - title: 群体相对策略优化 (GRPO) — verl 文档
    url: https://verl.readthedocs.io/en/latest/algo/grpo.html
    type: primary
---

## 真题记录

- 公司：百度 · 文心
- 岗位：大模型 强化学习（RL） 后训练；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“GRPO的损失计算，在序列级别的损失上，损失如何给到每一个token上？序列级别平均 或 批次级别平均”**

同一条回复的组相对优势 $\hat A_i$ 会原样广播到这条回复的每个 response token 上，变成 token 级损失；按序列平均还是按 batch 平均，是广播之后的 reduction 选择，它决定谁主导梯度。论文原版 GRPO 更接近按序列平均，veRL 默认按 token 平均。

这题容易把「优势怎么来」和「损失怎么加」拧成一个旋钮。优势那一步要求组大小 $n\gt 1$，见 `sys-rl-group-n`；这题问的是广播之后求和符号写在哪。所以我先写 token 级的 $\ell_{i,t}$，再写三种平均，最后报自己配的 `loss_agg_mode`。只说「按序列平均」或「按 batch 平均」不写分母，两种模式听起来像同一句话。

令 $\ell_{i,t}$ 为 token 级的 surrogate，例如 $-\min(\rho_{i,t}\hat A_i,\mathrm{clip}(\rho_{i,t})\,\hat A_i)$。veRL 文档里常见三种：

$$
\begin{aligned}
\text{seq-mean-token-mean}&=\frac1B\sum_i\frac1{|y_i|}\sum_t\ell_{i,t},\\
\text{seq-mean-token-sum}&=\frac1B\sum_i\sum_t\ell_{i,t},\\
\text{token-mean}&=\frac{\sum_{i,t}\ell_{i,t}}{\sum_i|y_i|}.
\end{aligned}
$$

差别在长度权重。设想一个 batch 里有一条短回复和一条很长的推理链。seq-mean-token-mean 每条回复权重相同，长回复里的单个 token 权重就更小，短回复相对更响。seq-mean-token-sum 每条先对 token 求和再平均，长回复权重更大，长度 hack 会被放大。token-mean 让 batch 里每个有效 token 等权。veRL 示例默认 token-mean，文档里也写明论文原版 GRPO 更接近 seq-mean-token-mean。长思维链（CoT）上 token-mean 通常更稳，一条长推理链的每个 token 不会被稀释掉，DAPO 的 token-level PG 也在推这个方向。没有绝对正确的选法，要声明你用的长度权重。

还有几个旋钮别混进来。KL 按 token 还是按序列，是正则项的 reduction，和 policy gradient 的 reduction 是两码事。GSPO 把 likelihood ratio 提到序列级，改的是 clip 的粒度；CISPO 仍是 token 级损失，但 clip 的是 detach 后的 IS 权重，梯度始终走 $\log\pi$，见 `pt-cispo`。要拆成三件事讲：优势怎么来（组相对）、ratio 在哪一级、loss 怎么平均。反向 KL 的方向见 `fund-kl-directions`，和这道平均题无关。现场要是被追问「论文和代码哪个对」，我会说：复现论文就改回 seq-mean-token-mean；跑长 CoT 的生产训练更常留 token-mean，同时在日志里盯着长度和梯度范数。

## 追问

**论文和 veRL 为什么不一致？**
实现为了长文本稳定选了 token-mean。要对齐论文数字，得显式改 `loss_agg_mode`。

**token-mean 下长回复会不会主导梯度？**
会，这是它的特性：每个 token 等权。想让每条样本等权，就用 seq-mean-token-mean。

**mask 怎么进分母？**
只算 response token，输入提示（prompt）和 padding 不进 $\sum|y_i|$。分母漏了 mask，梯度会被 pad 稀释。

**和动态采样有什么关系？**
被滤掉的零方差组根本不进这个求和。先保证有效组，再纠结 reduction，不然平均的全是零。

**和长度惩罚重复吗？**
不重复。reduction 改的是梯度权重，长度惩罚改的是 $r$，两件事可以同时做。
