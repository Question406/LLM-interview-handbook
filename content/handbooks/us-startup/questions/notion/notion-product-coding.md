---
id: notion-product-coding
section: notion
order: 1
level: A
title: Notion：字符串的撤销重做，嵌套清单，再设计日历
quick: >-
  2025 年电面是字符串操作加 undo/redo，40 分钟做完。后面的算法轮是产品向的机器编码，清单要嵌套。
  同一天的设计题是日历。作者这轮没有 offer。
tags:
  - Notion
  - Coding
  - System Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Notion Interview Experience - 2025
    url: https://wildwildtech.substack.com/p/notion-interview-experience-2025
    type: candidate-first-hand
---

## 真题记录

Pritish Thakkar 2025 年写的 Notion SWE。筛选轮是 easy 到 medium 的字符串，加上 undo/redo，他 35 分钟写完，整轮大约 40–45 分钟。下一周同一天两轮：算法和系统设计。

算法不是力扣题，是贴近产品的机器编码。第一问他用 `ArrayList.add` 处理了边界。第二问要在树形结构里用父到子的下标做导航，他维护层级。面试官提示有更简单的导航，他没想到，被允许按自己的方案写完。

设计是日历。他写了功能和非功能、容量、实体、API 和一张简图。自己觉得表拆多了，变更没走 CDC，面试官追问不多。一周内面完，结果 No Hire。

帖子没有函数签名，也没有清单的完整需求。下面是按他描述能落地的写法，不是原文 API。

## 撤销重做

字符串编辑用两个栈。执行把逆操作压进 undo，redo 清空。undo 弹出并执行逆操作，同时把正向操作压进 redo。

```python
class Editor:
    def __init__(self):
        self.text = ""
        self.undo_stack = []
        self.redo_stack = []

    def insert(self, i, s):
        self.text = self.text[:i] + s + self.text[i:]
        self.undo_stack.append(("del", i, len(s)))
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        op = self.undo_stack.pop()
        if op[0] == "del":
            _, i, n = op
            deleted = self.text[i:i + n]
            self.text = self.text[:i] + self.text[i + n:]
            self.redo_stack.append(("ins", i, deleted))
```

删除要记住被删的子串，不然 redo 无法还原。帖子没说是插入删除还是整段替换。先问操作有哪几种，再为每种写逆操作。

## 嵌套清单

一块块内容，块可以有子块。他用父节点保存孩子下标。面试官说的更简单导航，一种可能是孩子保存父 id，移动和删除时少维护一整条下标数组。两种都能做。下标在中间插入时会失效，id 不会。若他卡在下标上，换 id 往往就是那个提示。

第一问若只是平铺追加，用列表。第二问再把节点换成 `{id, parent, children}`。不要一开始就写事务和协同编辑。

## 日历

实体就三个：用户、日历、事件。事件是 `[start, end)` 加上日历 id。创建时查同一日历里有没有重叠。API：创建、改时间、按窗口列出。

Startup 规模下，重叠查询用该日历的事件按开始时间排序再扫。不要先讲分库。循环事件是坑：面试里先说「展开到查询窗口」，不要现场写 RRULE 的全部语法。

他后悔的多表和 CDC：一个事件表就够。若有「即将开始」的通知，用时间轮或延迟队列读这张表，而不是每写一次就同步到第二张派生表。派生表要讲一致性，时间不够就别建。

## 追问

**undo 栈里存全文快照？** 能做，实现短。文本一长，复制变成每次编辑的成本。存逆操作更贴这轮「把边界写对」。

**两个人改同一块？** 这轮帖子没问。若加上，每块一个版本号，写入带期望版本，冲突则拒绝。不要展开成 CRDT，除非面试官点名。
