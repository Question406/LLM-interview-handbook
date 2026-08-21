---
id: stepfun-adam
section: fundamentals
order: 162
level: A
title: 阶跃星辰：Adam 的公式是什么，一阶二阶矩怎么更新？
quick: >-
  一阶矩 $m$ 是梯度 EMA，二阶矩 $v$ 是梯度平方 EMA，偏差校正后步长为 $\eta\,\hat m/(\sqrt{\hat v}+\varepsilon)$。它自适应每维学习率，大模型里常和权重衰减做成
  AdamW。
tags:
  - StepFun
  - Adam
  - Optimizer
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
  - title: Adam
    url: https://arxiv.org/abs/1412.6980
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Adam的公式是什么？”**；**“Adam一阶矩、二阶矩和梯度更新是怎么算的？”**

陷阱是漏写偏差校正，或把 $v$ 说成「梯度的方差」却写下 $g_t^2$ 的 EMA 却忘了 $m$ 也是有偏的。$g_t$ 是 minibatch 梯度，不要和动量 SGD 的单一速度混为一谈。大模型上还要主动补一句 AdamW：衰减不进自适应分母。

## 公式与偏差校正从哪来

记 $g_t=\nabla_\theta\mathcal{L}_t$。一阶矩、二阶矩都是指数滑动平均：

$$
m_t=\beta_1 m_{t-1}+(1-\beta_1)g_t,\qquad
v_t=\beta_2 v_{t-1}+(1-\beta_2)g_t^2.
$$

默认 $\beta_1=0.9$，$\beta_2=0.999$，$m_0=v_0=0$。若 $\mathbb{E}[g_t]$ 近似恒定，展开 $m_t$：

$$
m_t=(1-\beta_1)\sum_{i=1}^{t}\beta_1^{t-i}g_i,
$$

系数和为 $1-\beta_1^t$ 而不是 $1$，早期 $m,v$ 系统性偏小。校正：

$$
\hat m_t=\frac{m_t}{1-\beta_1^t},\qquad
\hat v_t=\frac{v_t}{1-\beta_2^t}.
$$

参数更新

$$
\theta\leftarrow\theta-\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\varepsilon}.
$$

分母按坐标缩放：梯度长期大的维步长自动变小，稀疏或小梯度维相对走得开。$\varepsilon$ 防除零，也避免 $v\approx 0$ 时步长爆炸。面试写清：$v$ 估的是 $g^2$ 的 EMA，不是中心化方差；中心化是 AdaBelief 一类变体。

## AdamW 为什么要拆衰减

原始 Adam 把 $\lambda\theta$ 加进 $g_t$，衰减量被 $\sqrt{v}$ 除过，不同维衰减强度随自适应项漂。AdamW 把权重衰减从自适应项里拆出：$\theta\leftarrow\theta-\eta\hat m/(\sqrt{\hat v}+\varepsilon)-\eta\lambda\theta$（实现上常先 decay 再 adam 步）。大模型预训练 / SFT 几乎都是 AdamW。白板对比动量 SGD：后者只有一条速度 $v\leftarrow\mu v+g$，没有逐维二阶缩放，也没有 $1-\beta^t$ 校正。

偏差校正要能推，不要只背公式。$m_0=0$，若 $\mathbb{E}[g_i]=\bar g$，则 $\mathbb{E}[m_t]=(1-\beta_1^t)\bar g$，除以 $1-\beta_1^t$ 才把期望拉回 $\bar g$。$\beta_2=0.999$ 时 $1-\beta_2^t$ 在 $t=100$ 仍只有约 $0.095$，早期 $\sqrt{\hat v}$ 几乎全靠校正，漏写会让前几步步长小一个数量级。面试写更新式时把 $g_t^2$ 标成逐元素平方，不要写成 $g_t^\top g_t$ 那个标量——Adam 是坐标自适应，不是全局二阶。$\varepsilon$ 通常 $10^{-8}$，加在平方根外面：$\sqrt{\hat v}+\varepsilon$，有的实现写成 $\sqrt{\hat v+\varepsilon}$，数值略不同，被追就承认两种都见过，默认论文是前者。

大模型场景还要提：和权重衰减解耦后，wd 是对 $\theta$ 的各向同性收缩，和「这一维梯度大不大」无关，embedding 与输出头才不会因为 $v$ 小而被衰减得过狠。和 warmup 搭配：早期校正已经在放大步长，再叠高 lr 容易不稳，所以先 warmup 再进入余弦。不要把 Adam 说成「没有学习率」——$\eta$ 仍在，只是被每维 $\sqrt{v}$ 再缩放。

## 面试收口：两行矩、一行校正、一句 AdamW

阶跃这题要看你会不会写，不是会不会念「自适应学习率」。先写 $m,v$ 的 EMA，标清 $g_t^2$ 是逐元素平方。再写 $1-\beta^t$ 校正，并能用「系数和不是 $1$」推一句。最后写 $\hat m/(\sqrt{\hat v}+\varepsilon)$，默认 $\beta_1=0.9,\beta_2=0.999$。大模型补 AdamW：衰减不进自适应分母，否则 embedding 和小梯度维被衰减得莫名其妙。和动量 SGD 对比只要一句：那边没有逐维二阶，也没有偏差校正。NaN 先查混合精度里的 $v$ 和 clip，不要先改 $\beta$。现场把公式写对、校正能推、AdamW 能说出「拆」的原因，比背一篇博客完整。

## 追问

- **为什么 $\beta_2$ 更接近 1？** 二阶矩要更长的记忆才稳，校正项 $1-\beta_2^t$ 早期也更关键。短记忆会让 $v$ 跟着噪声跳，步长发抖。
- **能不用校正吗？** 前几百步 $m,v$ 明显偏小，步长会先过小再突然正常，曲线难看，微调刚起步也容易学不动。
- **和 RMSProp？** RMSProp 只有 $v$；Adam 再乘一阶动量 $\hat m$，方向更稳。两者都是对角自适应，不是牛顿法。
- **loss 突然 NaN？** 查 $\varepsilon$、混合精度下 $v$ 下溢、以及 grad clip；不是先改 $\beta$。bf16 下 $v$ 建议维持 fp32 主副本。
- **AdamW 和 L2 正则是一回事吗？** 不是。L2 进梯度再被 $\sqrt{v}$ 缩放；AdamW 的 decay 不进自适应分母，这正是拆开的原因。
