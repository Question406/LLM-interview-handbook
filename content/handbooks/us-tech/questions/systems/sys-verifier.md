---
id: sys-verifier
section: systems
order: 53
level: A
title: 系统：可验证奖励不在 GPU 上，一步要怎么等它？
quick: "外部 verifier 用 CPU 沙箱检查单测、编译或答案，仍会占训练步时间。我会让每条回答生成完就送去测试，与其余 GPU 生成重叠；超时、编译错误和失败都要返回有限的低奖励，避免整组更新一直等待。"
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

每条回答生成完就送到 CPU 沙箱验证，让测试与其余回答的 GPU 生成重叠。比如同组里一条程序已经写完，其他回答还在生成，就可以先编译和跑它的单测。RLVR 中数学核对、单测等可验证奖励来自外部环境，这道题就是按这项分工拟的。

生成在 GPU 上结束一条，就可以把这段程序或答案送去判。同一组里其他回答还在生成时，先完成的已经在跑测试。等最慢的一条生成完再串行开测，步时间是「最长生成 + 全部测试之和」。重叠之后，大约是「最长生成」和「测试队列」里较慢的那个。

测试返回一个标量。失败、超时、编译错误都要映射成一个低奖励，组里其他回答仍可比较。一条测试没返回，整组优势都算不出来，这张卡会卡住后面的更新。

如果用学习到的 reward model，则是另一份需要 GPU 的前向，可以放到单独卡上，与生成和训练错开。外部 verifier 不需要因此再加载一个 70B。

下面的队列把已完成样本送入测试池，并为等待设置超时：

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

代码中的超时异常还需要调用方按前述约定转换成有限的低奖励，避免一条测试阻塞整组优势计算。沙箱实现见 `sys-sandbox`。

## 追问

**奖励很稀疏，全是 0 怎么办？**
换更合适的题目，或加权重远小于最终对错的格式部分分。一组全 0 时，优势也是 0，不会提供更新信号；加训练卡不能解决信号缺失。
