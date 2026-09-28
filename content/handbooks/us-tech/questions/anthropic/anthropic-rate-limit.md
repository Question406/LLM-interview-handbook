---
id: anthropic-rate-limit
section: anthropic
order: 13
level: A
title: Anthropic：怎么给 API 设计 rate limiter（token 桶 / 滑动窗）？
quick: >-
  请求数和 token 数都要限。Token 桶管突发：容量 $B$、速率 $r$，允许短时冲高。滑动窗管「过去
  $W$ 秒真用了多少」，更公平但要存时间戳。分布式用 Redis 原子扣，失败要 fail closed。
tags:
  - Anthropic
  - API
  - Rate limit
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
  - title: Rate limits (Claude API)
    url: https://docs.anthropic.com/en/api/rate-limits
    type: primary
---

给 Claude 这类 API 做限流，是 SWE / 基础设施岗的现场设计题，不一定出现在 CodeSignal。官方文档把限额拆成请求速率和 token 速率（输入、输出分开）。我会按这个产品约束答，而不是只写 LeetCode 计数器。

## 要限的是两类资源

一次 `messages` 调用消耗：

- 1 个请求配额（RPM）；
- 输入 token（含系统提示、工具定义、多轮历史）；
- 输出 token（生成多少事先只能估计）。

所以 limiter 的键至少是 `(org_id, api_key, model, dimension)`。免费层、付费层、企业合同是不同桶。429 要带回 `retry-after`，不要只回一句 over limit。

输出 token 在请求开始时未知。常见做法：按 `max_tokens` 预扣，结束后按真实用量多退少补。预扣失败直接拒，避免十个请求同时按 4k 冲进去、实际每个只写 20 token，桶被占死。

## Token 桶：突发友好

状态：当前水位 $t$，容量 $B$，装填速率 $r$（单位 / 秒），上次更新时间。

```python
class TokenBucket:
    def __init__(self, rate, burst):
        self.r, self.B = rate, burst
        self.t, self.ts = burst, 0.0

    def allow(self, now, n=1):
        self.t = min(self.B, self.t + (now - self.ts) * self.r)
        self.ts = now
        if self.t < n:
            return False
        self.t -= n
        return True
```

复杂度 $O(1)$ 内存 $O(1)$。特性：空闲后可以一次打满 $B$，然后被 $r$ 卡住。适合「交互突发、平均更低」的聊天。$B$ 太大，邻居会被一个客户打爆；$B$ 太小，多轮 agent 一回合十次工具调用会抖。

Anthropic 文档里的 token 限额就是桶：允许短时高于平均，长期不超过速率。面试要说出 burst 和 sustained 是两个旋钮。

## 滑动窗：更公平，状态更重

固定窗（每分钟清零）会在整分处出现双倍突发：59 秒打满，0 秒再打满。滑动窗记过去 $W$ 秒的事件：

- 精确：每条请求一个时间戳，查询时丢掉 $now-W$ 之前的，求和。内存 $O(Q)$，$Q$ 是窗内请求数。
- 近似：把窗切成 $k$ 个槽，当前槽累加，查询时对槽求和。内存 $O(k)$，误差约一个槽。

Token 用量用滑动窗更公平：不会因为整分刷新而放进双份。实现成本高，尤其 token 级事件比请求级密。生产常见组合：请求走滑动窗，token 走桶。请求突发伤的是调度；token 突发伤的是 GPU。

## 分布式和失败模式

多机必须共享状态。Redis `INCR` + TTL 做固定窗最简单；桶要用 Lua 把读-加-写打成原子。不要先 GET 再 SET，会超发。

失败策略：Redis 超时是拒请求（fail closed），不是放行。限流器挂了就变成未限流的 GPU 账单。降级可以切到本机进程内桶，但额度要按机器数除，避免每台各给一份全额。

和 `anthropic-crawler-oa` 的礼貌是同一结构：每 host / 每 key 一条时间线。爬虫的 `next_ok` 是间隔下限；API 的桶是平均速率加突发。面试把两题连起来，像在同一家公司里做过系统。

## 追问

- **谁的配额被扣？** 工具调用的中间轮也是请求。Agent 循环要把内部轮次算进同一 key，否则用户一次会话打爆。
- **公平性？** 纯桶是 FCFS。多租户要加权：企业合同更大的 $r$。避免一个 key 占满模型槽，用每 key 最大并发另限。
- **429 怎么重试？** 客户端指数退避加抖动，服务端给明确 wait。不要让 SDK 无脑立刻重放非幂等请求。见 `anthropic-tool-use`。
- **按 token 还是按美元？** 内部可以换成美元桶，对外仍暴露 RPM / TPM，方便用户理解。计价变更时不要让用户重写限流逻辑。
