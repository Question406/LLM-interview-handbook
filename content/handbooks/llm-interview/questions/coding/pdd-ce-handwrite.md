---
id: pdd-ce-handwrite
section: coding
order: 181
level: A
title: 拼多多应用开发：如何手写 cross entropy，数值上要防什么？
quick: >-
  对 logits 做 log-softmax，再按目标 token gather 取负。先 softmax 再 $\log$ 会下溢，所以用
  `logsumexp` 或 `log_softmax`；padding 位置 mask 掉，再按有效 token 平均。
tags:
  - PDD
  - Cross Entropy
  - Coding
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 拼多多大模型应用开发一面凉经
    url: 'https://www.nowcoder.com/feed/main/detail/f87fcee060ea404ba99a20245f746e60'
    type: candidate-first-hand
---

## 题目描述

实现 `cross_entropy(logits,target,ignore_index=-100)`，计算多分类任务的平均 cross entropy，不直接调用封装好的 cross entropy loss。面经只披露“手写 cross entropy”，以下接口为手册重构练习约定。

### 接口、输入与输出要求

`logits` 是有限浮点 PyTorch 张量 `[N,V]`，`target` 是同设备的整数张量 `[N]`。N、V 为正；非忽略标签在 `[0,V)`，本练习的 `ignore_index` 是负整数，默认 -100。至少存在一条非忽略样本。

对每条非忽略样本 i，损失定义为 `-log(softmax(logits[i])[target[i]])`；返回这些损失的算术平均值，结果为可 backpropagation 的标量张量。忽略样本不计入分子或分母。本接口的标签已经对齐，不做语言模型的时间移位。要求较大绝对值的有限 logits 下仍得到数值稳定的结果。

### 示例

```text
输入：logits=[[0,0],[100,-100]]，target=[0,-100]
输出：约0.693147（log(2)）

输入：logits=[[1000,1000]]，target=[1]
输出：约0.693147
```

## 解题思路与参考答案

cross entropy 要在 log 域里算：每行 logits 先减最大值，再算 `logsumexp`，loss 就是 $-z_y+\mathrm{logsumexp}(z)$，pad 位置 mask 掉之后按有效 token 平均。

这是拼多多大模型应用开发一面的题，来自牛客候选人原帖，可信度 A，面试时间原帖没写，原话是**“手写 cross entropy”**。最常见的错是先 `softmax` 再 `log`：概率下溢成 0，$log0\to-\infty$。所以一定要在 log 域里做，减行最大值再 `logsumexp`。同一面的 Attention 见 `pdd-attention-handwrite`。序列任务还要用 `ignore_index` 丢掉 pad，见 `baidu-qwen2-sft-implementation`。

## 公式：NLL = $-z_y + \mathrm{logsumexp}(z)$

对 logits $z\in\mathbb{R}^{V}$ 与类别 $y$：

$$
\ell=-z_y+\mathrm{logsumexp}(z),\qquad
\mathrm{logsumexp}(z)=\max_j z_j+\log\sum_j e^{z_j-\max z}.
$$

减 max 不改变 softmax，但能让指数落在 $(0,1]$。label smoothing 时目标不再是 one-hot，变成对平滑分布的 cross entropy。均匀初始化时 $\ell\approx\log V$，十万 vocabulary 约 $11.5$，可以拿来判断初始 loss 离不离谱。

```python
import torch


def cross_entropy(logits, target, ignore_index=-100):
    # logits: [N, V], target: [N]
    z = logits - logits.max(dim=-1, keepdim=True).values
    logp = z - z.exp().sum(dim=-1, keepdim=True).log()
    safe = target.clamp(min=0)
    nll = -logp.gather(1, safe.unsqueeze(1)).squeeze(1)
    mask = target != ignore_index
    return nll[mask].mean()
```

`gather` 前把 ignore 位置 clamp 一下是为了不越界，平均只在 `mask` 上做。pad 位置算完乘 0、却还除以 $N$ 是错的，分母应该是有效 token 数。

## 序列 LM：shift 与平均方式

Causal LM 用 `logits[:, :-1]` 对 `labels[:, 1:]`。HF 的 `labels=` 已经在内部 shift 了，手写时只做一次。平均可以按 token 也可以按序列，按 token 时长句会占主导；GRPO/SFT 论文对「按序列还是按 token」很敏感，见 `baidu-grpo-loss-agg`。面试先写 token 平均加 ignore pad，再口头说另一种。

fp16 下 `exp` 仍可能溢出，减过 max 之后通常安全，极端值可以升 fp32。`F.softmax` 之后再 `log` 的写法不要用。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两类 logits 全零时，单样本 cross entropy 应是 log(2)。把被忽略样本设成强烈偏向错误类别，仍不应影响 loss；全被忽略的输入需要另行约定返回值，当前 mean 会得到 NaN。

```python
import math

logits = torch.tensor([[0.0, 0.0], [100.0, -100.0]])
target = torch.tensor([0, -100])
torch.testing.assert_close(cross_entropy(logits, target), torch.tensor(math.log(2)))
torch.testing.assert_close(
    cross_entropy(logits[:1] + 1000, target[:1]), torch.tensor(math.log(2))
)
print("simple tests passed")
```

## 追问

**起步 loss 多少算正常？**
均匀分布约 $\log V$，7 万 vocabulary $\approx 11.2$。如果一开始就是 0.1，多半是 label 全是 ignore，或者 logits 泄漏了答案。

**为什么要 clamp target？**
ignore 的下标不能进 `gather`；clamp 之后再靠 mask 把这些 NLL 丢掉。

**label smoothing 怎么算？**
$q=(1-\varepsilon)e_y+\varepsilon/V$，loss 是 $-q\cdot\log\pi$，要对整个分布求和，只取 $y$ 那一列就错了。

**和 KL 什么关系？**
对 one-hot 的 cross entropy loss（CE）等于相对均匀基线的 KL 差一个常数。平滑之后就是对 $q$ 的 CE。

**分母用 batch 还是有效 token？**
有效 token。用 batch 的话，pad 多的 batch，loss 会被人为缩小。
