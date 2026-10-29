---
id: drustz-516a90beeb1d1fe1de
section: anthropic
order: 96
level: A
title: Web Crawler Implementation
quick: original-structured-preparation-guide · Web Crawler Implementation
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/63b7bb68-fcb6-46cd-ab2c-fbac3302c9f9
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Web Crawler Implementation：清晰、可测的同步实现

## 契约

实现 `crawl(start_url: str, parser: HtmlParser) -> list[str]`。把 URL 看作图节点，`parser.get_urls(u)` 是出边；返回所有同 hostname 可达节点。例：`https://a.test/` 链到 `/p`、`https://b.test/x`，只有起点和 `a.test/p` 可进入结果。

## 模块化写法

先用 URL parser 取得起点 hostname，不能写 `url.startswith(host)`。维护 `deque([start])` 和 `{start}`；弹出页面后取得链接，将相对链接按题目约定用 `urljoin` 解析，再做同域检查和去重，成功后立刻入队。将 `canonicalize`、`same_host`、`fetch_links` 分成小函数，测试时可注入字典版 parser；若题目保证绝对 URL，就不要额外改变 query、尾斜杠或大小写。

同步版以队列耗尽终止，天然没有并发竞态。总时间 `O(V+E+S)`，其中 `S` 是解析 URL 的总字符数；空间 `O(V)`。结果若要求稳定顺序，可保留 BFS 发现顺序；若顺序无关，不必排序增加 `O(V log V)`。边界测试包括空页面、起点自环、菱形图、重复链接、`a.test.evil.com`、端口、非法链接、parser 异常和相对 `../x`。并发属于可选 follow-up，不应让基础实现先背上复杂的共享状态。

实现时最好同时保存 `result` 列表和 `seen` 集合：前者维持发现顺序，后者提供均摊 `O(1)` 查询；只用列表去重会退化到 `O(V²)`。起点即使没有任何出边也必须出现在答案中。若 parser 对同一页可能返回同一链接多次，在扫描当前出边时仍沿用全局 `seen`，无需额外建立局部集合。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/63b7bb68-fcb6-46cd-ab2c-fbac3302c9f9)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
