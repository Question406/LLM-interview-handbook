---
id: baidu-simpo-vs-dpo-length
section: posttrain
order: 206
level: A
title: 百度文心：SimPO 原理是什么？如何缓解 DPO 微调序列过长？
quick: >-
  SimPO 用平均 log-prob（长度归一）直接作为隐式奖励，并设目标 margin，不再依赖单独
  $\pi_{\mathrm{ref}}$ 比值形式的长度放大。对「刷长度抬高总 logp」更不敏感，但仍需用长度统计与人工抽检验证。
tags:
  - Baidu
  - SimPO
  - DPO
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯/百度/minimax 大模型算法面经总结帖
    url: https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279
    type: candidate-first-hand
  - title: SimPO
    url: https://arxiv.org/abs/2405.14734
    type: primary
---

## 真题记录

- 公司：百度 · 文心一言（总结帖收录）
- 原始措辞：**“说一下 simpo 的原理，它是怎么解决 dpo 微调序列过长的问题的”**；另有 **“DPO 如何解决回答过长的问题”**

这块容易声称「SimPO 彻底解决了 DPO 微调过长」。DPO 用序列总 log 概率差时，更长回答更容易堆出更大的绝对间隔，模型学会「啰嗦但偏好赢」。SimPO 把激励改成单位长度质量，对刷长度抬总 logp 明显不敏感，但平均长度、重复 n-gram 和人工抽检仍要做。它还去掉了显式 $\pi_{\mathrm{ref}}$，不是「DPO 换个 $\beta$」。chosen 的绝对 logp 仍可能下降，只要间隔在涨，见 `baidu-dpo-chosen-curve`。现场按「问题 → SimPO 改了什么 → 仍要监控什么 → 何时还用 DPO」答。

## DPO 的长度放大从哪来

DPO 间隔

$$
\Delta_{\mathrm{DPO}}=\beta\Big(\log\tfrac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\tfrac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big)
$$

是完成序列上的求和。多写正确套话、多重复安全措辞，就能抬 $\sum_t\log\pi$，尤其当标注者本身更吃长回答时。这和反向 KL 的 mode-seeking 叠在一起：策略锁住「长而安全」的峰，参考支撑里本来就够得到的废话会被留下，见 `fund-kl-directions`。$\beta$ 只管贴 ref 的幅度，不管 token 数，所以「把 $\beta$ 加大」治不好长度。标注控长、显式长度惩罚、训练时除以 $|y|$ 都是补丁；SimPO 把长度归一写进隐式奖励，激励本身变了。

## SimPO：平均 logp + 目标间隔，无 ref

$$
r(x,y)=\frac{\beta}{|y|}\log\pi_\theta(y\mid x),\qquad
\mathcal{L}_{\mathrm{SimPO}}=-\mathbb{E}\log\sigma\big(r(x,y_w)-r(x,y_l)-\gamma\big).
$$

隐式奖励是长度归一化的平均 log-prob，再设目标间隔 $\gamma$，逼 chosen 比 rejected 高出一块，而不是比「更长」高出一块。对「刷长度抬总 logp」更不敏感。代价也要说：没有 $\pi_{\mathrm{ref}}$ 当锚，漂移要靠 $\beta$、$\gamma$ 和数据本身来管；已经有强参考、偏好对已经控长时，DPO 往往更稳。监控平均长度、重复 n-gram、任务胜率和抽检，不要只看训练 $\mathcal{L}$。后续若切 GRPO，长度 hack 会换成「先写长再碰对」，组大小和长度尾部要分开管，见 `sys-rl-group-n`。token-mean 的 PG reduction 也在削弱长序列占权，但那是 RL 损失的分母，不是偏好目标。

## 追问

- **彻底解决了吗？** 没有。正确说法是「显著缓解并改变激励」。重复模板、无信息长思维链仍可能得分，抽检不能省。
- **为什么能去掉 ref？** 平均 logp 直接当隐式奖励，不再从 $r=\beta\log(\pi/\pi_{\mathrm{ref}})+Z$ 反解。少一张驻留的参考，也少一根漂移仪表。
- **DPO 侧还能做什么？** 序列平均 logp、硬负样本（短而错 vs 长而对）、标注说明「短而对优于长而对」、显式长度惩罚。
- **和 token-mean GRPO 是一回事吗？** 都在削弱「长序列占权」，但一个改偏好损失，一个改 PG reduction，不要说成同一个旋钮。
- **何时仍用 DPO？** 已有强 ref、数据已控长、需要和原 RLHF 闭式解对齐时。SimPO 不是在所有约束下的严格升级。
