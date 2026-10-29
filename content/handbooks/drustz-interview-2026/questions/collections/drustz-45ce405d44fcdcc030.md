---
id: drustz-45ce405d44fcdcc030
section: collections
order: 27
level: A
title: hack2hire 完整题解（抓取的解锁内容） · Concurrent Web Crawler
quick: 作者文档章节 · hack2hire 完整题解（抓取的解锁内容） · Concurrent Web Crawler
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/hack2hire-premium.md
    type: primary
---
## Concurrent Web Crawler

*(This question is a variation of the LeetCode question [1242. Web Crawler Multithreaded](https://leetcode.com/problems/web-crawler-multithreaded/description/). If you haven't completed that question yet, it is recommended to solve it first.)*

Given a URL `startUrl` and an interface `htmlParser`, implement a concurrent web crawler to discover and return all **unique** URLs that have the **exact same hostname** as `startUrl`.

The crawler must follow the rules below:

* **Starting Point:** Begin crawling from `startUrl`.
* **Same Hostname:** Only record and further crawl URLs whose hostname is **exactly identical** to the hostname of `startUrl`.

&lt;img src="[来源链接](https://res.cloudinary.com/algro/image/upload/v1765305551/production/post/692f5158cd79766b0b310122/tpnnebg42m0vxlwemsx3.png") alt="" height="200" width="1000" /&gt;

  All URLs use the `http` protocol without a port number.
  The hostname is defined as the substring between `"://"` and the next `'/'` (or the end of the string if no further `'/'` exists).
* **URL Uniqueness:** Before checking uniqueness, **remove the fragment part** (everything after and including `'#'`). Two URLs are considered the same if they match after this sanitization step.
  * For example: `"http://example.com/page#section1"` and `"http://example.com/page"` should both be treated as `"http://example.com/page"` for uniqueness checking and for subsequent crawling.
* **No Duplicate Visits:** A sanitized URL must **not** be crawled or added more than once.
* **Fragment Sanitization Order:** Fragment removal occurs **before** hostname comparison and before deduplication.
* **Graph Characteristics:** The hyperlink graph may contain cycles, and pages may reference previously visited pages.

You are provided with the implementation of `HtmlParser`:

```java
/*
 * Provided Html Parser implementation. You should NOT modify it.
 */
class HtmlParser {

  // Returns all raw URLs from the webpage of the given URL.
  List<String> getUrls(String url){...} 
}
```



Each call to `getUrls` is subject to a certain latency to simulate the real-world network conditions, so your solution must use **concurrency** to fetch multiple pages in parallel.

For testing purposes, you will be given three variables `urls`, `edges` and `startUrl` to describe the underlying hyperlink graph. Only `startUrl` is accessible in your code; `urls` and `edges` are **not** directly available.

Return all discovered URLs (after sanitization) in any order.




**Constraints:**

* All URLs use the `http` protocol and do not contain a port number.
* 1 â¤`urls.length`â¤ 1000, 
* 1 â¤ `edges.length` â¤ 1000
* Each `getUrls` call will return in â¤ 15 ms.


**Example 1:**

&lt;img src="[来源链接](https://res.cloudinary.com/algro/image/upload/v1764714794/production/post/692f5158cd79766b0b310122/l0vqimxxtu4xbwzknsla.png") alt="" height="400" width="500" /&gt;

> **Input:**
> urls = ["[来源链接](http://example.com/page1",) "[来源链接](http://example.com/page2",) "[来源链接](http://example.com/page3#sectionA",) "[来源链接](http://example.net/page4#"],)
> edges = [[0, 1], [0, 2], [1, 3], [2, 0]],
> startUrl = "[来源链接](http://example.com/page1")
>
> **Output:**
> ["[来源链接](http://example.com/page1",) "[来源链接](http://example.com/page2",) "[来源链接](http://example.com/page3"])
>
> **Explanation:**
> * All three reachable pages share the hostname "example.com".
> * The URL "[来源链接](http://example.com/page3#sectionA") is sanitized to "[来源链接](http://example.com/page3".)
> * The page "[来源链接](http://example.net/page4#") is ignored due to a different hostname.

**Example 2:**

> **Input:**
> urls = ["[来源链接](http://news.yahoo.com/home",) "[来源链接](http://news.google.com/top",) "[来源链接](http://news.yahoo.com/news"],)
> edges = [[1, 0], [0, 2]],
> startUrl = "[来源链接](http://news.google.com/top")
>
> **Output:**
> ["[来源链接](http://news.google.com/top"])

