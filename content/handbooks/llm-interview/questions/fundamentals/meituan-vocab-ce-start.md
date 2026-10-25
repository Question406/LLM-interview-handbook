---
id: meituan-vocab-ce-start
section: fundamentals
order: 180
level: A
title: 美团秋招二面：10 万词表时，交叉熵起步大概是多少？
quick: "随机初始化时预测近似均匀，交叉熵约等于 $\\log V$：$V=10^5$ 时 $\\ln(10^5)\\approx 11.5$ nats，换成 $\\log_2$ 约 $16.6$ bit。正常训练会明显低于这个数；长期贴着它，说明没在学，或者把 pad / 忽略位算进了平均。"
tags:
  - Meituan
  - Cross Entropy
  - Vocabulary
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法二面-秋招面经
    url: https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：“LLM的损失函数是什么？给你一个10w的词表，计算出事的损失值”

起步大约是 $\ln(10^5)\approx 11.5$ nat，按 $\log_2$ 算约 $16.6$ bit。随机初始化时各维 logits 差不多，模型对每个词的概率都接近 $1/V$，交叉熵就退化成均匀分布的熵 $\log V$。这题问的是数量级，先确认单位再报数。

原帖的「出事 / 起步」问的是随机初始化那一刻，别答成某个 checkpoint 的真实 loss，也别把 bit 和 nat 混着报。答案不是 0，也不是训练后期的 2.x。同面的 SwiGLU / RMSNorm 是公式题，这题是数量级题。

## 交叉熵怎么退化成 $\log V$

LLM 的主损失是 next-token 交叉熵，实现上是 `log_softmax` + NLL。标签 one-hot 为 $y$，模型 $q=\mathrm{softmax}(z)$：

$$
\ell=-\log q(y).
$$

交叉熵与 KL 的关系是

$$
\mathrm{CE}(p,q)=H(p)+D_{\mathrm{KL}}(p\|q).
$$

one-hot 的 $H(p)=0$，所以 $\mathrm{CE}=-\log q_y$，正向 KL 几乎就等于这一项。随机初始化时 $q(y)\approx 1/V$，于是

$$
\mathbb{E}[\ell]\approx -\log\frac1V=\log V=H(u).
$$

$V=10^5$ 时 $\ln(10^5)=5\ln 10\approx 11.51$ nat；$\log_2(10^5)\approx 16.6$ bit。PyTorch 默认用 nat。白板上的顺序是：先写 $\ell=-\log q_y$，再说均匀时 $\Rightarrow\log V$，代入得 $\approx 11.5$，最后补一句这是起步，不是目标。

## 曲线贴着 $11.5$ 不动说明什么

正常训练应该在几十到几百 step 内明显低于 $\log V$。前几个 step 从 $\approx\log V$ 往下掉，是 embedding 和输出头开始把类别拉开；掉到 3 到 4 还很常见，因为自然语言本身有剩余熵，不会逼近 0。长期贴着 11 才是事故，这时「模型太弱」一般解释不了，原因多半在三处：一是没在学，学习率、数据管线或梯度被掐死了；二是平均方式错了，把 pad / `ignore_index` 算进分子或分母，有效 token 的损失被稀释，曲线看起来「一直很高」或「假低」；三是单位说错，把 $16.6$ bit 当成 nat，或者把 $\log_{10}$ 报成 $\ln$。

平均方式最好在白板上补出来。Causal LM 用 `logits[:, :-1]` 对 `labels[:, 1:]`，pad 位 `ignore_index=-100`。正确的平均是有效 token 上的均值，分母是 $\sum_i\mathbf{1}[y_i\neq\mathrm{ignore}]$，用 batch 里的格子数就错了。如果把 pad 的 NLL 算进去再除以 $N$，曲线会「假高」或「假低」，取决于 pad 位置的 logits 乱不乱。

label smoothing 把目标从 one-hot 改成 $q=(1-\varepsilon)e_y+\varepsilon/V$，地板从 $0$ 抬到大约 $-(1-\varepsilon)\log(1-\varepsilon)-\varepsilon\log(\varepsilon/V)$ 那一截，观测值会略高于「理想 one-hot CE」。别把平滑后的偏高当成没训练。

被追问「你怎么知道 11.5 算对了」时，先对齐四件事：词表 $V$、单位是 nat 还是 bit、要不要算 smoothing、分母是不是有效 token。这四件对齐了，数量级才有意义。如果同面已经手写过交叉熵损失（CE），可以主动说一句：实现必须用 `logsumexp`，禁止先 softmax 再取 $\log$，数值下溢会把起步 loss 打成 Inf，那和「均匀熵」是两回事。也别把某个开源 checkpoint 的 1.8 当成这道题的标准答案，那是训完的数，这题问的是随机起步。

## 追问

**为什么起步不是 0？**
随机模型几乎只能以 $1/V$ 的概率猜中，NLL 就是 $-\log(1/V)$。0 只在 $q_y=1$ 时出现，初始化做不到。

**和 KL 差什么？**
one-hot 时 $H(p)=0$，CE 与 $D_{\mathrm{KL}}(p\|q)$ 同值；加了平滑以后差一个与模型无关的熵常数，梯度方向仍由 KL 决定。

**起步就是 0.1 呢？**
多半是 label 全是 ignore，或者 logits 泄漏了答案，或者把已经训过的权重当成了「随机初始化」。

**7 万词表呢？**
$\ln(7\times 10^4)\approx 11.16$。先报 $\log V$ 再代入，别背一个数。换词表等于换均匀熵，和换优化器没关系。

**多模态里视觉 token 也算进 CE 吗？**
只对有标签的文本位置平均，纯视觉前缀通常 mask 掉。否则分母被无标签位稀释，起步数就对不上 $\log V$。
