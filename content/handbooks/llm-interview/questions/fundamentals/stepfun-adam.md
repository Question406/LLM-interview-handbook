---
id: stepfun-adam
section: fundamentals
order: 162
level: A
title: 阶跃星辰：Adam 的公式是什么，一阶二阶矩怎么更新？
quick: >-
  Adam 维护两个指数滑动平均（EMA）：一阶矩 $m$ 是梯度的 EMA，二阶矩 $v$ 是梯度平方的 EMA。做完偏差校正后，更新量是
  $\eta\,\hat m/(\sqrt{\hat v}+\varepsilon)$，每一维按自己的二阶矩缩放步长。大模型上常用 AdamW，把
  weight decay 从自适应分母里拆出来。
tags:
  - StepFun
  - Adam
  - Optimizer
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3'
    type: candidate-first-hand
  - title: Adam
    url: 'https://arxiv.org/abs/1412.6980'
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：“Adam 的公式是什么？”；“Adam 一阶矩、二阶矩和梯度更新是怎么算的？”

Adam 给每个参数维护两个指数滑动平均：一阶矩 $m$ 是梯度的 EMA，二阶矩 $v$ 是梯度平方的 EMA。两者都从 0 起步、早期偏小，要做偏差校正；更新时用 $\hat m$ 除以 $\sqrt{\hat v}$，每一维按自己的梯度大小缩放步长。大模型上要主动补一句 AdamW：weight decay 不进自适应分母。

最常见的丢分是漏写偏差校正，或者嘴上说 $v$ 是「梯度的方差」，写下来却是 $g_t^2$ 的 EMA，还忘了 $m$ 也是有偏的。$g_t$ 是 minibatch 梯度，别和动量 SGD 的单一速度混为一谈。

## 公式和偏差校正

记 $g_t=\nabla_\theta\mathcal{L}_t$。一阶矩、二阶矩都是指数滑动平均：

$$
m_t=\beta_1 m_{t-1}+(1-\beta_1)g_t,\qquad
v_t=\beta_2 v_{t-1}+(1-\beta_2)g_t^2.
$$

默认 $\beta_1=0.9$，$\beta_2=0.999$，$m_0=v_0=0$。若 $\mathbb{E}[g_t]$ 近似恒定，展开 $m_t$：

$$
m_t=(1-\beta_1)\sum_{i=1}^{t}\beta_1^{t-i}g_i,
$$

系数和是 $1-\beta_1^t$，到不了 $1$，所以早期 $m,v$ 系统性偏小。校正：

$$
\hat m_t=\frac{m_t}{1-\beta_1^t},\qquad
\hat v_t=\frac{v_t}{1-\beta_2^t}.
$$

参数更新

$$
\theta\leftarrow\theta-\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\varepsilon}.
$$

偏差校正要能推出来。$m_0=0$，若 $\mathbb{E}[g_i]=\bar g$，则 $\mathbb{E}[m_t]=(1-\beta_1^t)\bar g$，除以 $1-\beta_1^t$ 才把期望拉回 $\bar g$。$\beta_2=0.999$ 时 $1-\beta_2^t$ 在 $t=100$ 仍只有约 $0.095$，早期的 $\sqrt{\hat v}$ 几乎全靠校正，漏写会让前几步步长小一个数量级。

分母是按坐标缩放的：梯度长期大的维度步长自动变小，稀疏或梯度较小的维度相对有更大的有效步长。写更新式时把 $g_t^2$ 标成逐元素平方，别写成 $g_t^\top g_t$ 那个标量，Adam 是坐标自适应，没有用全局二阶信息。$v$ 估的是 $g^2$ 的 EMA，不是中心化方差，中心化的是 AdaBelief 一类变体。

$\varepsilon$ 防除零，也避免 $v\approx 0$ 时步长爆炸，通常取 $10^{-8}$，加在平方根外面：$\sqrt{\hat v}+\varepsilon$。有的实现写成 $\sqrt{\hat v+\varepsilon}$，数值略有不同，被追问就承认两种都见过，论文默认是前者。

## AdamW 为什么要拆衰减

原始 Adam 把 $\lambda\theta$ 加进 $g_t$，衰减量被 $\sqrt{v}$ 除过，不同维度的衰减强度会随自适应项变化。AdamW 把 weight decay 从自适应项里拆出来：$\theta\leftarrow\theta-\eta\hat m/(\sqrt{\hat v}+\varepsilon)-\eta\lambda\theta$，实现上常先做 decay 再走 adam 步。拆开以后，wd 是对 $\theta$ 的各向同性收缩，和「这一维梯度大不大」无关，embedding 和输出头也就不会因为 $v$ 小被衰减得过狠。大模型的预训练和 SFT 几乎都用 AdamW。

白板上可以顺手和动量 SGD 对比：后者只有一条速度 $v\leftarrow\mu v+g$，没有逐维的二阶缩放，也没有 $1-\beta^t$ 校正。还有两点值得提。一是和 warmup 的搭配，早期校正已经在放大步长，再叠高 lr 容易不稳，所以先 warmup 再进入余弦。二是 Adam 照样有学习率，$\eta$ 一直在，只是每一维再被 $\sqrt{v}$ 缩放一次。

## 追问

**为什么 $\beta_2$ 更接近 1？**
二阶矩要更长的记忆才稳，早期校正项 $1-\beta_2^t$ 也更关键。记忆短了，$v$ 会跟着噪声跳，步长波动大。

**能不用偏差校正吗？**
前几百步 $m,v$ 明显偏小，步长先过小再突然正常，曲线难看，微调刚起步时也容易学不动。

**和 RMSProp 有什么区别？**
RMSProp 只有 $v$，Adam 再乘上一阶动量 $\hat m$，方向更稳。两者都是对角自适应，都算不上牛顿法。

**损失（loss）突然出现 NaN 怎么查？**
先查 $\varepsilon$、混合精度下 $v$ 是否下溢、以及 grad clip，改 $\beta$ 排在后面。bf16 下 $v$ 建议保留 fp32 主副本。

**AdamW 和 L2 正则是一回事吗？**
不是。L2 进梯度、再被 $\sqrt{v}$ 缩放；AdamW 的 decay 不进自适应分母，这正是要拆开的原因。
