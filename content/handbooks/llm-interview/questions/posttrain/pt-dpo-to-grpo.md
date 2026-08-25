---
id: pt-dpo-to-grpo
section: posttrain
order: 24
level: S
title: DPO 后模型分布变尖，还能直接接 GRPO 吗？
quick: >-
  可以，但先确认当前 policy 还有足够 rollout diversity。若同题采样几乎相同，组内 reward 方差接近 0，GRPO
  的相对优势会失去信号；应先恢复可控探索并监控能力漂移。
tags:
  - DPO
  - GRPO
  - 真实面经
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: 2026 淘天 Agent 面经
    url: 'https://www.nowcoder.com/discuss/909920471301226496'
    type: legacy-reference
  - title: DPO 原论文
    url: 'https://arxiv.org/abs/2305.18290'
    type: legacy-reference
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
---

这块容易两句口号：「DPO 之后熵一定崩，不能接 GRPO」或「DPO 是更好的初始化，直接上就行」。DPO 可以当 warm start，把策略推进偏好更好的区域；GRPO 再靠当前策略的在线组采样挖相对优势。接不接得上，看的不是「DPO 三个字母」，而是同题 $G$ 条候选是否还存在可被 verifier 分开的差异。

## 1. GRPO 吃的是组内方差

同一 prompt 采 $o_1,\ldots,o_G$，标量奖励 $r_i$，

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon},\qquad \mu=\frac1G\sum_j r_j.
$$

若 DPO 后温度采样几乎字面相同，或一组全对 / 全错，则 $\sigma\approx 0$，$\hat{A}\approx 0$，这一批是空梯度。DPO 的 Bradley-Terry 目标会压低 rejected、抬高 chosen，有可能把分布变尖，但这既不是定理也不是总发生：数据覆盖、$\beta$、过拟合程度都会改熵。真正要量的是 rollout，不是臆测熵。

建议先看：组内 reward std、unique response 比例、`pass@k` 与 `pass@1` 的缺口、token 熵、以及 DPO 的 chosen/rejected log-margin。`pass@k` 仍明显高于 `pass@1`，说明搜索空间里还有被漏掉的成功轨迹，GRPO 才有东西 amplify。

## 2. 可以接，但先恢复可控探索

温度 / `top-p` 略抬、加熵奖励或熵下界、减小 GRPO 学习率、clip 更紧，都是把「还能采到不同答案」找回来，而不是把模型打回随机。必要时装一小部分 SFT 或 DPO replay，锁格式与通用能力，避免 online RL 在长回复上只学灌水。

Reference 锚点要显式选：

- 以 **DPO checkpoint** 为 $\pi_{\mathrm{ref}}$：KL 管局部偏离，适合「已经很强、只想在可验证任务上再挤」。
- 以 **更早的 SFT** 为锚：探索空间更大，优化张力也更大，容易把 DPO 刚对齐的风格拉散。

不要默认「reference 就是上一行 checkpoint」而不说选的是谁。KL 系数也要跟着锚点改：锚越旧、分布差越大，同样的 $\beta$ 可能把探索直接掐死，或反过来完全管不住漂移。

一条可执行的接法：DPO 结束后先冻结做一组 on-policy 诊断（$G\ge 8$、与线上接近的温度），再决定是直接 GRPO、先升温、还是回到更难的偏好数据补一轮。跳过诊断、只改学习率，是最常见的失败方式。组方差塌了还猛更新，等于在同一条回复上反复强化，分布只会更尖，held-out 也更容易掉。

## 3. 监控不要只盯训练 reward

Reward 上涨可能来自长度、格式 hack 或组内对照变弱（大家都变好之后 std 又塌）。并行看组方差、回复长度、KL 到锚、以及独立 held-out（尤其 DPO 偏好集与 RL verifier 分布不一致的集合）。能力漂移比「接不接得上」更常见：数学涨了，指令遵循掉了。

淘天面经问这条，考的是你知不知道 GRPO 的信号来自相对而不是绝对：尖分布不是禁令，零方差才是。接得上的判据可以写成一句话：DPO 之后 `pass@k - pass@1` 仍明显大于 $0$，并且组内 $r_i$ 不是常数。满足再上 GRPO；不满足先改题难度或采样，而不是加大学习率硬推。

## 追问

- **DPO 一定降低熵吗？** 不一定。它降低的是「选错偏好方向」的概率质量；是否变成单点，取决于数据和 $\beta$。用采样指标说话。
- **组全对时怎么办？** 提高题难、加大 $G$、换更细的过程分，或接受这批梯度为 $0$。硬加噪声会毁格式。
- **先 GRPO 再 DPO 行不行？** 可以，但 DPO 的离线偏好可能与 RL 后的 on-policy 分布错位，等于在旧对比上拉新策略。更常见仍是 SFT $\to$ 偏好（DPO/PPO）$\to$ 可验证 RL。
