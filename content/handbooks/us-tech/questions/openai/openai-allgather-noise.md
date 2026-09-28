---
id: openai-allgather-noise
section: openai
order: 2
level: S
title: OpenAI：noisy 链路上实现 all_gather，轮数 bound 怎么推？
quick: >-
  先写正确的 ring / recursive all_gather。通道有噪声时，把「精确恢复任意 bit」改成「把 float 恢复到误差
  $\varepsilon$ 内」。naive 重复码给出一个太松的轮数；改进点是 IEEE float 只有有限位，有效信息量约
  $\log(\mathrm{range}/\varepsilon)$，不是无限精度实数。
tags:
  - OpenAI
  - Distributed
  - Information Theory
  - all_gather
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Experience (2025)
    url: https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2
    type: candidate-first-hand
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer
- 轮次：Coding + ML stats（候选人称为整个 loop 最难一轮）
- 来源：Exponent 2025 报告
- 题面大意：实现多节点 all_gather；通信有噪声时，推导达到目标精度需要多少轮；再改进，因为 naive 上界太慢。关键观察是在传 float，不是任意实数。

这块容易写成「再 all_gather 一次就行」或直接背集合通信复杂度 $2(N-1)M/N$。OpenAI 把集合通信当载体，考的是噪声信道上你要传多少信息。提示很少，需要自己把问题收成信息论。

## 第一部分：先写对无噪声 all_gather

$N$ 卡，每卡有一块 $M/N$ 的数据，最后每卡都要完整 $M$。Ring all_gather：$N-1$ 步，每步每卡发自己现有的一块、收一块，带宽项约 $(N-1)/N \cdot M$。Recursive doubling 在 $N$ 为 2 的幂时延迟更好。白板写出 send/recv 顺序和最终每卡内存布局，不要只说 NCCL 原语名。

和 all_reduce 的差别要主动说：all_reduce 是归约成一份再广播/反散；all_gather 是拼接。训练里 Tensor Parallel 的列并行、MoE token 分发，都更接近 gather 而不是 reduce。

## 第二部分：噪声下的轮数

通道每次传输会翻 bit 或加噪声。目标从「bit 精确」改成「估计误差 $<\varepsilon$」。

最朴素：同一 payload 重复 $R$ 次取多数。对翻转概率 $p$ 的 BSC，Chernoff / Hoeffding 给出

$$
R = \Theta\!\left(\frac{1}{(1-2p)^2}\log\frac{b}{\delta}\right)
$$

才能让 $b$ 个 bit 整体失败概率 $<\delta$。$b$ 如果按「任意实数无限精度」来取，这个界会大到不能用。这就是面试官说 naive 上界太高、太慢的原因。

## 第三部分：利用 float

IEEE-754 二进制32 只有 32 bit，其中有效精度大约 24 bit mantissa。目标是 $| \hat x - x | < \varepsilon$，不是 bit-exact 拷贝。把值域量化成 $K \approx \mathrm{range}/\varepsilon$ 个箱子，只需传 $\lceil \log_2 K \rceil$ bit。$\varepsilon=10^{-3}$、值域 $[0,1]$ 大约 10 bit，不是 32 bit 全可靠恢复。

更好的算法：

- 先传指数 / 数量级（MSB），再按剩余误差补 mantissa。
- 或者当成模拟值：重复观测做平均，方差按 $1/R$ 降，轮数跟 $\sigma^2/\varepsilon^2$ 走，仍然远小于「无限精度纠错」。
- 若噪声是加性高斯而不是 bit flip，直接量化 + 容量公式 $C=\frac12\log(1+\mathrm{SNR})$ 估最少传输次数。

集合通信的步数由拓扑决定；每步要重复多少次由信道容量和精度 $\varepsilon$ 决定。把 float 当成任意实数，会把第二项高估一个数量级。

## 追问

- **all_reduce 噪声怎么处理？** 先局部 reduce 再广播，误差会沿树放大。应用层通常用 fp32 accumulate 或误差补偿，而不是对 32 bit 做重型 ECC。
- **和梯度压缩的关系？** 同一件事：通信的是有精度预算的浮点，不是无损文件。
- **NCCL 会帮你纠错吗？** 一般假设链路可靠（RoCE/InfiniBand CRC）。这题是把信道故意弄脏，看你能不能改模型，不是让你调 NCCL 开关。