**Example 3:**
> **Input:**
> urls = ["[来源链接](http://site.com/a",) "[来源链接](http://site.com/b#frag1",) "[来源链接](http://site.com/b#frag2",) "[来源链接](http://site.com/c",) "[来源链接](http://other.com/x",) "[来源链接](http://site.com/d",) "[来源链接](http://site.com/e#",) "[来源链接](http://site.com/f"],)
> edges = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [3, 5], [5, 0], [5, 6], [6, 7], [7, 0]],
> startUrl = "[来源链接](http://site.com/a")
>
> **Output:**
> ["[来源链接](http://site.com/a",) "[来源链接](http://site.com/b",) "[来源链接](http://site.com/c",) "[来源链接](http://site.com/d",) "[来源链接](http://site.com/e",) "[来源链接](http://site.com/f"])

**讲解**: This problem requires a **concurrent breadth-first search (BFS)** to crawl a set of web pages, but with two key restrictions: URLs must match the hostname of `startUrl`, and all URLs are **sanitized** (removing any fragment after `'#'`) before being used for deduplication.

**Key Steps:**

1. **Hostname Matching**
   For each discovered URL, extract the hostname (the string after `"http://"` and before the next `'/'`, or the end of the string). Only URLs with a hostname exactly matching `startUrl` are further explored.

2. **Sanitization**
   Before adding a URL to the visited set, strip off any fragment (`'#'` and everything after). This ensures that, for example, `"http://site.com/page#foo"` and `"http://site.com/page#bar"` are considered the same and only crawled once.

3. **Concurrency**
   Use a thread pool or asynchronous workers to issue multiple `getUrls` requests in parallel. This hides network or I/O latency and ensures high throughput. All crawl tasks use a **thread-safe set** to track which URLs have been scheduled or visited, guaranteeing each (sanitized) URL is processed only once.

4. **Synchronization**
   To ensure the main process waits for all crawl tasks to finish, use a synchronization mechanism such as a phaser, a counter, or a barrier that dynamically tracks outstanding work. The crawler returns results only after all scheduled crawl tasks are complete.

5. **Result Collection**
   Gather all unique, sanitized URLs discovered by the crawler and return them in any order.


### Complexity Analysis

* **Time Complexity:**
  *O(N + E)*, where *N* is the number of unique URLs visited (after sanitization) and *E* is the total number of links examined. 

* **Space Complexity:**
  *O(N)*.  At peak, may have up to *O(N)* pending crawl tasks. Any additional memory for worker threads or async tasks is also at most *O(N)*.

**概要**:
- Implement a multithreaded crawler that explores pages starting from a given URL.
- Filter discovered links to only include those sharing the exact same hostname as the start page.
- Sanitize all URLs by removing fragment identifiers before deduplication and hostname comparison.

**考察点**:
- Thread-safe shared state management and race condition prevention
- Parallel graph traversal with dynamic work distribution
- String manipulation and URL parsing logic
- Synchronization primitives for coordinating async tasks

**常用模式**:
- Graph Traversal
- DFS/BFS
- Hashing

**提示**:
- Consider how multiple threads will safely read and update the set of visited URLs without creating duplicates or deadlocks.
- Use an ExecutorService to dispatch tasks asynchronously, pair it with a thread-safe Set for tracking, and employ a Phaser or atomic counter to signal when all scheduled crawls are finished.

**可能的 follow-up**:
- How would you implement crawl delay or rate limiting to avoid overwhelming target servers?
- What modifications would be needed to support breadth-first vs depth-first priority in a concurrent setting?
- How would you architect this solution to run across multiple worker nodes rather than a single process?





**参考解 (Python)**



