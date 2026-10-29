---
id: baidu-simpo-vs-dpo-length
section: posttrain
order: 206
level: A
title: 百度文心：SimPO 原理是什么？如何缓解 DPO 微调序列过长？
quick: "SimPO 用长度归一的平均 log-prob 直接当隐式奖励，再设一个目标 margin，不再依赖单独的 $\\pi_{\\mathrm{ref}}$ 比值形式带来的长度放大。它把激励改成单位长度的质量，对「刷长度抬高总 logp」更不敏感，但长度统计和人工抽检还得做。"
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

SimPO 把 DPO 里「策略相对参考的总 log 概率」换成长度归一的平均 log-prob，直接当隐式奖励，再要求 chosen 比 rejected 高出一个目标间隔 $\gamma$，同时去掉了显式的 $\pi_{\mathrm{ref}}$。它缓解过长靠的是改激励：模型拿到的是单位长度的质量分，多写不再自动加分。但它没有彻底解决过长，平均长度、重复 n-gram 和人工抽检还得做。

现场我按「问题 → SimPO 改了什么 → 还要监控什么 → 什么时候还用 DPO」来答。

先看 DPO 的长度放大从哪来。DPO 的间隔

$$
\Delta_{\mathrm{DPO}}=\beta\Big(\log\tfrac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\tfrac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big)
$$

是在完成序列上求和的。多写几句正确的套话、多重复几遍安全措辞，就能把 $\sum_t\log\pi$ 抬上去，标注者本身更吃长回答时更明显，模型就学会了「啰嗦但偏好赢」。这又和 reverse KL 的 mode-seeking 叠在一起：策略锁住「长而安全」的峰，参考支撑里本来就够得到的废话被留了下来，见 `fund-kl-directions`。$\beta$ 只管贴 ref 的幅度，不直接控制 token 数，所以把 $\beta$ 加大治不了长度。标注控长、显式长度惩罚、训练时除以 $|y|$ 都是补丁；SimPO 把长度归一写进了隐式奖励，激励本身变了。

SimPO 的写法是

$$
r(x,y)=\frac{\beta}{|y|}\log\pi_\theta(y\mid x),\qquad
\mathcal{L}_{\mathrm{SimPO}}=-\mathbb{E}\log\sigma\big(r(x,y_w)-r(x,y_l)-\gamma\big).
$$

隐式奖励是长度归一的平均 log-prob，目标间隔 $\gamma$ 逼着 chosen 比 rejected 高出一块，赢面要来自质量，写得更长不再占便宜。所以它对「刷长度抬总 logp」更不敏感。它也不是「DPO 换个 $\beta$」，显式的 $\pi_{\mathrm{ref}}$ 被去掉了。代价是没有 $\pi_{\mathrm{ref}}$ 当锚，漂移要靠 $\beta$、$\gamma$ 和数据本身来管；已经有强参考、偏好对也已经控过长的时候，DPO 往往更稳。和 DPO 一样，chosen 的绝对 logp 仍可能下降，只要间隔在涨就行，见 `baidu-dpo-chosen-curve`。监控看平均长度、重复 n-gram、任务胜率和抽检，别只看训练 $\mathcal{L}$。后面要是切到 GRPO，长度 hack 会变成「先写长再碰对」，组大小和长度尾部要分开管，见 `sys-rl-group-n`。token-mean 的 PG reduction 也在削弱长序列的权重，但那是 RL 损失的分母，和偏好目标是两回事。

## 追问

**SimPO 彻底解决了过长吗？**
没有。准确的说法是「显著缓解，并且改变了激励」。重复模板、没信息量的长 chain of thought 仍可能拿分，抽检省不了。

**为什么能去掉 ref？**
平均 logp 直接当隐式奖励，不再从 $r=\beta\log(\pi/\pi_{\mathrm{ref}})+Z$ 反解。少驻留一个 reference model，也少了一根监控漂移的仪表。

**DPO 这边还能做什么？**
用序列平均 logp，构造硬负样本（短而错 vs 长而对），在标注说明里写「短而对优于长而对」，或者加显式长度惩罚。

**和 token-mean 的 GRPO 是一回事吗？**
不是。两者都在削弱长序列的权重，但一个改偏好损失，一个改 PG 的 reduction，别说成同一个旋钮。

**什么时候还是用 DPO？**
已经有强 ref、数据已经控长、需要和原来的 RLHF 闭式解对齐时。SimPO 并不是在所有约束下都严格更好。
