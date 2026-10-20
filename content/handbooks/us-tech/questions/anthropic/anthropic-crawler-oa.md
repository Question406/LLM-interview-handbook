---
id: anthropic-crawler-oa
section: anthropic
order: 5
level: A
title: Anthropic OA：爬虫 / 网页抓取分层题，礼貌延迟与去重怎么做？
quick: >-
  先把单线程做对：URL 规范化、入队时去重、按主机限速；并发时 visited 的检查和插入必须原子。礼貌延迟靠每个主机的 next_ok，不是全局 sleep。
tags:
  - 完整编程练习
  - Anthropic
  - Coding
  - Crawler
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
  - title: Design a concurrent web crawler (Anthropic-style prompt)
    url: https://prachub.com/interview-questions/design-a-concurrent-web-crawler-3
    type: secondary
---

## 完整编程练习（手册重构版）

> 来源网站只披露了题型。下面的接口、约束和测试是手册补的练习约定，不是面试官原题或隐藏测试。Python 3 标准库，不发真实网络请求。

### 题面、接口与约束

- `crawl(start, get_urls, workers=4) -> list[str]`：从 `start` 出发多线程抓取，返回所有抓到的 URL，按字典序排序。
- `get_urls(url)` 由调用方注入，线程安全，返回该页面上的链接列表。
- 只抓和起始 URL 同一 hostname 的链接。去掉 fragment（`#` 之后的部分），URL 的其余部分原样保留，不做更多规范化。
- 每个 URL 只解析一次，也就是 `get_urls` 对同一个 URL 最多调用一次。
- `get_urls` 抛异常时，先把剩下的工作做完，再抛 `RuntimeError`（原异常作为 `__cause__`）；不能因为任务计数没对上而卡死。
- `workers >= 1`，否则抛 `ValueError`；起始 URL 没有 hostname 也抛 `ValueError`。图是有限的，URL 数不超过 $10^{4}$。

### 输入输出示例

```text
get_urls("https://a/x") -> ["https://a/y#f", "https://b/z"]
get_urls("https://a/y") -> ["https://a/x", "https://a/y"]

crawl("https://a/x", get_urls, workers=3) -> ["https://a/x", "https://a/y"]
# https://b/z 不同 host，被跳过；a/x、a/y 各只解析一次
```

### 解题思路与正确性

检查 `seen` 和放进队列在同一把锁里完成，所以一个 URL 最多入队一次，也就最多被解析一次。如果先抓再标记已访问，两个线程可能同时发现同一个链接，各抓一遍。

结束条件靠 `Queue.join()`。它等的是「未完成任务数」归零，这个计数包括动态新加入的 URL 和正在处理中的 URL。队列某一刻暂时为空，但还有线程在解析、马上会放进新链接，这时 `join()` 不会返回，所以不会提前结束。

每个任务的 `task_done()` 写在 `finally` 里，`get_urls` 抛异常也照样计数，计数不会少减而让 `join()` 永远等下去。所有真实任务完成后，再给每个线程放一个 `None` 哨兵让它退出。

### 完整参考实现（Python 3）

```python
from queue import Queue
from threading import Lock, Thread
from urllib.parse import urldefrag, urlsplit


def crawl(start, get_urls, workers=4):
    """多线程抓取与 start 同 hostname 的所有页面，返回排序后的 URL 列表。

    每个 URL 只调用一次 get_urls；get_urls 出错时做完剩余工作，再抛 RuntimeError。
    """
    if workers < 1:
        raise ValueError(f"workers must be >= 1, got {workers}")
    start = urldefrag(start)[0]
    domain = urlsplit(start).hostname
    if domain is None:
        raise ValueError(f"start URL has no hostname: {start!r}")

    work = Queue()
    work.put(start)
    seen = {start}
    lock = Lock()
    errors = []

    def worker():
        while True:
            url = work.get()
            try:
                if url is None:  # 退出哨兵
                    return
                for link in get_urls(url):
                    link = urldefrag(link)[0]
                    if urlsplit(link).hostname != domain:
                        continue
                    with lock:  # 检查和插入必须原子，否则同一 URL 会被抓两次
                        if link in seen:
                            continue
                        seen.add(link)
                    work.put(link)
            except Exception as error:
                with lock:
                    errors.append(error)
            finally:
                work.task_done()  # 出错也要计数，否则 join() 永远不返回

    threads = [Thread(target=worker) for _ in range(workers)]
    for thread in threads:
        thread.start()
    work.join()  # 等所有真实任务（含动态加入的）完成
    for _ in threads:
        work.put(None)
    for thread in threads:
        thread.join()
    if errors:
        raise RuntimeError(f"crawler failed on {len(errors)} page(s)") from errors[0]
    return sorted(seen)
```

