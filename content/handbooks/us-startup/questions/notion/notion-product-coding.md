---
id: notion-product-coding
section: notion
order: 1
level: A
title: Notion：字符串的撤销重做，嵌套清单，再设计日历
quick: >-
  2025 年这份 Notion 面经里，电面是字符串操作加 undo/redo，作者 35
  分钟写完，整轮四十来分钟。后面的算法轮是产品向的机器编码，清单要嵌套；同一天的设计题是日历，作者这轮没有 offer。撤销重做用两个栈存逆操作，嵌套清单用
  id 比下标稳，日历一张事件表就够。
tags:
  - Notion
  - Coding
  - System Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22T00:00:00.000Z
sources:
  - title: Notion Interview Experience - 2025
    url: 'https://wildwildtech.substack.com/p/notion-interview-experience-2025'
    type: candidate-first-hand
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现一个字符串编辑器的插入和撤销核心，使每次撤销恢复最近一次尚未撤销的插入。公开面经提到 undo/redo，但未披露完整操作表；本页可运行主练习与当前参考实现约定只覆盖 insert 与 undo，redo 是扩展讨论。

### 输入与接口

实现 Editor()，初始公开属性 text=""，undo_stack 与 redo_stack 均为空列表；提供 insert(i,s) 与 undo()。i 为当前字符串中合法的零基插入位置，0≤i≤len(text)；s 为字符串，按 Python 字符下标处理。

### 输出与约束

insert 在 i 之前插入 s，原 i 及之后内容右移，更新 text，记录可撤销历史，并清空 redo_stack；返回 None。undo 撤销最近一次尚未撤销的插入，恢复插入前 text，保存将来重做所需信息到 redo_stack；无可撤销操作时无副作用，返回 None。

撤销后再 insert 会开启新的编辑分支，之前的重做历史失效。无需实现删除、整段替换、协作编辑或持久化。可选 redo 扩展应恢复最近撤销的操作；可选嵌套清单讨论用稳定 id、父 id 和有序孩子表示节点，说明插入/导航/移动；可选日历讨论定义事件[start,end)及按窗口查询。公开帖缺失这些任务的完整业务规则，因此不把推测 API 当作主练习的测试要求。

### 示例

```text
editor=Editor()
insert(0,"ac") -> text="ac"
insert(1,"b") -> text="abc"
undo() -> text="ac"
insert(2,"d") -> text="acd"，redo_stack=[]
undo() -> text="ac"
undo() -> text=""
undo() -> text=""
```

## 解题思路与参考答案

这份 2025 年的 Notion 面经考了三样：电面是字符串操作加 undo/redo，算法轮是贴近产品的嵌套清单，设计题是日历。三道的写法都偏朴素，撤销重做用两个栈存逆操作，嵌套清单用 id 比用下标稳，日历一张事件表就够。

来源是 Pritish Thakkar 2025 年写的 Notion SWE 面经。筛选轮是 easy 到 medium 的字符串，加上 undo/redo，他 35 分钟写完，整轮大约 40–45 分钟。下一周同一天两轮，算法和系统设计。算法轮是贴近产品的机器编码，没出力扣题。第一问他用 `ArrayList.add` 处理了 edge cases；第二问要在树形结构里用父到子的下标做导航，他维护了层级。面试官提示有更简单的导航，他没想到，最后被允许按自己的方案写完。

设计题是日历。他写了功能和非功能需求、容量、实体、API 和一张简图，自己觉得表拆多了，变更也没走 CDC，面试官追问不多。一周内面完，结果 No Hire。帖子没有函数签名，也没有清单的完整需求，下面是按他的描述能落地的写法。

撤销重做我会用两个栈。执行一个操作时，把它的逆操作压进 undo，同时清空 redo；undo 时弹出并执行逆操作，再把正向操作压进 redo。

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
            deleted = self.text[i : i + n]
            self.text = self.text[:i] + self.text[i + n :]
            self.redo_stack.append(("ins", i, deleted))
```

删除要记住被删的子串，不然 redo 还原不了。比如在 "hello" 后面插入 " world" 再 undo，被删掉的 " world" 得存进 redo，redo 时才能插回去。帖子没说操作是插入删除还是整段替换，先问清有哪几种操作，再给每种写逆操作。

嵌套清单是一块块内容，块下面可以有子块。他用父节点保存孩子的下标。面试官说的更简单的导航，一种可能是让孩子保存父 id，移动和删除时就不用维护一整条下标数组。两种都能做，只是下标在中间插入时会失效，id 不会。如果他卡在下标上，换成 id 往往就是那个提示。第一问如果只是平铺追加，用列表就行，第二问再把节点换成 `{id, parent, children}`。事务和协同编辑一开始别写。

日历的实体就三个，用户、日历、事件。事件是 `[start, end)` 加日历 id，创建时查同一日历里有没有重叠。API 是创建、改时间、按窗口列出。Startup 规模下，重叠查询就把这个日历的事件按开始时间排序扫一遍，分库先别讲。循环事件是个坑，面试里先说「展开到查询窗口」，别现场写 RRULE 的全部语法。

他后悔的多表和 CDC，其实一个事件表就够了。要做「即将开始」的通知，就用时间轮或延迟队列读这张表，用不着每写一次就同步到第二张派生表。派生表要讲一致性，时间不够就别建。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

当前参考实现提供 insert 和 undo。先测插入、撤销和空栈撤销，再确认撤销后进行新编辑会清空 redo 历史；这里不调用尚未实现的 redo 方法。

```python
editor = Editor()
editor.insert(0, "ac")
editor.insert(1, "b")
assert editor.text == "abc"
editor.undo()
assert editor.text == "ac"
editor.insert(2, "d")
assert editor.text == "acd" and editor.redo_stack == []
editor.undo()
editor.undo()
editor.undo()
assert editor.text == ""
print("simple tests passed")
```

## 追问

**undo 栈里直接存全文快照行不行？**
能做，实现也短。可文本一长，每次编辑都要复制一遍全文。存逆操作更贴这轮「正确处理 edge cases」的考法。

**两个人改同一块怎么办？**
这轮帖子没问到。如果加上，每块一个版本号，写入时带上期望版本，冲突就拒绝。面试官没点名的话，别展开成 CRDT。
