---
id: xai-rate-limiter
section: xai
order: 3
level: A
title: xAI coding：API rate limiter，多租户公平和突发
quick: >-
  先落地懒填充 token bucket：状态是余额和时间戳，请求来了再按间隔补 token，不要后台线程。多租户是每
  key 一个桶再加全局容量；突发是桶深，公平是加权借还，不是把 burst 设成无限。
tags:
  - xAI
  - Rate Limiter
  - Token Bucket
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Get a Job at xAI — Interview Process and Top Questions
    url: https://www.tryexponent.com/blog/xai-interview-process
    type: secondary
  - title: xAI Software Engineer Interview Guide
    url: https://www.tryexponent.com/guides/xai-software-engineer-interview
    type: secondary
  - title: xAI Interview Questions from Candidate Reports
    url: https://aceoffer.app/interviews/xai
    type: secondary
  - title: Practice xAI Mock Interviews
    url: https://igotanoffer.com/en/mock-interviews/company/xai
    type: secondary
---

## 题怎么来的

公开汇总里这题以 coding 和 design 两种形态出现：先实现单 URL / 单 key 的限流，再加复合规则、按 payload 计费、多租户配额。Exponent 把 rate limiter 和 KV 事务并列成 xAI 高频应用题；AceOffer 写过 **lazy-refill token bucket**。不是某一场能引用 experience id 的逐字题，按「能跑的类 + 公平和突发说得清」准备。和 `xai-kv-txn` 同一口味：共享状态、时钟、并发，不是 LeetCode 花样。

## 先写懒填充桶，再谈分布式

生产不会每毫秒给所有用户加 token。每个 key 存 `(tokens, last_ts)`。来请求时：

$$
t \leftarrow \min(\mathrm{burst},\; t + r\cdot\Delta),\qquad
\text{若 } t \ge c \text{ 则扣 } c \text{，否则拒绝}.
$$

$r$ 是稳态速率，$c$ 是本次代价（默认 1，payload 规则里可以是字节），burst 是桶深。时钟用注入的 `now`，单测才能复现。

```python
class TokenBucket:
    def __init__(self, rate, burst, now):
        self.rate, self.burst, self.now = rate, burst, now
        self.tokens, self.ts = burst, now()

    def allow(self, cost=1) -> bool:
        t = self.now()
        elapsed = max(0.0, t - self.ts)
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.ts = t
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True
```

错法：另起线程 refill（OA 里难测，还会和请求抢状态）；用固定窗口（边界可以双倍突发）；漏桶只平滑、不会「先攒再爆」，和产品说的 burst 对不上。滑动窗口更准、状态更重，当 follow-up。

## 多租户：两层桶，不是一把全局锁

API 网关常见两层：平台总 QPS，以及每个 consumer / API key 的配额。两个桶都过才放行；先扣哪一层要规定，失败要回滚，否则会「全局扣了、用户被拒、额度蒸发」。复合规则（URL A 和 B 共用一笔预算、同时又各有上限）用规则表：一次请求列出命中的 bucket id，按 id 排序加锁，避免 AB/BA 死锁。这和 `xai-kv-txn` 的按 key 排序是同一手。

公平不是平均。大客户权重大，但不允许它把小客户的突发窗口吃光。我会讲：

- **加权公平：** 每个租户一个桶，全局还有一个令牌或队列。权重 $w_i$ 决定借还速度，不是决定 burst 无限。
- **突发：** burst 只覆盖短尖峰（重试风暴、页面刷新）。稳态仍是 $r$。把 burst 设成「一分钟配额」等于没限流。
- **排队 vs 拒绝：** 同步 API 通常 429 加 `Retry-After`；内部推理网关可以对可延迟请求排队，但对齐的是租户权重，不是 FIFO 让大象流堵死。

并发：单机用 per-key 锁或把 key 哈希到 shard；多机把桶放缓存，用事务做「读-补-扣」原子。不要先 get 再 set，那是 lost update，和 BankAccount race 同构。分布式时钟用逻辑时间或接受略松，强同步时钟不是这轮重点。

评委若把限流接到 Grok API：计费单位从请求变成 token 也不改骨架，只改 `cost`。别一上来画 Kafka。缓存层见 `xai-lru-cache`。

## 追问

- **为什么面试官会暗示 lazy refill？** 不用定时器，状态小，单测只推进 `now`。热路径上补 token 是 $O(1)$。
- **突然 10 倍流量？** burst 吃掉尖峰，然后 429。公平队列保证小租户仍有 $w_i$ 份额。不要靠再加大 burst。
- **和推理 batching 的关系？** 限流在入口保护 GPU 队列；batching 在内部提高利用率。入口公平不等于 decode 公平，后者还要看 KV 占位和抢占，见 `xai-grok-moe`。
- **固定窗口能不能过？** 能写对计数，但边界突发是 $2r$。要自己点出来，再换成桶。
