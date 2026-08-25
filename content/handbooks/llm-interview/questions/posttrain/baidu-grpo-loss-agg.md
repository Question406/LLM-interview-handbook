---
id: baidu-grpo-loss-agg
section: posttrain
order: 228
level: A
title: 百度后训练一面：GRPO 序列级损失怎么落到每个 token？按序列平均还是按 batch 平均？
quick: >-
  先有 token 损失 $\ell_t=-\rho_t A$，再选 reduction。`seq-mean-token-mean` 先在序列内平均再对样本平均，长文单
  token 权更小；`token-mean` 全 batch 有效 token 等权，veRL 默认。论文 GRPO
  偏前者，长 CoT 时后者更稳。说清你配的 `loss_agg_mode`。
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
- 岗位：大模型 RL 后训练；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“GRPO的损失计算，在序列级别的损失上，损失如何给到每一个token上？序列级别平均 或 批次级别平均”**

这块容易把「优势怎么来」和「损失怎么加」拧成一个旋钮。同一组 $\hat A_i$ 广播到该回复的每一个 response token 之后，reduction 决定谁主导梯度。组大小必须 $n\gt 1$ 才能定义 $\hat A$，见 `sys-rl-group-n`；这题问的是广播之后求和符号写在哪。面试先写 token 级 $\ell_{i,t}$，再写三种平均，最后报你配的 `loss_agg_mode`。只背「按序列平均」或「按 batch 平均」而不写分母，两种模式会被说成同一句话。

## 三种 reduction，长度权重不同

令 $\ell_{i,t}$ 为 token 级 surrogate，例如 $-\min(\rho_{i,t}\hat A_i,\mathrm{clip}(\rho_{i,t})\,\hat A_i)$。veRL 文档里常见三种：

$$
\begin{aligned}
\text{seq-mean-token-mean}&=\frac1B\sum_i\frac1{|y_i|}\sum_t\ell_{i,t},\\
\text{seq-mean-token-sum}&=\frac1B\sum_i\sum_t\ell_{i,t},\\
\text{token-mean}&=\frac{\sum_{i,t}\ell_{i,t}}{\sum_i|y_i|}.
\end{aligned}
$$

seq-mean-token-mean：每条回复权重相同，长文的单个 token 权更小，短回复相对更响。seq-mean-token-sum：每条先对 token 求和再平均，长回复权更大，长度 hack 会被放大。token-mean：batch 内每个有效 token 等权。veRL 示例默认 token-mean，并写明论文原 GRPO 更接近 seq-mean-token-mean。长 CoT 时 token-mean 通常更稳，因为不会把一条长推理链的每个 token 稀释掉；DAPO 的 token-level PG 就是在推这条。没有绝对正确，只有「你有没有声明长度权重」。

## 不要和 KL / GSPO / CISPO 混

KL 按 token 还是按序列，是正则 reduction，不是 policy gradient reduction。GSPO 把 likelihood ratio 提到序列级，clip 的粒度变了；CISPO 仍是 token 级损失，但 clip 的是 detach 后的 IS 权重，梯度始终走 $\log\pi$，见 `pt-cispo`。三套旋钮要拆开：优势怎么来（组相对）、ratio 在哪一级、loss 怎么平均。反向 KL 的方向仍见 `fund-kl-directions`，和这道平均题无关。现场若被追「论文和代码哪个对」，答：复现论文改回 seq-mean-token-mean；跑长 CoT 生产更常留 token-mean，并在日志里盯长度与梯度范数。

## 追问

- **论文和 veRL 为什么不一致？** 实现为了长文稳定选了 token-mean；要对齐论文数字，必须显式改 `loss_agg_mode`。
- **长回复会不会被 token-mean 主导？** 会。这是特性：每个 token 等权。若要样本等权，用 seq-mean-token-mean。
- **mask 怎么进分母？** 只计 response token，prompt 与 padding 不进 $\sum|y_i|$。分母漏 mask，梯度会被 pad 稀释。
- **和动态采样什么关系？** 滤掉的零方差组根本不进这根求和。先保证有效组，再纠结 reduction，否则平均的是零。
- **和长度惩罚重复吗？** 不重复。reduction 改的是梯度权重；长度惩罚改的是 $r$。两件事可以同时做。
