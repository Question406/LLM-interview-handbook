---
id: anthropic-inmemory-db
section: anthropic
order: 1
level: A
title: Anthropic：实现带 TTL 的内存数据库，后续怎么加备份和并发？
quick: >-
  第一层用 map 做 CRUD。TTL 不要扫全表：过期堆 + 惰性删除。备份是某时刻的一致快照，不是把 dict
  浅拷贝出去。后面再加的 backup/restore、账户合并、并发，全靠第一层接口没把时间戳和存储细节漏出去。
tags:
  - Anthropic
  - Coding
  - TTL
  - Systems
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
  - title: Anthropic SDE OA — Memory Database and Bank System
    url: https://programhelp.net/en/oa/anthropic-sde-oa-interview-guide/
    type: secondary
---

## 真题记录

- 公司：Anthropic
- 岗位：SWE / 部分 RE 的 CodeSignal 或现场编码
- 来源：IGotAnOffer 汇总的高频题；OA 拆解文把「Memory Database（TTL + backup/restore）」和「Bank System」列为分层解锁题
- 形态：90 分钟、4 层，前一层单测不过后一层不开放

这题难在层数和时钟，不在单层算法。第一层把 `get/set` 写成无时间参数的 dict，第三层 TTL 就只能推倒重来。

## 第一层：接口先带时间

值保存 `(value, expire_at | None)`。所有读路径走同一个 `now`：OA 里时间是命令里的整数时间戳，不要用墙上时钟，否则单测不可复现。

过期策略：

- **惰性：** `get` / `scan` 时丢弃过期键。写路径简单。
- **主动：** min-heap `(expire_at, key)`，推进时间时弹出。避免「只写不读，内存被过期键撑死」。

生产两个都要。面试至少实现惰性，并说出主动回收。过期堆要处理「同一 key 被续期」：堆里会有旧时间戳，弹出时核对当前 `expire_at`，不匹配就跳过。

## 备份：深拷贝一份已过滤快照

Backup 不是 `dict.copy()`。要：

1. 按当前 `now` 丢掉过期键；
2. 拷贝 value，可变对象要 deepcopy；
3. restore 覆盖整个命名空间，还是 merge，题目会规定，默认整库替换；
4. 快照里存的是绝对过期时间还是剩余 TTL？绝对时间更简单；若 restore 发生在「时间已推进」之后，绝对过期可能让整份备份立刻失效。剩余 TTL 更合理，restore 时 `expire_at = now + remaining`。

面试里把这句说出来，比把 backup 写成 `self.data = snapshot` 更像用过带 TTL 的缓存。

## 后面几层别把状态塞进调用方

Bank 变体（开户、转账、合并、cashback）和 DB 变体共享一件事：余额 / 版本号放在记录里，操作返回成功或失败，不要抛半更新。转账：先检查两账户都在、金额非负、源余额足够，再改两处。合并账户要定义主键谁留下、历史 cashback 怎么并。

并发 follow-up：单线程 OA 不考锁，但现场会问。每键一把锁再加全局顺序（按 account id 排序加锁）避免 AB/BA 死锁。`setAll` 或全表 backup 需要停写或 copy-on-write 版本号，不能在遍历时被 set 改掉。

## 追问

- **TTL 用 Redis 的那种 expire 命令模型还是滑动窗口？** 先实现绝对过期。滑动 TTL 每次 get 续期，heap 更新更烦，当 follow-up。
- **为什么不每秒全表扫描？** $O(n)$ 唤醒。过期堆是 $O(\log n)$ 插入，$O(k)$ 弹出到期的 $k$ 个键。
- **和计算机使用 / 工具超时的关系？** 同一类状态机：每个资源有 deadline，过期后行为要确定，不能「偶发读到旧值」。工具超时见 computer-use 章。
