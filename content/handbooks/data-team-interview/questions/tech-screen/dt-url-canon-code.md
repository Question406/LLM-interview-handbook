---
id: dt-url-canon-code
section: tech-screen
order: 26
level: A
title: CoderPad：URL 怎么规范化，opt-out / robots 怎么落到一条拒绝函数？
quick: "URL 先统一规范化，再拿去做去重、许可拒绝表和评测匹配：scheme 和 host 转小写，去掉默认端口和 fragment，只删跟踪类 query，保留分页参数。host 后缀匹配要守住域名边界。原 URL 和规范化后的 URL 都要记录，robots 和 opt-out 由上游另做检查。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Crawl
  - URL
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: RFC 3986 Uniform Resource Identifier
    url: https://www.rfc-editor.org/rfc/rfc3986
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: About Applebot
    url: https://support.apple.com/en-us/119829
    type: primary
---

我会先把 URL 规范化，再按拒绝表匹配：scheme 和 host 转小写，去默认端口，删跟踪参数，对保留的 query 排序，去掉 fragment；拒绝规则按 host 后缀和 path 前缀查。抓取去重和许可检查用的是同一个规范化 URL。

比如 `http://Example.com/a?utm_source=x#top` 和 `https://example.com/a`，直接用原始字符串会被当成两篇，opt-out 表也对不上。去重、许可拒绝表和评测匹配都依赖 URL，所以这一步要先做。

## 规范化

```python
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

DROP_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid",
}
DEFAULT_PORTS = {"http": 80, "https": 443}


def canon_url(url):
    """规范化 URL：小写 scheme/host、去默认端口、去跟踪参数并排序 query、去 fragment。

    无法解析（没有 host 或端口非法）时返回 None。
    """
    parsed = urlparse(url.strip())
    scheme = (parsed.scheme or "http").lower()
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    netloc = host
    if port and port != DEFAULT_PORTS.get(scheme):
        netloc = f"{host}:{port}"
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in DROP_QUERY_KEYS
    ]
    query.sort()
    return urlunparse((scheme, netloc, path, "", urlencode(query), ""))
```

要不要去掉 www 按域定，有的站 `www` 和裸域是两套 CMS。登录墙和付费墙别靠 URL 去猜，在抓取阶段就不进。

## 拒绝：后缀 host，前缀 path

`example.com` 要挡住 `a.example.com`，但不能挡住 `notexample.com`，所以用 `endswith("." + s)`，别用 `s in host`。

```python
def host_denied(host, suffixes):
    """host 等于某个后缀，或是它的子域，就算命中。"""
    host = host.lower()
    for s in suffixes:
        s = s.lower().lstrip(".")
        if host == s or host.endswith("." + s):
            return True
    return False


def url_denied(url, host_suffixes, path_prefixes):
    """返回 (是否拒绝, 原因)。先规范化，再按 host 后缀和 path 前缀匹配。"""
    canonical = canon_url(url)
    if canonical is None:
        return True, "unparseable"
    parsed = urlparse(canonical)
    if host_denied(parsed.hostname or "", host_suffixes):
        return True, "host"
    for prefix in path_prefixes:
        if (parsed.path or "/").startswith(prefix):
            return True, "path"
    return False, "ok"
```

测试覆盖规范化的几种情况、非法输入、域名边界和四种拒绝结果：

```python
# 大小写、默认端口、跟踪参数、fragment、结尾斜杠都被规范掉
assert canon_url("http://Example.com:80/a/?utm_source=x#top") == "http://example.com/a"

# query 排序后再拼，参数顺序不同的同一页对得上
assert canon_url("https://example.com/s?b=2&a=1") == canon_url("https://example.com/s?a=1&b=2")

# 非默认端口保留，分页等有意义的参数保留
assert canon_url("https://example.com:8443/news?page=2") == "https://example.com:8443/news?page=2"

# 没有 host 或端口非法时返回 None
assert canon_url("not a url") is None
assert canon_url("http://example.com:99999/") is None

# 后缀匹配挡住子域，但不挡名字里恰好含有它的域
assert host_denied("a.example.com", ["example.com"])
assert not host_denied("notexample.com", ["example.com"])

# url_denied：host、path、无法解析、放行四种结果
assert url_denied("https://WWW.Example.com/x", ["example.com"], []) == (True, "host")
assert url_denied("https://site.org/private/doc", [], ["/private"]) == (True, "path")
assert url_denied("garbage", [], []) == (True, "unparseable")
assert url_denied("https://site.org/public", ["example.com"], ["/private"]) == (False, "ok")
```

每条 URL 解析一次，拒绝表按后缀和前缀线性查。robots 和训练 opt-out 是上游抓取器的表，训练侧再挡一层，防止旧快照混进来。撤回需要精确的墓碑记录，因为 Bloom 不支持删除，见 `dt-exact-dedup-code`。命中拒绝的文档进 quarantine，同时留原 URL 和 canon URL，方便审计误杀。

## 追问

**https 和 http 当同一页吗？**
默认当，再用内容哈希确认。有的站 HTTP 是镜像，HTTPS 才是登录后的正文。

**query 全部丢掉？**
不行，新闻分页的 `?page=2` 要留，只丢跟踪参数。

**和评测 URL 的重叠怎么查？**
规范化之后才能和冻结评测比，用原始字符串比对会漏。

**拒绝表里的域名为什么不用 `s in host`？**
那样 `notexample.com` 会被 `example.com` 误挡。用等于或 `endswith("." + s)` 守住域名边界。

相关：`dt-exact-dedup-code`
