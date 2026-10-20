---
id: p3a-anthropic-coding-q1-web-crawler
section: anthropic
order: 603
level: A
title: "Anthropic：同域爬虫：从 BFS 到并发和分布式"
quick: "用 hostname 判断同域、去掉 fragment 后在同一把锁里检查并标记 visited；结束条件看未完成工作总数而不是队列是否为空，task_done 放在 finally 里防止异常导致卡死。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · coding-q1-web-crawler"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-web-crawler
    type: secondary
---

## 题目

给一个起始 URL 和一个 `get_urls(url)` 接口（返回页面里的链接），抓取所有与起始 URL 同域的页面，每个页面只抓一次。题目会从单线程 BFS 逐步追问到多线程并发，再到多机分布式。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

单线程版本就是 BFS：队列存待抓的 URL，`visited` 集合去重。同域判断要用 `urlsplit` 解析出 hostname 再比较，不要用字符串前缀匹配；URL 里的 fragment（`#` 之后的部分）不影响页面内容，入队前去掉。

改成多线程时有两个关键点：

- 「检查是否访问过」和「标记为已访问」必须在同一把锁里完成。分开做的话，两个线程可能同时发现某个 URL 没访问过，于是都把它入队。
- 结束条件不能是「队列为空」。队列暂时空着时，可能还有线程正在处理页面，马上会产生新链接。要统计未完成的工作总量（排队中加处理中），归零才算结束。Python 的 `Queue.join()` 和 `task_done()` 正好提供这个计数。

还要约定 `get_urls` 抛异常时怎么办。这份练习的约定是：记录异常，继续把其他页面抓完，最后统一抛 `RuntimeError`。`task_done()` 必须放在 `finally` 里，否则一次异常就会让计数永远降不到零，主线程卡死。

限速、超时和跨机器分片属于另外的契约，放到追问里讨论。

相关题：[[anthropic-crawler-oa]]（同类题的另一份整理，额外要求按域名礼貌延迟；两边题面契约不同，分开练习，不要混用）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `crawl(start, get_urls, workers=4) -> list[str]`：从 `start` 出发，只抓与它 hostname 相同的 URL，返回排好序的已访问 URL 列表。
- `get_urls` 是注入的线程安全函数，不发真实网络请求。URL 去掉 fragment 后比较，其余部分原样保留；同一个 URL 只调用一次 `get_urls`。
- `get_urls` 抛异常时，先完成剩余工作再抛 `RuntimeError`，不能卡死。
- `workers >= 1`，起始 URL 必须有 hostname，否则抛 `ValueError`。有限图，URL 不超过 $10^4$ 个。

### 输入输出示例

```text
get_urls("https://a/x") -> ["https://a/y#f", "https://b/z"]
get_urls("https://a/y") -> ["https://a/x", "https://a/y"]

crawl("https://a/x", get_urls, workers=3) -> ["https://a/x", "https://a/y"]
```

`https://a/y#f` 去掉 fragment 后是 `https://a/y`；`https://b/z` 不同域，跳过。两个页面各只调用一次 `get_urls`。

### 解题思路与正确性

每个 URL 入队之前都要在锁内通过「不在 `visited` 中」的检查并被加入 `visited`，所以同一个 URL 最多入队一次，`get_urls` 最多调用一次。

`Queue` 的未完成计数在 `put` 时加一、`task_done` 时减一。线程在处理完一个页面、把它产生的新链接都 `put` 进去之后才调用 `task_done`，所以只要还有页面在处理，计数就不会归零。`join()` 返回时，所有可达页面都已处理完，这时再给每个线程发一个 `None` 哨兵让它退出。

### 完整参考实现（Python 3）

```python
from queue import Queue
from threading import Lock, Thread
from urllib.parse import urldefrag, urlsplit


def _strip_fragment(url):
    return urldefrag(url)[0]


def crawl(start, get_urls, workers=4):
    """多线程抓取与 start 同 hostname 的所有页面，每个 URL 只调用一次 get_urls。

    get_urls 抛异常时，先把其余工作做完，再统一抛 RuntimeError。
    """
    if workers < 1:
        raise ValueError(f"workers must be >= 1, got {workers}")
    start = _strip_fragment(start)
    domain = urlsplit(start).hostname
    if domain is None:
        raise ValueError(f"start url has no hostname: {start!r}")

    frontier = Queue()
    frontier.put(start)
    visited = {start}
    lock = Lock()
    errors = []

    def worker():
        while True:
            url = frontier.get()
            try:
                if url is None:  # 退出哨兵
                    return
                for link in get_urls(url):
                    link = _strip_fragment(link)
                    if urlsplit(link).hostname != domain:
                        continue
                    # 「检查 + 加入」必须在同一把锁里，否则两个线程可能同时入队同一个 URL
                    with lock:
                        if link in visited:
                            continue
                        visited.add(link)
                    frontier.put(link)
            except Exception as error:
                with lock:
                    errors.append(error)
            finally:
                # 无论成功还是异常都要 task_done，否则 join 永远等不到计数归零
                frontier.task_done()

    threads = [Thread(target=worker) for _ in range(workers)]
    for thread in threads:
        thread.start()
    # join 等的是「未完成任务数」归零，包括正在处理、还可能产生新链接的任务；
    # 所以队列暂时为空不会被误判成结束
    frontier.join()
    for _ in threads:
        frontier.put(None)
    for thread in threads:
        thread.join()

    if errors:
        raise RuntimeError(f"{len(errors)} page(s) failed") from errors[0]
    return sorted(visited)
```

### 可执行测试

```python
from collections import Counter

graph = {
    "https://a/x": ["https://a/y#f", "https://b/z"],
    "https://a/y": ["https://a/x", "https://a/y"],
}
calls = Counter()

def get_urls(url):
    calls[url] += 1
    return graph[url]

# 去掉 fragment、跳过别的域名，每个页面只解析一次
assert crawl("https://a/x", get_urls, 3) == ["https://a/x", "https://a/y"]
assert all(count == 1 for count in calls.values())

# get_urls 抛异常时不能卡死，最后抛 RuntimeError
def broken(url):
    raise ValueError("bad page")

try:
    crawl("https://a/x", broken)
except RuntimeError:
    pass
else:
    raise AssertionError("parser error should surface as RuntimeError")

# 部分页面失败时，其他页面仍会被抓完
seen = []

def flaky(url):
    seen.append(url)
    if url == "https://a/y":
        raise ValueError("bad page")
    return {"https://a/x": ["https://a/y", "https://a/w"], "https://a/w": []}[url]

try:
    crawl("https://a/x", flaky, 2)
except RuntimeError:
    pass
else:
    raise AssertionError("flaky page should surface as RuntimeError")
assert sorted(seen) == ["https://a/w", "https://a/x", "https://a/y"]
```

### 复杂度与追问

设可达页面数为 V、链接总数为 E。每个页面解析一次、每条链接检查一次，总工作量 O(V + E)；`visited` 占 O(V)，队列同时最多 O(V) 个 URL。实际吞吐主要取决于 `get_urls` 的耗时，线程数受 I/O 等待程度限制。

- 跨进程或多机时，`visited` 要放到外部存储里，并用原子操作去重（例如 Redis 的 `SADD` 返回值）；也可以按 URL 哈希把不同 URL 分给固定的机器，每台机器只负责自己那一片的去重。
- 生产环境还要有每个域名的限速、遵守 robots.txt、请求超时和重试，以及可持久化的 frontier，机器重启后能从断点继续。
