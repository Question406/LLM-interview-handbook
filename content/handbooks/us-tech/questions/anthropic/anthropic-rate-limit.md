---
id: anthropic-rate-limit
section: anthropic
order: 13
level: A
title: Anthropic：怎么给 API 设计 rate limiter（token 桶 / 滑动窗）？
quick: "请求数和 token 数都要限：令牌桶允许短时突发，滑动窗口更公平但状态更重；分布式用 Redis 原子扣减，故障时 fail closed。"
tags:
  - 完整编程练习
  - Anthropic
  - API
  - Rate limit
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
  - title: Rate limits (Claude API)
    url: https://docs.anthropic.com/en/api/rate-limits
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试原题或官方测试，和 `xai-rate-limiter` 共用同一份程序。Python 3，只用标准库。

### 题面、接口与约束

- `Limiter(user_capacity, user_rate, global_capacity, global_rate)`：每个用户一个令牌桶，平台再共用一个全局桶。四个参数都必须是有限正数，否则抛 `ValueError`。两种桶初始都是满的。
- `Limiter.allow(user, cost, now) -> bool`：按经过的时间给两个桶惰性补充 token（不超过容量），两个桶都够 `cost` 时同时扣款并返回 `True`；任意一个不够就返回 `False`，两个桶都不扣。
- `cost` 是有限正数，`now` 是有限非负数，并且在整个 limiter 上（跨用户）单调不减；违反时抛 `ValueError`。
- 多线程共享同一个实例时，检查和扣款必须是原子的。
- 不排队；每用户配额隔离不等于加权公平调度（见复杂度与追问）。

### 输入输出示例

```text
Limiter(user_capacity=2, user_rate=1, global_capacity=3, global_rate=1)
allow("a", 2, now=0)  -> True    # 用户桶 a: 0，全局: 1
allow("a", 1, now=0)  -> False   # a 的桶不够，全局桶不扣
allow("b", 1, now=0)  -> True    # 全局还剩 1，刚好够
allow("b", 1, now=0)  -> False   # 全局用完
allow("b", 1, now=1)  -> True    # 过了 1 秒，两个桶各补 1
```

### 解题思路与正确性

每个桶只存「余额」和「上次更新时间」。请求到来时先按 $\Delta t \times \text{rate}$ 补充并封顶，再判断够不够，所以不需要后台线程。

两个桶的补充、检查和扣款都在同一把锁里完成，而且只有两个桶都够时才一起扣。如果先扣全局、再发现用户桶不够，就会出现「全局扣了、用户被拒、额度蒸发」。被拒的请求仍然把补充后的余额和时间写回去，只是不扣费，这不影响结果，因为补充只依赖时间差。

时间要求在整个 limiter 上单调，是因为全局桶被所有用户共享：如果允许用户 a 在 `now=5` 之后，用户 b 又用 `now=3` 调用，全局桶的时间就会倒退。

### 完整参考实现（Python 3）

```python
import math
from threading import Lock


class Limiter:
    """每用户令牌桶 + 全局令牌桶，惰性补充；两个桶都够才同时扣款。线程安全。"""

    def __init__(self, user_capacity, user_rate, global_capacity, global_rate):
        params = (user_capacity, user_rate, global_capacity, global_rate)
        if any(not math.isfinite(value) or value <= 0 for value in params):
            raise ValueError(f"capacities and rates must be positive and finite, got {params}")
        self.user_capacity = user_capacity
        self.user_rate = user_rate
        self.global_capacity = global_capacity
        self.global_rate = global_rate
        self.user_buckets = {}         # user -> (tokens, last_refill_time)
        self.global_tokens = global_capacity
        self.last_time = None          # 上一次调用的 now，整个 limiter 共用
        self.lock = Lock()

    def allow(self, user, cost, now):
        """补充两个桶后，两个都够 cost 才扣款并返回 True；否则不扣任何桶，返回 False。"""
        if not math.isfinite(cost) or cost <= 0:
            raise ValueError(f"cost must be positive and finite, got {cost}")
        if not math.isfinite(now) or now < 0:
            raise ValueError(f"now must be non-negative and finite, got {now}")
        with self.lock:
            if self.last_time is not None:
                if now < self.last_time:
                    raise ValueError(f"time went backwards: {now} < {self.last_time}")
                elapsed = now - self.last_time
                self.global_tokens = min(self.global_capacity,
                                         self.global_tokens + elapsed * self.global_rate)
            self.last_time = now
            tokens, last_refill = self.user_buckets.get(user, (self.user_capacity, now))
            tokens = min(self.user_capacity, tokens + (now - last_refill) * self.user_rate)
            accepted = tokens >= cost and self.global_tokens >= cost
            if accepted:
                tokens -= cost
                self.global_tokens -= cost
            self.user_buckets[user] = (tokens, now)
            return accepted
```

