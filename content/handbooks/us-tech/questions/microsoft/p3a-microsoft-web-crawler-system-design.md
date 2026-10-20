---
id: p3a-microsoft-web-crawler-system-design
section: microsoft
order: 612
level: A
title: "Microsoft AI / Copilot：MAI 分布式爬虫：调度、礼貌与去重"
quick: "分布式爬虫的 URL frontier 要按域名控制抓取速率和并发，并把下载、解析、去重和存储拆成彼此独立的阶段。"
companies:
  - microsoft
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · web-crawler-system-design"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/web-crawler-system-design
    type: secondary
---

## 题目

在压缩的时间里设计一条网页抓取流水线：从种子 URL 出发持续抓取，遵守网站的礼貌规则，对 URL 和内容去重，机器挂掉后能接着抓。

> 来源：一亩三分地 Microsoft 题卡摘要（2026-10-18 读取），属于网站对候选人报告的二手整理，没有逐条核对原帖，网站收录也不代表公司官方确认；规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

核心组件是 URL frontier，它决定下一个抓什么。frontier 要按域名分组，对每个域名单独控制速率和并发。下载、解析、去重和存储彼此解耦，各自可以独立扩容。

跨机器分片时，要避免多台机器同时打同一个域名造成突发过载，常见做法是按 hostname 分片，让一个域名只归一台调度器管。重试策略、robots 规则和内容去重是三件不同的事，要分别设计。

时间紧的时候，先用估算定住规模：每天抓多少页、平均每页多大，据此算出需要的吞吐和存储。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

练习设定：每天抓取一亿个页面，同一域名要礼貌限速，需要去重和断点续抓；面试只有 30 分钟，优先讲清核心流水线。

开场可以问：抓取范围是全网还是指定站点，页面需要多新鲜，是否需要渲染 JavaScript。

### 一套可展开的参考答案

**1. 架构与关键路径。** 一条 URL 依次经过：

1. URL frontier：按 hostname 分组排队。
2. 域调度器：决定这个域名现在能不能抓、能开几个连接。
3. fetch：下载页面。
4. parse：提取正文和新链接。
5. 规范化与去重：新链接规范化后去重，再回到 frontier。
6. 内容存储与索引。

robots 规则和每个域名的并发上限属于调度约束，要在调度器里执行，而不是只在 HTTP 客户端里设置。

**2. 数据模型和状态变化。** url 记录 (normalized, host, `seen_version`, `next_fetch`, status)；另有 `fetch_attempt`、`content_hash` 和 `host_budget`。URL 去重和内容去重分开做：两个不同的 URL 可能返回完全相同的内容，同一个 URL 不同时间的内容也可能变化。

**3. 追踪一个 URL。** `https://Example.com/a?utm=x` 先规范化为 `https://example.com/a`，查 url 表发现没见过，按 host 哈希进入 example.com 的子队列。调度器确认该域名的 robots 允许抓取、距上次抓取已超过最小间隔、当前并发未满，于是派给 fetcher。fetcher 下载后算出 `content_hash`，发现与库里另一个 URL 的内容相同，就只记录映射，不重复存正文；页面中的新链接各自规范化后进入 frontier。最后更新这个 URL 的 status 和 `next_fetch`。

**4. 失败、重复与恢复。** worker 失联后，它领走的任务按租约到期回收，交给别的 worker。重复抓取可以接受，但索引发布要幂等。慢域名放进隔离队列，避免拖住其他域名（队头阻塞）。遇到重定向时，对新地址重新检查域名规则和目标地址是否安全，例如是否指向内网。

**5. 容量和验证指标。** 一亿页每天，平均约 1157 页/秒；假设每页 100 KB，每天约 10 TB。衡量抓取新鲜度、成功率、违反域名礼貌规则的次数、内容重复率和队列年龄。

### 面试追问与参考回答

**分布式爬虫怎么判断已经结束？** 开放互联网的爬虫通常是持续运行的服务，用抓取预算和 frontier 状态来管理，而没有“结束”这一说。如果是有限任务，就要全局统计排队中和在途的 URL 数量都为零，不能因为某一台机器的队列空了就宣布结束。

**同一个域名突然变慢，会不会拖垮整个爬虫？** 不会，前提是 fetcher 不按 FIFO 死等。每个域名有独立的子队列和并发上限，慢域名只占用自己的配额；超时的连接释放回池，调度器转去服务其他域名。可以监控每个域名的平均响应时间，连续变慢时自动降低它的抓取速率。
