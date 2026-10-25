---
id: ali-multineg-then-grpo
section: posttrain
order: 8
level: S
title: 淘天面经：单正多负 DPO 后，能否再接 GRPO？分类场景为何 DPO 常更稳？
quick: "能接。多负例 DPO 主要学「正例优于各个负例」，不保证学会负例之间的排序；之后接 GRPO 可以用当前策略继续探索，但要先检查输出是不是太集中、候选之间还有没有差异。分类标签或偏好清晰时，DPO 往往更稳、成本更低。"
tags:
  - Alibaba
  - DPO
  - GRPO
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

能接。多负例 DPO 主要学的是「正例优于各个负例」，负例之间的细致排序它不保证；之后接 GRPO，可以用当前策略采样、在可验证奖励上继续探索，前提是 DPO 之后组内还能采出被奖励分开的差异。分类这种标签或偏好很清晰的场景，DPO 通常更稳、更省。

这题常听到两种说法，一种是「多负 DPO 已经学全排序，不必再 RL」，一种是「DPO 后熵一定崩，不能接 GRPO」，两种都太绝对。接续时怎么诊断见 `pt-dpo-to-grpo`，三种方法的对比见 `ali-ppo-dpo-grpo-ask`。

先看多负 DPO 学到了什么。单正多负一般是把一条 chosen 和多条 rejected 拆成多个 pair，或者写成 listwise 变体。Bradley-Terry 目标拉高 $\pi_\theta(y_w\mid x)$、压低各个 $y_l$，并不会自动得到 $y_l$ 之间的序。业务上如果要「错误 A 比错误 B 更可接受」，就得有更完整的 ranking 标注或额外约束，别假设多负已经给出了全序。DPO 还可能让分布变尖，$\beta$ 大、负例太容易、过拟合都会让采样多样性下降。这不是定理，要拿实际采样结果去验证，别口头断言熵怎么样了。

再看接 GRPO 的条件。GRPO 按同一道题各个回答在组内的相对得分计算优势：

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon}.
$$

DPO 之后如果同一道题采出来几乎一样，或者一组全对 / 全错，$\sigma\approx 0$，相对信号就消失了。这时先调温度 / 熵、减小学习率，或者回放一部分监督微调（SFT）数据，别加大步长硬推。组内 advantage 的细节见 `ali-grpo-advantage`。Reference 锚点也要说清，用 DPO checkpoint 还是更早的 SFT，KL 系数跟着变。

分类场景 DPO 更稳，是因为标签边界清晰、偏好噪声低，比如意图分类、是否拒答、格式对错，这时离线偏好对通常比 on-policy 强化学习（RL）更稳、成本更低。GRPO 更依赖验证器和采样质量，分类往往没有「多种正确轨迹」可以探索，组方差天然就小，组内常常全对或全错，RL 容易空转或刷格式。可验证的工具成功率、数学、代码才更配 GRPO。阶段顺序仍然是 SFT 学协议，DPO 学偏好，需要探索再上 RL，见 `ali-sft-then-posttrain`。

## 追问

**多负等于 listwise 吗？**
不等于。多个 pair 只约束「正优于各负」，负例之间没有直接的梯度。

**DPO 之后一定不能接 GRPO？**
不一定。看 `pass@k-pass@1` 和组内奖励的标准差，别光凭熵高低下结论。

**负例怎么造？**
要 hard negative，也就是近义的错误类别。随机负例只会让模型学会「别说废话」，学不到边界。
