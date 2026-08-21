---
id: ali-be-mysql-mvcc
section: alibaba-oa
order: 57
level: S
title: 阿里研发面：InnoDB MVCC、redo/undo/binlog 怎么串？
quick: >-
  MVCC 用 undo 链 + Read View 读历史版本。redo 保崩溃恢复，undo 回滚/MVCC，binlog 保复制和备份。两阶段提交让 redo 与 binlog 一致。
tags:
  - Alibaba
  - MySQL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

## 真题记录

- 岗位：阿里校招 MySQL

## 定义

InnoDB 用 MVCC 让读大多不加锁。每行藏着 `trx_id`（最后改它的事务）和 `roll_ptr`（指向 undo 里的上一个版本）。读的时候构造 Read View：里面记着「当前活跃事务 ID 集合」和上下水印。可见性规则口述成三句：自己的改动可见；未提交的别人不可见；在 Read View 建立之后才提交的事务，在 RR 下也不可见。于是同一行可以同时存在多个历史版本，读走 undo 链，写才加锁。

三条日志分工不同。redo 是物理日志，记下页被怎么改，crash 后重放，保证已提交事务不丢。undo 是逻辑日志，既能回滚未提交事务，又是 MVCC 的版本链。binlog 是 Server 层逻辑日志，给主从复制和备份用，InnoDB 自己恢复不靠它。事务提交时 InnoDB 内部先写 redo，再和 binlog 做内部两阶段提交，避免「binlog 有、引擎没有」或反过来，否则主从会分叉。

## 对比 / 分层

| | redo | undo | binlog |
| --- | --- | --- | --- |
| 层级 | InnoDB | InnoDB | Server |
| 用途 | 崩溃恢复 | 回滚 + MVCC | 复制、时间点恢复 |
| 形态 | 物理页改动 | 逻辑反向操作 | 逻辑行 / 语句 |
| 丢了会怎样 | 提交成功也可能丢（看刷盘） | 长事务 / 读旧版本失败 | 主从断层 |

隔离级别分层：RC 每条语句新建 Read View，所以能看到语句开始前已提交的更新，仍有不可重复读。RR 在事务第一次读时建 View，之后保持，配合 MVCC 解决大部分不可重复读。幻读在 RR 下靠 **next-key 锁**（记录锁 + 间隙锁）堵写入，不是单靠 MVCC。很多人把「RR 防幻读」全算到 MVCC 头上，这是扣分点。

刷盘分层：`innodb_flush_log_at_trx_commit=1` 每次提交刷 redo，`sync_binlog=1` 每次提交刷 binlog，双 $1$ 最安全、最慢。双十一有人会改成 $2$ 换吞吐，接受宕机丢最后一秒。口述必须把「性能」和「丢多少」一起说。

## 阿里场景

订单列表在 RR 下打开一个事务做导出，期间别的事务不断插入新单。导出事务的 Read View 看不到这些新单，这是 MVCC 的预期，不是丢单。如果导出用的是 `SELECT ... FOR UPDATE` 扫一个范围，会加上间隙锁，下单插入会被堵住，大促时这就是事故。只读报表用普通一致读；真正要锁库存行才用当前读。

主从延迟也要串日志：binlog 没及时送到从库，读从库会读到旧库存。交易里「写后立刻读」要走主库或用写后读自己的位点。crash 恢复故事：机器掉电，redo 重放把脏页补齐，undo 把未提交事务滚掉，binlog 位点决定从库从哪续。对账发现主库有单、从库没有，优先查提交时 binlog 是否刷盘、是否中途切主。

长事务是阿里 DBA 高压线。一个没提交的后台任务拿着旧 Read View，undo 不能清，ibd 膨胀，purge 落后，最后把磁盘打满。下单链路事务要短：算出价、写行、提交，不要在事务里调 HTTP。

## 追问

- 当前读和快照读差在哪？`SELECT` 走 MVCC；`SELECT FOR UPDATE` / `UPDATE` 走最新版本并加锁。
- 间隙锁锁的是什么？索引记录之间的空隙，防幻插入。
- 为什么长事务危险？undo 堆积、锁等待、主从延迟、DDL 被堵。
- redo 和 binlog 谁先落盘？prepare redo → 写 binlog → commit redo，靠内部 XA。
- `trx_id` 是主键吗？不是，是事务号，和行主键无关。
- 更新不改索引列会不会加 next-key？主要加行锁；范围条件才容易间隙锁。
- 如何看事务持有什么锁？`performance_schema` / `information_schema.innodb_trx`，再对死锁日志。