### 可执行测试

```python
from concurrent.futures import ThreadPoolExecutor


def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


limiter = Limiter(2, 1, 3, 1)

# 用户桶用完后被拒
assert limiter.allow("a", 2, 0)
assert not limiter.allow("a", 1, 0)

# 被拒的请求没有消耗全局额度，b 还能用掉剩下的 1
assert limiter.allow("b", 1, 0)
assert not limiter.allow("b", 1, 0)

# 时间推进后两个桶都补充
assert limiter.allow("b", 1, 1)

# 补充封顶在容量：空闲很久后也只能用到 user_capacity
assert limiter.allow("a", 2, 100)
assert not limiter.allow("a", 3, 100)

# 时间倒退报错
expect_error(ValueError, limiter.allow, "a", 1, 99)

# 非法参数和非法请求
expect_error(ValueError, Limiter, 0, 1, 1, 1)
expect_error(ValueError, Limiter, 1, float("inf"), 1, 1)
expect_error(ValueError, limiter.allow, "a", 0, 100)
expect_error(ValueError, limiter.allow, "a", 1, float("nan"))

# 全局桶限制所有用户的总和
shared = Limiter(5, 1, 3, 1)
results = [shared.allow(f"user-{i}", 1, 0) for i in range(5)]
assert results == [True, True, True, False, False]

# 并发：100 个线程同时请求，只放行全局容量 7 次
concurrent = Limiter(10, 1, 7, 1)
with ThreadPoolExecutor(8) as pool:
    accepted = sum(pool.map(lambda _: concurrent.allow("u", 1, 0), range(100)))
assert accepted == 7
```

### 复杂度与追问

设用户数为 $U$。每次 `allow` 是 $O(1)$，空间 $O(U)$。

- 追问「一把锁会不会成为瓶颈」：单锁保证单机正确，但所有用户串行。可以把用户桶按 key 分片加锁，全局桶单独用原子操作；分布式时，两个桶的检查和扣款必须放进同一个原子操作（比如一段 Redis Lua 脚本）。
- 追问「这算公平吗」：这段代码只保证每个用户的配额互相隔离。Weighted Fair Queueing 这类加权公平调度需要单独的调度策略，token bucket 不会自动提供。

## 题怎么来的

给 Claude 这类 API 做限流，是 SWE / 基础设施岗的现场设计题，不一定出现在 CodeSignal 上。官方文档把限额拆成请求速率和 token 速率，输入和输出分开算。回答时按这个产品约束来，而不是只写一个 LeetCode 式的计数器。上面的练习覆盖了「每 key 一个桶 + 全局容量」这一层，下面讲产品上还要限什么。

## 要限的是两类资源

一次 `messages` 调用会消耗：

- 1 个请求配额（RPM）；
- 输入 token，包括系统提示、工具定义和多轮历史；
- 输出 token，生成多少事先只能估计。

所以 limiter 的键至少是 `(org_id, api_key, model, dimension)`。免费层、付费层和企业合同各是不同的桶。返回 429 时要带上 `retry-after`，不要只回一句 over limit。

输出 token 在请求开始时是未知的。常见做法是按 `max_tokens` 预扣，预扣不够就直接拒绝；请求结束后按真实用量多退少补。如果不退还，十个请求各按 4k 预扣、实际每个只写 20 token，桶会被这些预扣长期占满。

## Token 桶：对突发友好

状态是当前水位 $t$、容量 $B$、装填速率 $r$（单位 / 秒）和上次更新时间。单个桶的写法：

