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


def test():
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


if __name__ == "__main__":
    test()
