---
id: dt-url-canon-code
section: tech-screen
order: 26
level: A
title: CoderPad：URL 怎么规范化，opt-out / robots 怎么落到一条拒绝函数？
quick: "统一规范化 URL，再用于去重、许可拒绝表和评测匹配。小写 scheme、host，去默认端口和 fragment，只删跟踪 query，保留分页参数。host 后缀匹配注意域名边界；记录原 URL 与 canon URL，robots 和 opt-out 另有上游检查。"
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

先做 URL 规范化（canon），再按拒绝表匹配（deny）。将 scheme、host 转小写，去默认端口，排序保留的 query，移除 fragment。拒绝规则按 host 后缀和 path 前缀检查。精确去重如果对原始 URL 做，`http://Example.com/a?utm_source=x#top` 和 `https://example.com/a` 会当两篇。opt-out 表也要对得上规范化之后的 host。

Applebot 公开口径尊重 robots 和「不要用来训基础模型」。抓取去重和许可是同一把钥匙。

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

www 去不去按域定。有的站 `www` 和裸域是两套 CMS。登录墙、付费墙不要靠 URL 猜，抓取阶段就不进，Apple 公开口径写了不爬这些。

## 拒绝：后缀 host，前缀 path

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

### 可执行测试

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

`example.com` 要挡住 `a.example.com`，不要挡住 `notexample.com`。所以用 `endswith("." + s)`，不要 `s in host`。

robots / 训练 opt-out 是上游抓取器的表，训练侧再挡一层，防止旧快照混进来。撤回需要精确墓碑记录，不能由 Bloom 单独承担，见 `dt-exact-dedup-code`。命中拒绝的文档进 quarantine，留原 URL 和 canon URL，方便审计误杀。

## 追问

- **https 和 http 当同一页吗？** 默认当。内容哈希再确认；有的站 HTTP 是镜像、HTTPS 是登录后正文。
- **query 全丢？** 新闻分页 `?page=2` 要留。只丢跟踪参数。
- **和评测 URL 重叠？** canon 之后才能和冻结评测比。原始字符串比对会漏。
