---
id: fund-warmup
section: fundamentals
order: 8
level: A
title: Warmup 为什么有用？
quick: "Warmup 保护的是训练刚开始统计还没稳的那段时间：Adam 的一阶、二阶矩和激活、梯度尺度都还没就位，直接用目标学习率，一步就可能把参数推得太远。所以让学习率从接近 0 慢慢升到目标值，长度够不够看 grad norm 和更新比。"
tags:
  - Optimization
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Accurate, Large Minibatch SGD
    url: https://arxiv.org/abs/1706.02677
    type: primary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: secondary
---

Warmup 有用，是因为训练刚开始时 optimizer 的一阶 / 二阶矩、激活尺度和残差分支都还没进入稳定统计，这时用目标学习率直接开跑，一次更新就可能让 logits 或 LayerNorm 后的幅度突然变大。Warmup 把 LR 从接近 0 抬到目标值，让这些统计先在小步长下形成。它在大 batch、Adam、深层 Transformer 上作用最明显，小模型小 batch 上可能几乎感觉不到。

举个例子，Adam 刚开始的几步里 $v$ 还很小，有效步长 $\eta/\sqrt{v}$ 会异常大，再乘上还没归一好的梯度，参数跳得很剧烈。如果再是大 batch，梯度噪声小，每一步方向更「硬」，会更一致地往错误的尺度上走。ImageNet 大 batch 训练引入线性 warmup，就是这个动机。

## 初期到底哪里不稳

Adam / AdamW 的 $\hat{m},\hat{v}$ 从 0 起步，前几步 $v$ 偏小，这就是上面例子的来源。Adam 的偏差修正 $(\hat{m}/(1-\beta_1^t))$ 在 $t$ 很小时还会放大早期梯度，这是矩估计本身的问题，warmup 用小 $\eta$ 去对冲这段不可靠。

Transformer 还有自己的早期毛病：残差和注意力还没学会合理的尺度，过大的更新会让某一层的输出范数主导后面所有层。Warmup 期间模型相当于在用很小的步长做校准，等二阶矩和激活进入可工作的范围，再用目标 LR。Goyal 等人把线性 warmup 当作大 batch SGD 能逼近小 batch 曲线的条件之一，Vaswani 等人的 Transformer 用的是 warmup 后再逆平方根衰减。两者场景不同，思路一样：先让优化器和网络进入可预测的局部，再给满步长。

所以 warmup 多长没有和模型无关的定律，要看初始化、batch、深度、是否用预归一化。Pre-LN 通常比 Post-LN 更能忍短 warmup，但也不能据此就取消。小 batch 的噪声本身像一种正则，warmup 的收益往往更小。面试时别背「Transformer 都必须 warmup 多少步」，说清它在保护什么就够了。

## 日程怎么接、怎么验收

常见接法是线性从 0 升到 $\eta_{\max}$，再接 cosine、逆平方根或阶梯衰减。断点要合理：warmup 太短等于没保护；太长则大部分预算花在欠学习率上，到后期才开始真正拟合。和 batch size 联动时，线性放大 $\eta$ 往往要一起加长 warmup，光把峰值 LR 乘上去容易出事。

验收看曲线，把 LR 和 grad norm / 更新比画在一起。Warmup 段 grad norm 偏高但被小 LR 压住，这是预期；warmup 一结束更新比就冲高，说明峰值 LR 还是太大。常见误用有两个。一个是把 warmup 拉得很长来掩盖峰值 LR 过大，曲线看着平滑，有效训练预算却被吃掉；另一个是 cosine 从峰值立刻下降、warmup 只占极短一段，等于没保护。如果损失（loss）在 warmup 结束后才突然爆炸，先查峰值 LR、FP16 下的稳定性或者坏 batch，别靠无限加长 warmup 去掩饰。

Warmup 和 gradient clipping 是两件事：clip 限制单步范数，warmup 限制学习率随时间的可用幅度，两个可以同时用。它也算不上「从差的初始化爬出来」的数据课程，基本不改变样本顺序，只改步长。和 weight decay 的配合要说得清：warmup 期间 decay 仍在，小步长下衰减相对更明显，有人会在 warmup 里关掉 decay。这是实现细节，但要知道它在改有效目标。

## Post-training 和 RL 里的同类问题

监督微调（SFT）之后接 PPO / GRPO 时，奖励分数（reward）和 advantage 的尺度一开始也不稳：奖励模型（RM）分数没归一，组内 baseline 还在抖。这时用目标 KL 系数和学习率直接推策略，容易一步 drift。短 warmup，或者从小 $\eta$、从保守的 $\beta$ 过渡，作用和预训练一样，等优势估计的统计稳定了再允许较大更新。机制相同，保护的对象不同：预训练保的是激活和 Adam 矩，RL 保的是策略相对 $\pi_{\mathrm{ref}}$ 的距离。

RL 里用自适应 KL controller 也有滞后。前几步实测的 KL 不可靠，立刻按它猛调 $\beta$ 会振荡；先固定 $\beta$ 或限制 $\beta$ 的变化率，相当于给 controller 做 warmup。SFT 自己也可以 warmup：从预训练 LR 切到指令数据时分布突变，短 warmup 能减少一上来就把指令格式冲掉。原则都一样，统计没稳时别给满步长。

## 追问

**小 batch 还要 warmup 吗？**
不一定。小 batch 的噪声本身就在限制步长，小模型小 batch 上可能几乎无感，不必当仪式。理由最强的是大 batch + Adam + 深 Transformer。

**为什么和 batch 一起线性放大 LR 时更需要 warmup？**
因为有效步更确定，初期的偏差会被一致地放大，warmup 用来度过矩估计不可靠的阶段。只放大峰值 LR、不加长 warmup，是常见翻车。

**Warmup 能替代好的初始化吗？**
不能。初始化决定起点，warmup 只是起点附近的步长课表。Post-LN 和差的初始化会让你更依赖 warmup，但拿它去顶替初始化行不通。

**RL 没有「epoch 意义」上的步数，warmup 怎么设？**
按更新次数或 token 数设一段短日程，以 KL / 熵是否落在目标带内来验收，别抄预训练的步数。Controller 也要限制 $\beta$ 的变化率，相当于给调节过程 warmup。
