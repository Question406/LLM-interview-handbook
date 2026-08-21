---
id: fund-warmup
section: fundamentals
order: 8
level: A
title: Warmup 为什么有用？
quick: 训练初期 optimizer moments、激活/梯度统计与参数适配尚未稳定，大 LR 容易产生巨大更新；warmup 让 LR 从小到目标值逐步增加。
tags:
  - Optimization
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Accurate, Large Minibatch SGD
    url: https://arxiv.org/abs/1706.02677
    type: primary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: secondary
---

训练初期 optimizer 的一阶 / 二阶矩、激活尺度和残差分支都还没进入稳定统计，若用目标学习率直接开跑，一次更新就可能把 logits 或 LayerNorm 后的幅度打飞。Warmup 把 LR 从接近 0 抬到目标值，让这些统计先在小步长下形成。它不是宗教仪式：大 batch、Adam、深层 Transformer 上更常见，小模型小 batch 上可能几乎无感。面试别背「Transformer 都必须 warmup 多少步」——要说清它在保护什么，以及 post-training 里同类问题。初期矩估计和激活统计未稳，大 LR 容易一步打飞；warmup 让步长从小抬到目标值。大 batch、Adam、深层网络上更有用，不是固定仪式。RL 里优势尺度未稳时同样先别迈大步。用更新比验收，不要抄一个与模型无关的步数。

## 初期真正不稳的是统计，不是「学习率数字太大」

Adam / AdamW 的 $\hat{m},\hat{v}$ 从 0 起步。前几步 $v$ 偏小，有效步长 $\eta/\sqrt{v}$ 可以异常大，再乘上尚未归一好的梯度，参数跳动剧烈。大 batch 还会减少梯度噪声，使每步方向更「硬」、更一致地往错误尺度上走，这正是 ImageNet 大 batch 训练里引入线性 warmup 的动机。

Transformer 还有自己的早期病：残差与注意力尚未学会合理的尺度，过大的更新会让某一层的输出范数主导后面所有层。Warmup 期间模型相当于用很小的步长做「校准」，目标 LR 要等二阶矩和激活进入可工作的范围后再用。Goyal 等人把线性 warmup 当作大 batch SGD 能逼近小 batch 曲线的条件之一；Vaswani 等人的 Transformer 则用 warmup 后再逆平方根衰减的日程。两者场景不同，共同点是：**先让优化器与网络进入可预测的局部，再给满步长**。

Warmup 长度与初始化、batch、深度、是否用预归一化有关，没有与模型无关的步数定律。Pre-LN 通常比 Post-LN 更能忍短 warmup，但不能据此说可以取消。Adam 的偏差修正 $(\hat{m}/(1-\beta_1^t))$ 在 $t$ 很小时会放大早期梯度，这是矩估计问题，不是「学习率写错了」那么简单。Warmup 用小 $\eta$ 对冲这段不可靠。大 batch 下噪声小，错误尺度会被一致执行很多步，所以 Goyal 等人把线性 warmup 当作大 batch 能逼近小 batch 结果的条件之一。小 batch 的噪声本身像一种正则，warmup 的收益往往更小。面试把「保护早期统计」讲清楚，比背 Transformer 论文里的具体步数有用。

## 日程怎么接，比「用了 warmup」更重要

常见接法：线性从 0 到 $\eta_{\max}$，再接 cosine / 逆平方根 / 阶梯衰减。断点要合理：warmup 太短，等于没保护；太长则大部分预算耗在欠学习率上，后期才开始真正拟合。和 batch size 联动时，线性缩放 $\eta$ 往往 **一起** 加长 warmup，而不是只把峰值 LR 乘上去。

不要把 warmup 和 gradient clipping 当成同一件事。Clip 限制单步范数；warmup 限制学习率随时间的可用幅度。可以同时用。也不要把 warmup 理解成「从差的初始化爬出来」的数据课程——它基本不改变样本顺序，只改变步长。若 loss 在 warmup 结束后才突然爆炸，更该查峰值 LR、稳定性（FP16）、或数据坏 batch，而不是无限加长 warmup 掩饰。

记录上应画出 LR 与 grad norm / 更新比。Warmup 段 grad norm 偏高但被小 LR 压住，是预期；warmup 一结束更新比冲高，说明峰值 LR 仍太大。常见误用是把 warmup 拉得很长来掩盖峰值 LR 过大：曲线看起来平滑，有效训练预算被吃掉。另一个误用是 cosine 从峰值立刻下降、warmup 只占极短，等于没保护。和 weight decay、clip 的配合：warmup 期间 decay 仍在，小步长下衰减相对更明显，有人会在 warmup 关掉 decay，这是实现细节，要能说「我知道它在改有效目标」。不要把 warmup 说成数据课程学习，它几乎不改变样本顺序。

## Post-training / RL 里同样有「先别迈大步」

SFT 之后接 PPO / GRPO 时，reward、advantage 的尺度一开始也不稳：RM 分数未归一、组内 baseline 还在抖。此时用目标 KL 系数和学习率直接推策略，容易一步 drift。短 warmup（或从小 $\eta$、从保守 $\beta$ 过渡）的作用类似：等优势估计的统计稳定，再允许较大更新。这和预训练 warmup 机制相同、对象不同：一个保激活与 Adam 矩，一个保策略相对 $\pi_{\mathrm{ref}}$ 的距离。

RL 里若用自适应 KL controller，也有滞后：前几步实测 KL 不可靠，立刻按它猛调 $\beta$ 会造成振荡。先固定 $\beta$ 或限制 $\beta$ 变化率，等价于给 controller 做 warmup。不要把这些说成另一套神秘技巧。SFT 自己也可以 warmup：从预训练 LR 切到指令数据时，分布突变，短 warmup 能减少一开始就把指令格式冲掉。原则相同：统计未稳时不要给满步长。把预训练、SFT、RL 三处的 warmup 都收束成这句话，这题就从「背日程」变成「会迁移」。

原则就是一句话：统计未稳时不要给满步长。保护的对象可以是 Adam 矩、激活范数、优势尺度或 KL controller。长度没有跨架构的定律，应用更新比和 KL 是否在目标带内来验收，而不是抄论文步数。训练初期 Adam 矩、激活和残差尺度都还没进入稳定统计，目标学习率一步就可能把更新打飞，所以要把 LR 从接近 0 抬到峰值。大 batch 噪声小，错误尺度会被一致执行，warmup 更必要。它保护的是早期统计，不是数据课程，也不能替代好的初始化。Post-training 里优势尺度和 KL controller 同样需要「先别迈大步」。长度用更新比和 KL 是否在目标带内验收。

## 追问

- **小 batch 还要 warmup 吗？** 不一定。噪声本身在限制步长。大 batch + Adam + 深 Transformer 上理由最强。小模型小 batch 上可能几乎无感，不要当仪式。
- **为什么和 batch 一起线性放大 LR 时更需要？** 有效步更确定、初期偏差会被一致地放大，warmup 用来度过矩估计不可靠的阶段。只放大峰值 LR、不加长 warmup，是常见翻车。
- **Warmup 能替代好的初始化吗？** 不能。初始化决定起点；warmup 只是起点附近的步长课表。Post-LN 与差初始化会让你更依赖它，但不能反过来。
- **RL 没有「epoch 意义」的步数，怎么设？** 按更新次数或 token 数设一段短日程，并以 KL / 熵是否在目标带内为验收，而不是抄预训练的步数。controller 也应对 $\beta$ 的变化率做限制，等价于给调节过程 warmup。
