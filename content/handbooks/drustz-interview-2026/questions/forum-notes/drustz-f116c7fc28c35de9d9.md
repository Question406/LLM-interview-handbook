---
id: drustz-f116c7fc28c35de9d9
section: forum-notes
order: 46
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Problem Statement
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Problem Statement
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Problem Statement

You are given:

- A starting web address called `startUrl`.
- A tool called `HtmlParser` that finds all links on a specific web page.
You need to build a web crawler. It must find **all URLs** that you can reach from the `startUrl`.

**Important Rule:** You must only keep URLs that belong to the same **hostname** as the `startUrl`. The order of the list does not matter.

Here is the interface for the `HtmlParser`:

```java
interface HtmlParser {
    // Returns all URLs from a given page URL.
    public List<String> getUrls(String url);
}
```



Your function signature will look like this: `List<String> crawl(String startUrl, HtmlParser htmlParser)`.

### Core Rules

Your crawler must follow these steps:

- **Start** at the `startUrl`.
- **Use** `HtmlParser.getUrls(url)` to get all links from that page.
- **Avoid duplicates**: Do not visit the same URL more than once.
- **Check the Hostname**: Only follow links if the **hostname** matches the `startUrl`.
- Assume all links use `http` and do **not** use port numbers.

### Things to Clarify

- **URL Fragments**: Ask the interviewer about links with `#` (like `http://example.com/page#section1`). Should you treat them as the same page or a new page?
- **URL Normalization**: Ask if you need to clean up or standardise the URLs. Usually, you can assume this is not needed for the basic part.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
