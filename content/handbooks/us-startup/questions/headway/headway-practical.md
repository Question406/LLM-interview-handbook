---
id: headway-practical
section: headway
order: 1
level: A
title: Headway：找预约空档、按路由限流、小规模 Airbnb
quick: >-
  2025 年 5 月一位拿到 offer 的 SWE：电面是在已有预约里找一段足够长的空档。
  终面另一道编码是给若干 API 路由做限流。设计是 Airbnb 风格的应用，但按 startup 规模，考模型和 API，不考大架构。
tags:
  - Headway
  - Coding
  - System Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Headway Software Engineer, United States, 2025-05-01, offer
    url: https://www.jointaro.com/interviews/companies/headway/experiences/software-engineer-united-states-may-1-2025-accepted-offer-positive-96b077f6/
    type: candidate-first-hand
---

## 真题记录

Jointaro，2025 年 5 月 1 日，美国，Software Engineer，正面体验，拿到 offer。从招聘邮件到 offer 大约两到三周。

流程：招聘官问背景和求职意向；技术电面一道实用题，语言不限；终面可以一天做完或拆开，三块是系统设计、行为面、再一道编码。第二道编码必须用 Python 或 JavaScript，难度和电面接近。之后是两份 reference，以及你可以约的了解公司的会。

题面只有三句：

- 给定已有预约和一个时长，找最好的可预约时间。
- 给一些 API 路由实现限流。
- 设计一个 Airbnb 风格的应用，重点是 startup 规模下的建模和 API。

「最好」没有定义。行为面是普通的 tell me about a time。

## 预约空档

先问：工作时间、预约是否已排序、能不能贴着上一单的结束时刻开始、「最好」是最早、还是最靠近某个偏好时间。

我会假设预约是闭开区间，按开始时间排序，空档是上一单结束到下一单开始。长度至少为 `duration` 的空档里，取开始最早的那段，返回它的起点。

```python
def earliest(appts, duration, day_start, day_end):
    slots = sorted(appts)
    cursor = day_start
    for start, end in slots:
        if start - cursor >= duration:
            return cursor
        cursor = max(cursor, end)
    if day_end - cursor >= duration:
        return cursor
    return None
```

重叠的预约要先合并，否则中间会算出负的空档。合并是排序后扫一遍，不是这题的难点，不合并会被一组重叠数据打挂。

## 限流

问清：按路由、按用户，还是按两者；限制是每秒多少次；超了返回什么。多条路由不要共用一个计数器。

单机面试用滑动窗口：每个 key 一个队列，存时间戳，请求时丢掉窗口外的戳，队列长度到上限就拒绝。令牌桶要讲补充速率。分布式再加「计数放 Redis，用 lua 保证读和加在一起」。Headway 这轮和电面一样，先把单机写跑。

Key 我会用 `route + user`。只按 IP，NAT 后面会误伤。

## Airbnb，startup 规模

三张核心：用户、房源、预订。预订是 `[check_in, check_out)` 加房源 id。同一房源日期重叠则创建失败。搜索是城市加日期，返回该城市里没有重叠预订的房源。

API：创建房源、搜索、创建预订、取消。创建预订在事务里再查一次重叠。两个人同时订同一天，只靠应用层先查后插会双订。

规模停在这里。一个地区一个数据库，预订表按房源 id 索引。不要讲多区域复制，除非面试官把 QPS 加到那个程度。作者写这轮要的就是模型和 API。

## 追问

**空档要避开午休？** 把午休当成一条已有预约放进列表再跑同一函数。不要在扫描里写死 12 点。

**限流的边界算不算一次？** 窗口是闭开还是滑动，用一个刚好落在边界上的时间戳和面试官对一下。差一毫秒会和他们的测试不一致。

**取消预订之后搜索要立刻可见？** 取消把预订标成 cancelled，搜索时过滤。软删比物理删好讲，纠纷时还查得到。