### 可执行测试

```python
from collections import Counter


def expect_error(error_type, action):
    try:
        action()
    except error_type as error:
        return error
    raise AssertionError(f"expected {error_type.__name__}")


# 基本场景：去 fragment、跳过其他 host、自环和回边不会重复解析
links = {
    "https://a/x": ["https://a/y#f", "https://b/z"],
    "https://a/y": ["https://a/x", "https://a/y"],
}
calls = Counter()


def parser(url):
    calls[url] += 1
    return links[url]


assert crawl("https://a/x", parser, 3) == ["https://a/x", "https://a/y"]
assert all(count == 1 for count in calls.values())

# 起始 URL 带 fragment，单线程也能跑完
assert crawl("https://a/x#top", parser, 1) == ["https://a/x", "https://a/y"]

# 一个页面解析出错：其余页面照常抓完，最后抛 RuntimeError
visited = []
flaky_links = {"https://a/1": ["https://a/2", "https://a/3"], "https://a/3": []}


def flaky_parser(url):
    visited.append(url)
    if url == "https://a/2":
        raise ValueError("bad page")
    return flaky_links[url]


error = expect_error(RuntimeError, lambda: crawl("https://a/1", flaky_parser, 2))
assert isinstance(error.__cause__, ValueError)
assert sorted(visited) == ["https://a/1", "https://a/2", "https://a/3"]

# 每个页面都出错时也不会卡死
expect_error(RuntimeError, lambda: crawl("https://a/x", lambda url: 1 / 0))

# 非法参数
expect_error(ValueError, lambda: crawl("https://a/x", parser, 0))
expect_error(ValueError, lambda: crawl("not-a-url", parser))
```

### 复杂度与追问

设页面数为 V、链接总数为 E。每个页面解析一次，每条链接检查一次，总工作量 O(V + E)；`seen` 占 O(V)，队列里同时排队的 URL 不超过 V。线程实际能带来多少吞吐，取决于 `get_urls` 的等待时间（网络 I/O 时线程会释放 GIL）。

- 追问「多进程或多机抓取」：`seen` 要换成外部的原子去重，例如 Redis 的 `SADD` 返回值判断是否新插入。
- 追问「上生产还缺什么」：每个主机的限速、`robots.txt`、请求超时，以及能在崩溃后恢复的持久化 frontier，见下文。

## 题怎么来的

Anthropic 的 CodeSignal 题是分层的，一层的单测全过了才开下一层。公开题库里的网页爬虫也是这个形态：给种子 URL，抽链接、去重、限制域名范围，再加礼貌延迟和线程池。按层实现即可。和 `anthropic-bank-oa` 一样，第一层的接口如果漏掉了时间或身份，后面每一层都只能打补丁。

## 第一层：规范化 + 调度时去重

上面的练习只去掉了 fragment。真实爬虫在抓取之前，要把 URL 统一成同一个键：host 转小写、去掉默认端口和 fragment、对无意义的 query 参数排序、把相对链接解析成绝对链接。不做规范化，`http://A.com` 和 `http://a.com/` 会被当成两个页面各抓一次。

