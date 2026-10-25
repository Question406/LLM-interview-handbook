---
id: sys-rl-group-n
section: systems
order: 31
level: S
title: GRPO 的组大小 $n$ 为什么必须大于 1？太大或太小会怎样？
quick: "GRPO 的优势来自同题 $n$ 条回答的相对奖励；$n=1$ 时分子恒为 0，提供不了更新方向。太小（2 到 4）容易全对或全错，太大则 rollout 和 KV 成本增加，数学题常见 8 到 16。选值时先看非零优势组的比例，再对照长度尾部和实际耗时。"
tags:
  - GRPO
  - Rollout
  - LLM RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: veRL GRPO docs
    url: https://verl.readthedocs.io/en/latest/algo/grpo.html
    type: primary
---

GRPO 要对同一道题采多条回答，用组内奖励比较来确定更新方向，所以 $n$ 必须大于 1。比如整组全对或全错时，没有哪条比其他条更好，优势就会变成 0。GRPO 不训 Critic，baseline 来自同一输入提示的平均奖励；`rollout.n` 控制每题对比几条，global batch 控制一步更新几道题，这两个参数要分开调。veRL 文档也要求 $n$ 大于 1。增大 $n$ 会让 decode 和 KV 成本近似线性增加，换取更可靠的组内信号。

## 为什么 $n$ 必须大于 1

对 输入提示（prompt） $q$ 采 $n$ 条回复，标量奖励 $r_1,\ldots,r_n$，组内优势是相对量：

$$
\hat A_i = \frac{r_i - \mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

没有 Critic 的 $V(s)$，就只能靠组内均值当 baseline。$n=1$ 时 $\mathrm{mean}(r)=r_1$，分子为 0，优势恒为 0（或实现里直接除零 / 跳过）。梯度没有方向：答对了不知道相对谁好，答错了也不知道相对谁差。这里是估计器本身没有可用的组内对照。PPO 可以 $n=1$，因为它另有 $V_\psi(s)$ 提供 baseline，所以两套算法里的 `rollout.n` 不能照搬。

相对信号还有一层含义：同一题上「比组平均好」才加概率，「比组平均差」才压。跨题的绝对分不可比（有的题天生容易），所以必须 **先分组再减均值**。把不同一输入提示 的奖励混在一起做 baseline，题难度会泄漏进优势，难的题永远像负例。有的代码在 $n=1$ 时把 $\hat A$ 设成 $r-\bar r_{\mathrm{batch}}$，看起来能跑，数学上已经换了估计器。我会主动说：定义域是 $n\ge 2$，没有组内对照就没有 GRPO 的 advantage。

## 按有效组比例和耗时选大小

$n=2$ 到 $4$ 时组均值很噪，$\hat A$ 乱跳。更致命的是 **整组全对或全错**：$\mathrm{std}(r)=0$，$\hat A=0$，这步白算。字节那道长尾题就是这个，见 `byte-grpo-rollout-tail-gpu`。题很难、pass@1 很低时，小 $n$ 几乎采不到正例，等于没学；题太简单则整组满分，同样零信息。DAPO 动态采样专门丢掉这些零方差组，见 `slime-dynamic-partial`。温度不够、解码太贪心，也会把有效 $n$ 变成 1（$n$ 条几乎相同）。

每步轨迹数 $= \text{prompt batch}\times n$，KV 和生成时间近似线性涨，大量时间花在 rollout 上，见 `infra-rl-mfu-6nd`。边际信息很快饱和：已经有几条对、几条错，再翻倍对优势 **方向** 帮助不大，只是把组均值估得更稳。组一大，最长那条更拖尾，continuous batching 也只能部分缓解。过大时组内奖励挤在一个窄区间，标准化后 $\hat A$ 变小，相对信号被摊薄，看起来像「采得越多学得越慢」。

数学题常用 8 到 16，但我会先查温度和题目难度，再按非零优势组占比选值。从 8 增到 16 可能多采到正例，从 16 增到 64 则常得到重复的对错模式，同时 decode 耗时近似线性增长，最长回复还会拖住整组，见 `byte-grpo-rollout-tail-gpu`。组均值的方差按 $1/n$ 降，生成成本却按 $n$ 升，因此要对照非零组比例、平均长度和一步耗时，找收益开始变小的位置。DAPO 可以 over-sample 后丢掉零方差组，名义 $n$ 不必一味增大，见 `slime-dynamic-partial`。

调参时一次只改一个量：$n$ 管每题的对照条数，`train_batch_size` 管一步的题数，动态采样管零方差组是否丢掉重采。有效组不足时先调温度、难度和 $n$ 或 DAPO filter；有效组够了但梯度噪声大，再增加题数；主要等最长回复时，先处理长度尾部。组过大时，相似样本会挤在狭窄的奖励区间，标准化后的 $\hat A$ 可能变小，所以还要观察组内 $r$ 的分布。

## 追问

**$n=1$ 改成减一个滑动平均 baseline 行不行？**
那已经不是 GRPO，是在手搓 value-free 的全局 baseline，跨题难度会混进优势。能训，但不是这道题的估计器。定义域是 $n\ge 2$。
**$n$ 和 `train_batch_size` 哪个先加？**
有效组比例低先加 $n$ 或降难度、开 DAPO 滤零方差；有效组已经够、更新方差大，再加题数。不要两个一起拧，也不要先加学习率。
**组内要不要去重？**
重复回复会让有效 $n$ 下降，等价于更小的组，甚至退化成 $n=1$。温度、nucleus、是否允许相同 completion 都要看日志。
**太大能不能靠动态 batch 救？**
能缓解 KV，救不了「相对信号已经饱和」。组内 $r$ 挤在窄区间，标准化后 $\hat A$ 变小。先看非零组比例和平均长度。
**PPO 为什么可以 $n=1$？**
因为有 Critic 提供 $V(s)$ 当 baseline。GRPO 故意不训 value，才必须用组内均值。两套算法不要混着调同一个 `rollout.n`。
**从 16 加到 64 通常发生什么？**
实际耗时按 decode 线性涨，最长尾更明显，边际上只是把组均值估得更稳，优势方向帮助不大。数学题常见拐点在 8 到 16。
**整组满分是不是说明模型已经学会了？**
对这题而言是零信息：$\hat A=0$，这步白算。要降温难度或开动态采样丢掉零方差组，而不是加学习率。
