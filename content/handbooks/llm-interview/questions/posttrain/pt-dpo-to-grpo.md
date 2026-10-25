---
id: pt-dpo-to-grpo
section: posttrain
order: 24
level: S
title: DPO 后模型分布变尖，还能直接接 GRPO 吗？
quick: "可以接，前提是当前 policy 还有足够的采样多样性。同题采样几乎一样时，组内奖励方差接近 0，GRPO 的相对优势就没有信号；先做一组 on-policy 诊断，必要时恢复可控探索，再接 GRPO，同时盯住能力漂移。"
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

能接，关键看 DPO 之后同一道题采 $G$ 条候选，它们之间还有没有能被 验证器（verifier） 分开的差异。直接偏好优化（DPO） 可以当 warm start，把策略推到偏好更好的区域；GRPO 再靠当前策略的在线组采样挖相对优势。分布尖一点没关系，组内方差为零才接不上。「DPO 之后熵一定崩，不能接 GRPO」和「DPO 是更好的初始化，直接上就行」这两句口号都不对。

## GRPO 吃的是组内方差

同一输入提示 采 $o_1,\ldots,o_G$，拿到标量奖励 $r_i$，

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon},\qquad \mu=\frac1G\sum_j r_j.
$$

比如 DPO 之后用温度采一组，几条回复几乎字面相同，或者一组全对、全错，那 $\sigma\approx 0$，$\hat{A}\approx 0$，这一批就是空梯度。DPO 的 Bradley-Terry 目标会压低 rejected、抬高 chosen，有可能把分布变尖，但这既不是定理，也不总会发生，数据覆盖、$\beta$ 和过拟合程度都会影响熵。所以要去量 采样轨迹（rollout），别凭感觉猜熵。

先看几样东西：组内 reward 的标准差、unique response 的比例、`pass@k` 和 `pass@1` 的差距、token 熵，以及 DPO 的 chosen/rejected log-margin。`pass@k` 仍然明显高于 `pass@1`，说明搜索空间里还有被漏掉的成功轨迹，GRPO 才有东西可以放大。判据可以写成一句话：DPO 之后 `pass@k - pass@1` 仍明显大于 $0$，而且组内 $r_i$ 不是常数。满足就上 GRPO；不满足，先改题目难度或采样，别加大学习率硬推。

## 怎么接

可执行的接法是：DPO 结束后先冻结，做一组 on-policy 诊断（$G\ge 8$、温度和线上接近），再决定是直接 GRPO、先升温，还是回到更难的偏好数据补一轮。跳过诊断、只改学习率，是最常见的失败方式。组方差已经塌了还猛更新，等于在同一条回复上反复强化，分布只会更尖，held-out 也更容易掉。

需要恢复探索时，可以把温度或 `top-p` 略微抬高、加熵奖励或熵下界、减小 GRPO 的学习率、把 clip 收紧。目的是把「还能采到不同答案」找回来，模型用不着被打回随机。必要时混一小部分 监督微调（SFT） 或 DPO 的 replay，锁住格式和通用能力，免得 online 强化学习（RL） 在长回复上只学会灌水。

reference 锚点要明确说选的是谁，别默认「reference 就是上一个 checkpoint」。用 DPO checkpoint 当 $\pi_{\mathrm{ref}}$，KL 管的是局部偏离，适合「已经很强、只想在可验证任务上再挤一点」；用更早的 SFT 当锚，探索空间更大，优化的张力也更大，容易把 DPO 刚对齐好的风格拉散。KL 系数要跟着锚点改：锚越旧、分布差越大，同样的 $\beta$ 可能把探索直接掐死，也可能完全管不住漂移。

训练时别只盯 reward。reward 上涨可能来自长度、格式 hack，或者组内对照变弱（大家都变好之后 std 又塌了）。要同时看组方差、回复长度、到锚点的 KL，以及独立的 held-out，尤其是 DPO 偏好集和 RL verifier 分布不一致的那些集合。能力漂移比「接不接得上」更常见：数学涨了，指令遵循掉了。

## 追问

**DPO 一定会降低熵吗？**
不一定。它降低的是「选错偏好方向」的概率质量，会不会塌成单点，取决于数据和 $\beta$。用采样指标说话。

**组全对的时候怎么办？**
提高题目难度、加大 $G$、换更细的过程分，或者接受这一批梯度为 $0$。硬加噪声会把格式搞坏。

**先 GRPO 再 DPO 行不行？**
可以，但 DPO 的离线偏好可能和 RL 之后的 on-policy 分布错位，等于拿旧的对比去拉新的策略。更常见的顺序还是 SFT $\to$ 偏好（DPO/PPO）$\to$ 可验证 RL。
