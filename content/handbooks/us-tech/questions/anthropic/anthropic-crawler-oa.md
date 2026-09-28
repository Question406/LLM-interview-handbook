---
id: anthropic-crawler-oa
section: anthropic
order: 5
level: A
title: Anthropic OA：爬虫 / 网页抓取分层题，礼貌延迟与去重怎么做？
quick: >-
  先保证单线程正确：URL 规范化、调度时原子去重、按域礼貌。并发不是加线程，是 frontier 和 visited
  的检查插入不能拆开。礼貌是每主机一条队列加 next_ok 时间，不是全局 sleep。
tags:
  - Anthropic
  - Coding
  - Crawler
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
  - title: Design a concurrent web crawler (Anthropic-style prompt)
    url: https://prachub.com/interview-questions/design-a-concurrent-web-crawler-3
    type: secondary
---

Anthropic 的 CodeSignal 是「一层单测过了才开下一层」。公开题库里网页爬虫按同一形态出：种子 URL、抽链、去重、域范围，再加礼貌延迟和线程池。按分层实现答。和 `anthropic-bank-oa` 一样，第一层接口漏掉时间或身份，后面全是补丁。

## 第一层：规范化 + 调度时去重

抓之前要把 URL 收成同一个键：小写 host、去掉默认端口、fragment、排序无意义 query、解析相对链接。不去规范化，`http://A.com` 和 `http://a.com/` 会抓两次。

`visited` 的检查插入发生在 **放进 frontier 时**，不是抓回来之后。先抓再标已访问，并发下同一 URL 会打出去两遍。伪代码：

```python
def enqueue(self, url, depth):
    key = canon(url)
    if key in self.seen or depth > self.max_depth:
        return
    if not in_scope(key, self.allowed):
        return
    self.seen.add(key)
    self.frontier.append((key, depth))
```

`seen` 用集合就够 OA。生产再谈 Bloom：假阳性会漏抓，假阴性不会；爬虫能接受漏、不能接受打爆站点，所以 Bloom 只当第一道，命中再查精确集。

内容去重是另一层：URL 去重防重复抓，正文哈希防镜像站。OA 先把 URL 做对。近重复用 SimHash 当 follow-up，白板不要展开。

## 礼貌：每主机一条时间线

全局 `sleep(1)` 是错的。礼貌是 **每个 host 的最小间隔**，外加 `robots.txt` 的 crawl-delay。结构：

- 全局 frontier 按 BFS 或优先级出队。
- 按 host 分到 back queue。
- 每个 host 记 `next_ok`。到点才把队头交给 fetcher。
- 同 host 同时 in-flight 上限，弱礼貌是「同时只有 1 个连接」，强礼貌还要在两次请求之间留间隔。Mercator 后来用「间隔随上次耗时放大」，面试说自适应即可。

`robots.txt`：先抓规则再抓内容，缓存带 TTL。4xx 可当无限制，5xx 或超时当全禁止，这是保守默认。User-Agent 要可识别。

延迟实现不要扫全表。和 TTL 堆一样：`(next_ok, host)` 进 min-heap，推进时钟弹出到期的 host，从它的队列取一个 URL。OA 若时间是模拟整数，不要用真实 `time.sleep`，否则单测不可复现。

## 并发：锁的粒度

线程池只解决网络等待。真正要设计的是：

1. `seen` 的 check-and-add 一把锁或并发集。
2. 每 host 一把锁，保护该 host 队列和 `next_ok`。
3. frontier 有界，形成反压：抽链太快会把内存打爆。
4. 失败重试带指数退避，且退避加在该 host 的 `next_ok` 上，不要换一条线程继续砸。

完成条件：frontier 空且 in-flight 为 0。优雅停：停入队、等 in-flight、把未完成 URL 写回。别在遍历 `seen` 时无锁扩容。

陷阱：日历页、会话 id、重复 path segment 会让 frontier 无穷。深度上限 + 每 host URL 上限 + 规范化掉 session 参数，面试点一下。

## 追问

- **Bloom 假阳性怎么办？** 当「可能见过」，回源精确集。不要把 Bloom 当唯一 visited。
- **礼貌和吞吐的矛盾？** 瓶颈几乎总是「不重复的慢主机」而不是连接数。加 worker 不加 host 多样性，只会违反礼貌。
- **和 API 限流的关系？** 每 host 的 `next_ok` 就是 token 桶的特例。见 `anthropic-rate-limit`。
- **要不要解析 JavaScript？** OA 按静态链接。现场说：动态站点是另一条渲染队列，成本和礼貌更差，默认不做。