```python
class TokenBucket:
    """单个懒填充令牌桶：容量 burst，每秒补 rate；调用方传入当前时间。"""

    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_ts = 0.0

    def allow(self, now, n=1):
        self.tokens = min(self.burst, self.tokens + (now - self.last_ts) * self.rate)
        self.last_ts = now
        if self.tokens < n:
            return False
        self.tokens -= n
        return True
```

时间和内存都是 $O(1)$。它的特性是：空闲一段时间后可以一次打满 $B$，之后被速率 $r$ 限住，适合「交互时有突发、平均用量更低」的聊天场景。$B$ 太大，一个客户可能占用过多资源、影响其他客户；$B$ 太小，多轮 agent 一个回合里有十次工具调用时，就会频繁触发限流。

Anthropic 文档里的 token 限额就是这种桶：允许短时间高于平均速率，长期不超过速率。面试时要说出 burst 和 sustained 是两个独立的旋钮。

## 滑动窗：更公平，状态更重

固定窗口（每分钟清零）会在整分处出现双倍突发：第 59 秒打满一次，第 0 秒再打满一次。滑动窗口记录过去 $W$ 秒内的事件：

- 精确版：每个请求存一个时间戳，查询时丢掉 $now-W$ 之前的再求和。内存 $O(Q)$，$Q$ 是窗口内的请求数。
- 近似版：把窗口切成 $k$ 个槽，当前槽累加，查询时对所有槽求和。内存 $O(k)$，误差大约是一个槽。

token 用量用滑动窗口更公平，不会因为整分刷新而放进两倍的量；但实现成本更高，尤其 token 级事件比请求级密得多。生产上常见的组合是请求走滑动窗口，token 走令牌桶。请求的突发伤的是调度，token 的突发伤的是 GPU。

## 分布式和失败模式

多台机器必须共享状态。Redis 的 `INCR` 加 TTL 是最简单的固定窗口；令牌桶要用 Lua 脚本把「读、加、写」做成原子操作。不要先 GET 再 SET，否则并发请求可能重复使用同一份额度。练习里两个桶「都够才一起扣」的要求，放到 Redis 上也要在同一段脚本里完成。

失败策略：Redis 超时时应该拒绝请求（fail closed），而不是放行。限流器一挂就放行，等于给 GPU 账单开了闸。可以降级到本机进程内的桶，但额度要按机器数平分，避免每台机器都给一份全额。

这和 `anthropic-crawler-oa` 里的「礼貌」是同一种结构：每个 host 或每个 key 一条时间线。爬虫的 `next_ok` 是相邻请求的最小间隔，API 的桶是平均速率加突发。面试时把两道题连起来讲，会显得像在同一家公司真做过系统。

## 追问

- **谁的配额被扣？** 工具调用的中间轮次也是请求。agent 循环要把内部轮次算到同一个 key 上，否则用户一次会话就可能耗尽配额。
- **怎么做公平？** 纯令牌桶是先到先得。多租户要加权，比如企业合同给更大的 $r$。为了避免一个 key 占满模型槽位，再单独限制每个 key 的最大并发。
- **429 之后怎么重试？** 客户端用指数退避加抖动，服务端给出明确的等待时间。不要让 SDK 立刻无脑重放非幂等请求，见 `anthropic-tool-use`。
- **按 token 限还是按美元限？** 内部可以换成美元桶，对外仍然暴露 RPM / TPM，方便用户理解。计价变化时，不应该让用户重写自己的限流逻辑。

## 相关题

- [[xai-rate-limiter]]：和本题共用同一份两层令牌桶程序；xAI 那题正文更细讲懒填充和多租户两层桶怎么一起扣。
- [[p3a-xai-distributed-token-bucket-limiter]]：本题「分布式」一节的编码版，多实例共享限额时补充、检查、扣减必须在共享存储里原子执行。
- [[msft-azure-tpm]]：站在调用方看 TPM/RPM 配额，429 之后产品层怎么排队、退避和降级。
- [[design-chat-serving]]：把限流放进整套对话服务里，和优先级队列、前缀缓存、KV 准入一起设计。