```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from collections import defaultdict

"""
Provided Html Parser implementation. You should NOT modify it.
"""


class HtmlParser:
    def __init__(self, urls, edges):
        self.graph = {}
        for u in urls:
            self.graph[u] = []

        for edge in edges:
            from_idx = edge[0]
            to_idx = edge[1]
            self.graph[urls[from_idx]].append(urls[to_idx])

    def getUrls(self, url):
        try:
            time.sleep(0.01)  # Simulate network latency
        except:
            pass

        links = self.graph.get(url)
        if links is None:
            return []
        return links


class Solution:
    def crawl(self, startUrl, htmlParser):
        startHost = self.getHost(startUrl)
        visited = set()
        visited_lock = threading.Lock()
        pool = ThreadPoolExecutor(max_workers=max(4, os.cpu_count()))

        # Use threading primitives to track completion
        pending_tasks = threading.Semaphore(0)
        active_tasks = threading.Event()
        task_count = [0]  # Use list to make it mutable in nested functions
        task_count_lock = threading.Lock()

        sanitizedStart = self.sanitize(startUrl)
        visited.add(sanitizedStart)
        self.submitTask(
            startUrl,
            htmlParser,
            startHost,
            visited,
            visited_lock,
            pool,
            pending_tasks,
            active_tasks,
            task_count,
            task_count_lock,
        )

        # Wait for all crawl tasks to complete
        while True:
            with task_count_lock:
                if task_count[0] == 0:
                    break
            time.sleep(0.001)  # Small sleep to prevent busy waiting

        pool.shutdown()

        result = list(visited)
        return result

    def submitTask(
        self,
        url,
        parser,
        host,
        visited,
        visited_lock,
        pool,
        pending_tasks,
        active_tasks,
        task_count,
        task_count_lock,
    ):
        with task_count_lock:
            task_count[0] += 1

        def task():
            try:
                urls = parser.getUrls(url)
                for next_url in urls:
                    sanitized = self.sanitize(next_url)
                    nextHost = self.getHost(sanitized)
                    if nextHost != host:
                        continue
                    # only schedule if not already visited
                    with visited_lock:
                        if sanitized not in visited:
                            visited.add(sanitized)
                            should_submit = True
                        else:
                            should_submit = False

                    if should_submit:
                        self.submitTask(
                            next_url,
                            parser,
                            host,
                            visited,
                            visited_lock,
                            pool,
                            pending_tasks,
                            active_tasks,
                            task_count,
                            task_count_lock,
                        )
            finally:
                with task_count_lock:
                    task_count[0] -= 1

        pool.submit(task)

    def getHost(self, url):
        # Remove scheme (http:// or https://)
        start = url.find("://")
        if start == -1:
            start = 0
        else:
            start = start + 3

        end = url.find('/', start)
        if end == -1:
            end = len(url)

        return url[start:end]

    def sanitize(self, url):
        idx = url.find('#')
        if idx == -1:
            return url

        return url[:idx]


def main():
    test1()
    test2()
    test3()


def test1():
    print("===== Test 1 =====")

    urls = [
        "http://example.com/page1",
        "http://example.com/page2",
        "http://example.com/page3#sectionA",
        "http://example.net/page4#",
    ]
    edges = [[0, 1], [0, 2], [1, 3], [2, 0]]
    startUrl = "http://example.com/page1"

    parser = HtmlParser(urls, edges)
    solution = Solution()
    result = solution.crawl(startUrl, parser)
    print(result)
    # Expected: ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3"]


def test2():
    print("===== Test 2 =====")

    urls = [
        "http://news.yahoo.com/home",
        "http://news.google.com/top",
        "http://news.yahoo.com/news",
    ]
    edges = [[1, 0], [0, 2]]
    startUrl = "http://news.google.com/top"

    parser = HtmlParser(urls, edges)
    solution = Solution()
    result = solution.crawl(startUrl, parser)
    print(result)
    # Expected: ["http://news.google.com/top"]


def test3():
    print("===== Test 3 =====")

    urls = [
        "http://site.com/a",
        "http://site.com/b#frag1",
        "http://site.com/b#frag2",
        "http://site.com/c",
        "http://other.com/x",
        "http://site.com/d",
        "http://site.com/e#",
        "http://site.com/f",
    ]
    edges = [
        [0, 1],
        [0, 2],
        [1, 3],
        [2, 3],
        [3, 4],
        [3, 5],
        [5, 0],
        [5, 6],
        [6, 7],
        [7, 0],
    ]
    startUrl = "http://site.com/a"

    parser = HtmlParser(urls, edges)
    solution = Solution()
    result = solution.crawl(startUrl, parser)
    print(result)
    # Expected: ["http://site.com/a", "http://site.com/b", "http://site.com/c",
    # "http://site.com/d", "http://site.com/e", "http://site.com/f"]


if __name__ == "__main__":
    main()
```





*通过率: 56%*

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/hack2hire-premium.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/hack2hire-premium.md)。作者整理资料；许可和第三方来源范围见阅读指南。
