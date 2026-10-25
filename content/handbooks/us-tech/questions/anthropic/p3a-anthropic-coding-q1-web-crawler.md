---
id: p3a-anthropic-coding-q1-web-crawler
section: anthropic
order: 603
level: A
title: "Anthropic：同域爬虫：从 BFS 到并发和分布式"
quick: "我会用 BFS 管待抓 URL，解析 hostname 判断同域，去掉 fragment 后去重。并发时检查和标记 visited 要在同一把锁里完成；未完成工作总数归零才结束，task_done 放在 finally 里，避免异常让主线程一直等。"
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

## 题目描述

实现一个并发网页遍历器，收集起始页面所在站点能够到达的所有页面。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`crawl(start, get_urls, workers=4)` 返回排序后的 URL 字符串列表。`get_urls`(url) 是注入的线程安全函数，返回该页面的出链，不需要真实联网。只访问与 start 的 hostname 相同的 URL；去掉 URL 的 fragment 后作为页面身份，其他 URL 部分保留。每个规范化后的 URL 最多调用一次 `get_urls`，重复链接和环不能导致重复遍历。

图有限且不超过 10000 个页面，workers 为正整数。使用最多 workers 个并发工作者；发生抓取异常时完成必要的工作收尾并抛出 RuntimeError，不能使调用永久等待。

### 示例

```text
start = "https://a.test/x"
x 的出链为 ["https://a.test/y#part", "https://b.test/z"]
y 的出链为 ["https://a.test/x", "https://a.test/y"]
返回 ["https://a.test/x", "https://a.test/y"]；x、y 各抓取一次。
```

## 解题思路与参考答案

## 题目

给一个起始 URL 和一个 `get_urls(url)` 接口（返回页面里的链接），抓取所有与起始 URL 同域的页面，每个页面只抓一次。题目会从单线程 BFS 逐步追问到多线程并发，再到多机分布式。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会先用 BFS 写单线程版本，队列保存待抓 URL，`visited` 记录已经安排抓取的页面。同域要用 `urlsplit` 解析 hostname 后比较，字符串前缀不足以判断。URL 中的 fragment（`#` 之后的部分）不改变页面内容，入队前先去掉，这样同一页面不会因锚点不同被重复抓取。

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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert crawl("https://a/x", get_urls, 3) == ["https://a/x", "https://a/y"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

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