`visited` 的检查和插入发生在**放进 frontier 的时候**，而不是抓回来之后。先抓再标记已访问，并发时同一个 URL 会被请求两遍。伪代码：

```python
def enqueue(self, url, depth):
    key = canonicalize(url)
    if key in self.seen or depth > self.max_depth:
        return
    if not in_scope(key, self.allowed_hosts):
        return
    self.seen.add(key)
    self.frontier.append((key, depth))
```

OA 里 `seen` 用集合就够了。生产环境再谈 Bloom filter：它的假阳性会让一些没见过的 URL 被当成见过而漏抓，但不会有假阴性。爬虫能接受漏抓，不能接受把站点打爆，所以 Bloom 只当第一道过滤，命中之后再查精确集合。

内容去重是另一层问题。URL 去重防止同一个地址被抓多次，正文哈希防止镜像站的相同内容。OA 先把 URL 去重做对；近似重复检测（SimHash）留作 follow-up，白板上不必展开。

## 礼貌：每主机一条时间线

用全局 `sleep(1)` 控速是错的。礼貌指的是**每个 host 两次请求之间的最小间隔**，再加上 `robots.txt` 里的 crawl-delay。结构是这样：

- 全局 frontier 按 BFS 或优先级出队。
- 出队的 URL 按 host 分到各自的 back queue。
- 每个 host 记一个 `next_ok` 时间，到点了才把它队头的 URL 交给 fetcher。
- 限制同一 host 同时进行中的请求数。弱一点的礼貌是「同一时刻只有 1 个连接」，强一点的还要求两次请求之间留出间隔。Mercator 后来让间隔随上次请求的耗时放大，面试时说「自适应间隔」就够了。

`robots.txt` 要在抓内容之前先抓，缓存时带 TTL。拿 `robots.txt` 时返回 4xx 可以当作没有限制；返回 5xx 或超时则当作全站禁止，这是保守的默认做法。User-Agent 要能让站长识别出是谁在抓。

延迟的实现不要每次扫全表。做法和 TTL 堆一样：`(next_ok, host)` 放进最小堆，推进时钟时弹出已到点的 host，从它的队列里取一个 URL。如果 OA 的时间是模拟的整数，就不要调用真实的 `time.sleep`，否则单测结果不可复现。

## 并发：锁的粒度

线程池只解决网络等待的问题，真正要设计的是下面几件事：

1. `seen` 的 check-and-add 用一把锁或一个并发集合保护。
2. 每个 host 一把锁，保护该 host 的队列和 `next_ok`。
3. frontier 要有容量上限，队列满了就暂停抽取新链接，避免内存耗尽。
4. 失败重试用指数退避，退避时间加在该 host 的 `next_ok` 上，而不是换一个线程立刻重新请求。

结束条件是 frontier 为空并且进行中的请求数为 0。优雅停机的步骤：停止入队，等进行中的请求结束，把没完成的 URL 写回持久存储。另外，不要在无锁的情况下一边遍历 `seen` 一边让它扩容。

还有一类陷阱是爬虫陷阱：日历页、URL 里的会话 id、重复的 path segment 都会让 frontier 无限增长。用深度上限、每个 host 的 URL 数上限，再在规范化时去掉 session 参数，面试时点到即可。

## 追问

- **Bloom 假阳性怎么办？** 命中只当作「可能见过」，再回到精确集合确认。不要把 Bloom 当成唯一的 visited。
- **礼貌和吞吐怎么平衡？** 瓶颈几乎总是 host 不够多、慢主机拖住了进度，而不是连接数不够。只加 worker 而不增加 host 的多样性，只会让同一个 host 被请求得更频繁，违反礼貌。
- **和 API 限流有什么关系？** 每个 host 的 `next_ok` 就是令牌桶（token bucket）的一个特例，见 `anthropic-rate-limit`。
- **要不要解析 JavaScript？** OA 只按静态链接处理。现场可以说：动态站点要走另一条渲染队列，成本更高、对站点的压力也更大，默认不做。
