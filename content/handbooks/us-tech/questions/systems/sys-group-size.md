---
id: sys-group-size
section: systems
order: 62
level: A
title: 系统：GRPO 的组大小 G，显存和方差怎么一起看？
quick: >-
  GRPO 对每条 prompt sampling G 个回答，用组内奖励计算相对优势。G 太小更容易全对或全错、缺少区分信号；G 增大能降低方差，但
  KV、打分和训练样本数都会增加。先算完整组的优势，再按 microbatch 拆训练，不能用半组估计均值。
tags:
  - Post-train
  - GRPO
  - Batch
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: verl GRPO
    url: 'https://verl.readthedocs.io/en/latest/algo/grpo.html'
    type: primary
  - title: DeepSeekMath
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

调大 GRPO 的组大小 G，是用更多 sampling 和显存换更稳定的组内比较。比如 G 为 2 时，两条回答都错就没有区分信号；到 8 或 16，组里更容易同时出现对和错。DeepSeekMath 用组内相对优势定义 GRPO，verl 用 `rollout.n` 配 G；batch 三层数见 `sys-grad-accum`。

prompt 数是 $B$，回答条数是 $B \cdot G$。生成的 KV、打分次数、训练前向的行数都乘 G。优化器若按 prompt 的 mini-batch 更新，更新次数不必跟着 G 变；若有人把 mini-batch 当成回答条数，G 一变，一步里的更新次数就变了。

G 为 2 时，组内标准差经常是 0 或极大。全对全错的组没有优势。G 到 8 或 16，组内才比较容易同时有对和错。继续增大主要是进一步降低方差，KV 和时间则线性增加。

一组的 G 条要在同一次优势计算里。micro batch 装不下整组，就先把整组的奖励算完、优势写回每条样本，再拆开做前向。不要在半组上求均值。

```python
import torch


def group_advantage(rewards, group_size):
    # rewards: [B * G], prompts are contiguous
    r = rewards.view(-1, group_size)
    mean = r.mean(dim=1, keepdim=True)
    std = r.std(dim=1, keepdim=True, correction=0)
    centered = r - mean
    adv = torch.where(std < 1e-8, torch.zeros_like(r), centered / std)
    return adv.reshape(-1)
```

## 追问

**显存不够，减 G 还是减回答长度？**
长度进 attention 的平方和 KV 的线性。G 进条数。长回答先截断并在奖励里记一笔，通常比把 G 收到 2 更少伤害优势。G 收到 2 以下，组内 standardization 没有意义。

## 相关题

- [[align-grpo]]：口述 GRPO 为什么用组均值代替 critic，$G>1$ 和全对/全错组的问题在那里从算法侧讲。
- [[coding-rloo-advantage]]：RLOO 用其余 $G-1$ 条当 baseline，$G=2$ 时退化成两条互减，$G$ 的取舍同样适用。
