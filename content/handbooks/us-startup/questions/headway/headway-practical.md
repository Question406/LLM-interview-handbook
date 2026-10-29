---
id: headway-practical
section: headway
order: 1
level: A
title: Headway：找预约空档、按路由限流、小规模 Airbnb
quick: >-
  2025 年 5 月一位拿到 offer 的 Headway SWE 写，电面是在已有预约里找一段足够长的空档，终面另一道编码是给若干 API
  路由做限流。设计是 Airbnb 风格的应用，按 startup 规模，考模型和 API，不考大架构。三道都先问清定义，再写一个单机能跑的版本。
tags:
  - Headway
  - Coding
  - System Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22T00:00:00.000Z
sources:
  - title: 'Headway Software Engineer, United States, 2025-05-01, offer'
    url: >-
      https://www.jointaro.com/interviews/companies/headway/experiences/software-engineer-united-states-may-1-2025-accepted-offer-positive-96b077f6/
    type: candidate-first-hand
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

本页包含预约空档、API 限流和小规模房源预订三个场景。可运行主练习是预约空档：给定一天的可工作区间和已有预约，找能容纳指定时长的新预约的最早起点。公开面经没有完整接口，以下规则是重构练习约定。

### 输入与接口

实现 earliest(appts,duration,`day_start`,`day_end`)。时间用同一单位的整数表示；`day_start`<`day_end`，duration 为正数。appts 是 (start,end) 列表，均位于当天工作区间且 start<end；列表可未排序、可重叠或嵌套。所有预约按左闭右开区间 [start,end) 占用时间。

### 输出与约束

返回最早可行起点 t，使 [t,t+duration) 完全位于 [`day_start`,`day_end`) 且不与已有预约重叠；不存在返回 None。新预约可以紧贴既有预约的结束时刻，结束也可以恰好等于下一预约开始或 day_end。不修改输入。

另两项为讨论任务，不要求在 earliest 中实现：为每个(route,user)定义窗口内最多 L 个已接受请求，窗口约定(now-W,now]，超额拒绝；请求时间单调，拒绝请求不入窗口。房源系统需给出用户、房源、预订数据模型及创建房源、城市和日期搜索、创建/取消预订接口；预订日期为[`check_in`,`check_out`)，同房源有效预订不得重叠，取消后可重新预订。上述 rate-limiting 与 booking conventions 是练习约定。

### 示例

```text
earliest([(10,20)],10,0,30) -> 0
earliest([(0,10),(20,30)],10,0,30) -> 10
earliest([(0,20),(5,10)],10,0,30) -> 20
earliest([(0,30)],1,0,30) -> None
限流讨论样例：L=2、W=10，同key在t=0、1接受，在t=2拒绝，在t=10接受（t=0已过期）
```

## 解题思路与参考答案

Headway 公开的三道题都很实用：电面在已有预约里找一段足够长的空档，终面给若干 API 路由做限流，设计是 startup 规模的 Airbnb。每道都先把「最好」指什么、按什么限、规模多大问清楚，再写一个单机能跑的版本。

来源是 Jointaro 上 2025 年 5 月 1 日一份美国 Software Engineer 面经，正面体验，拿到了 offer，从招聘邮件到 offer 大约两到三周。招聘官先问背景和求职意向。技术电面是一道实用题，语言不限。终面可以一天做完也可以拆开，三块是系统设计、行为面，再加一道编码；第二道编码必须用 Python 或 JavaScript，难度和电面接近。之后是两份 reference，以及你可以约的了解公司的会。行为面是普通的 tell me about a time。

题面只有三句：给定已有预约和一个时长，找最好的可预约时间；给一些 API 路由实现限流；设计一个 Airbnb 风格的应用，重点是 startup 规模下的建模和 API。「最好」没有定义。

预约空档这题，我会先问工作时间、预约是否已排序、能不能贴着上一单的结束时刻开始，还有「最好」是最早，还是最靠近某个偏好时间。然后假设预约是闭开区间、按开始时间排序，空档就是上一单结束到下一单开始。在长度至少为 `duration` 的空档里，取开始最早的那段，返回它的起点。

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

重叠的预约要先合并，否则中间会算出负的空档。合并就是排序后扫一遍，不是这题的难点，可不合并会被一组重叠数据打挂。

限流先问清是按路由、按用户，还是两者都按，限制是每秒多少次，超了返回什么。多条路由别共用一个计数器。单机面试用滑动窗口，每个 key 一个队列存时间戳，请求进来先丢掉窗口外的戳，队列长度到上限就拒绝。用令牌桶的话要讲补充速率。到分布式再加一句「计数放 Redis，用 lua 保证读和加在一起」。Headway 这轮和电面一样，先把单机写跑。Key 我会用 `route + user`，只按 IP 的话，NAT 后面会误伤。

Airbnb 这题核心就三张表：用户、房源、预订。预订是 `[check_in, check_out)` 加房源 id，同一房源日期重叠就创建失败。搜索按城市加日期，返回这个城市里没有重叠预订的房源。API 有创建房源、搜索、创建预订、取消。创建预订要在事务里再查一次重叠，两个人同时订同一天，只靠应用层先查后插会双订。

规模就停在这里，一个地区一个数据库，预订表按房源 id 建索引。面试官没把 QPS 加到那个程度，就别讲多区域复制。作者写了，这轮要的就是模型和 API。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用整数表示分钟。检查刚好放得下、完全没空、无预约，以及相互重叠的预约不会把 cursor 往回推。

```python
assert earliest([(10, 20)], 10, 0, 30) == 0
assert earliest([(0, 10), (20, 30)], 10, 0, 30) == 10
assert earliest([(0, 30)], 1, 0, 30) is None
assert earliest([], 30, 0, 30) == 0
assert earliest([(0, 20), (5, 10)], 10, 0, 30) == 20
print("simple tests passed")
```

## 追问

**空档要避开午休怎么办？**
把午休当成一条已有预约放进列表，再跑同一个函数。别在扫描里写死 12 点。

**限流 window endpoints 上的事件是否计数？**
用一个刚好位于 window endpoint 的 timestamp 和面试官对一下，确认窗口是闭开还是滑动。差一毫秒就会和他们的测试不一致。

**取消预订之后，搜索要立刻可见吗？**
取消时把预订标成 cancelled，搜索时过滤掉，就能马上生效。软删比物理删好讲，有纠纷时还查得到。
