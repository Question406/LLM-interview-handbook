---
id: anthropic-bank-oa
section: anthropic
order: 4
level: A
title: Anthropic OA：银行账户 / 转账后续，接口如何从内存库长出来？
quick: >-
  和内存库同一套分层纪律：时间从外面传，状态放记录里，操作要么整笔成功要么整笔失败。余额别做成裸 int，先留交易日志，后面的 top-K
  流出、预约转账、合户才接得上。
tags:
  - Anthropic
  - Coding
  - OA
  - Systems
realInterview: false
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

公开面经把银行系统和内存库并列成 CodeSignal 分层题，不是某一帖的独家题面。我会把它当成 `anthropic-inmemory-db` 的同一套接口课：第一层如果把账户做成 `id -> 余额`，第三层预约转账和第四层合户一定推倒重来。

## 时间、失败、日志，三个东西第一层就要在

OA 的时间是命令里的整数时间戳，不要用墙上时钟。所有会改余额的路径走同一个 `now`，和 TTL 那题一样。

记录至少要能回答：这笔钱从哪来、到哪去、什么时候、算不算流出。第一层我不会只写 `balances[id] += x`。最小形状：

```python
class Bank:
    def __init__(self):
        self.acct = {}          # id -> {bal, out, txs, pending}

    def deposit(self, now, aid, amt):
        if amt <= 0 or aid not in self.acct:
            return False
        a = self.acct[aid]
        a["bal"] += amt
        a["txs"].append(("D", now, amt, None))
        return True

    def transfer(self, now, src, dst, amt):
        if amt <= 0 or src == dst:
            return False
        a, b = self.acct.get(src), self.acct.get(dst)
        if a is None or b is None or a["bal"] < amt:
            return False
        a["bal"] -= amt
        b["bal"] += amt
        a["out"] += amt
        a["txs"].append(("T-", now, amt, dst))
        b["txs"].append(("T+", now, amt, src))
        return True
```

转账先检查再改两处。半更新是这题最快的挂法。金额非负、账户存在、源余额足够，三条全过才动。

## 后几层是接口长出来的，不是新写一题

公开拆解里层序不完全一样，常见四截：

1. 开户 / 存款 / 余额。
2. 转账、支付；有的版本要按流出总量做 top-K。
3. 预约未来转账、取消；有的版本是合户。
4. 合户，或 cashback / top spenders。

我会按「最贵的后续」预留，而不是猜某一版的函数名。

**流出 top-K：** 转账时累加 `out`。查询时按 `out` 排序，平局用题目规定的 id 序。不要每次从全日志扫。

**预约：** 和 TTL 过期堆同一结构。`(execute_at, tx_id)` 进 min-heap，推进 `now` 时弹出到期的。取消用 tombstone：弹出后核对 `pending[tx_id]` 还在。执行时走同一条 `transfer`，余额不够就按题目：失败并丢掉，还是留着下次再试。默认失败并清掉，行为要确定。

**合户：** 先定谁留下。余额相加，`out` 相加，日志拼接，pending 里指向被删 id 的改成留下的 id。被删 id 以后所有操作返回失败。有的题要求「历史仍按原账户可查」，那日志要带 `orig_id`，合户只改活余额，不改历史主键。

Cashback 跟支付绑在一起：支付时记下应返比例，结算时间到了再 `deposit` 一笔内部入账。合户要把未结算 cashback 一起搬走，否则第四层会跟第二层打架。

## 别把状态塞进调用方

接口返回成功 / 失败，不要抛一半。调用方不持有余额副本。并发 follow-up 单线程 OA 不考，现场会问：两把账户锁按 id 排序加，避免 AB/BA 死锁；全表 backup / top-K 要么停写，要么 copy-on-write 版本号。

## 追问

- **和内存库差在哪？** 内存库是单键 TTL；银行是两账户原子更新加时间序副作用。堆、惰性过期、快照这三件可以直接搬。
- **转账要不要事务 id？** 预约和幂等需要。同一 `tx_id` 重放必须是 no-op，否则网络重试会双花。
- **合户后 top-K 用谁的流出？** 默认并到留下的 id。如果题目要「历史排名不变」，流出按发生时的账户冻结，合户后只影响未来。
- **余额用 float 吗？** 面试用整数分。float 累加对 cashback 百分比不稳，说一句就够。
