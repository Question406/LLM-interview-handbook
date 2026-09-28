---
id: sys-verifier
section: systems
order: 53
level: A
title: 系统：可验证奖励不在 GPU 上，一步要怎么等它？
quick: >-
  单测、编译、检索是否命中，跑在 CPU 沙箱里，不占训练卡的算力，但占步时间。
  生成一结束就送去判，不要等整组 GPU 都闲着再串行跑测试。超时和失败要变成一个有限的奖励，不能把训练卡挂死。
tags:
  - Post-train
  - RLVR
  - Reward
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: DeepSeekMath, 可验证奖励上的 GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

RLVR 的奖励不是奖励模型的一次前向。数学对错、单测通过，是外部环境。这道按这个分工拟的。沙箱本身见 `sys-sandbox`。

## 和 GPU 步怎么接

生成在 GPU 上结束一条，就可以把这段程序或答案送去判。同一组里其他回答还在生成时，先完成的已经在跑测试。等最慢的一条生成完再串行开测，步时间是「最长生成 + 全部测试之和」。重叠之后，大约是「最长生成」和「测试队列」里较慢的那个。

测试返回一个标量。失败、超时、编译错误都要映射成一个低奖励，组里其他回答仍可比较。一条测试没返回，整组优势都算不出来，这张卡会卡住后面的更新。

奖励模型才需要 GPU。它是另一份前向，可以放在单独的卡上，和生成、训练都错开。不要把「有奖励」都说成要再加载一个 70B。

## 代码

```python
def score_as_ready(done_queue, pool, reward_of):
    pending = []
    while True:
        sample = done_queue.get()
        if sample is None:
            break
        pending.append(pool.submit(reward_of, sample))
    return [f.result(timeout=30) for f in pending]
```

## 追问

**奖励很稀疏，全是 0 怎么办？** 这是数据问题，不是再加一张卡。一组里全 0，优势是 0，这一组没有更新。要换更合适的题目，或加上只有格式对错的部分分，权重要远小于真正的对错。
