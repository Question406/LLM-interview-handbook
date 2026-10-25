---
id: ali-be-mysql-mvcc
section: alibaba-oa
order: 57
level: S
title: 阿里研发面：InnoDB MVCC、redo/undo/binlog 怎么串？
quick: >-
  MVCC 用 Read View 判断一个行版本对当前事务是否可见，看不见就沿 undo 链往回找历史版本，所以大多数读不加锁。redo 用于崩溃恢复，undo 用于回滚和 MVCC，binlog 用于复制和备份；提交时 redo 和 binlog 走内部两阶段提交，保证两边状态一致。
tags:
  - Alibaba
  - MySQL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

InnoDB 用 MVCC 让大多数读不加锁：每行带着最后修改它的事务号和指向上一版本的 undo 指针，读的时候用 Read View 判断哪个版本可见。三条日志分工不同：redo 保证已提交的事务崩溃后不丢，undo 负责回滚并提供历史版本，binlog 给复制和备份用。提交时 redo 和 binlog 要通过内部两阶段提交保持一致。这是阿里校招 MySQL 部分的题。

具体来说，每行藏着 `trx_id`（最后改它的事务）和 `roll_ptr`（指向 undo 里的上一个版本）。读的时候构造 Read View，里面记着当前活跃事务 ID 的集合和上下水印。可见性规则三句话就能说完：自己的改动可见；别人没提交的不可见；在 Read View 建立之后才提交的事务，在 RR 下也不可见。所以同一行可以同时存在多个历史版本，读走 undo 链，写才加锁。

redo 是物理日志，记的是页被怎么改，崩溃后重放，保证已提交事务不丢。undo 是逻辑日志，既能回滚未提交的事务，又是 MVCC 的版本链。binlog 是 Server 层的逻辑日志，给主从复制和备份用，InnoDB 自己做崩溃恢复不靠它。事务提交时，InnoDB 内部先写 redo，再和 binlog 做两阶段提交，避免「binlog 有、引擎没有」或者反过来，否则主从会分叉。

| | redo | undo | binlog |
| --- | --- | --- | --- |
| 层级 | InnoDB | InnoDB | Server |
| 用途 | 崩溃恢复 | 回滚 + MVCC | 复制、时间点恢复 |
| 形态 | 物理页改动 | 逻辑反向操作 | 逻辑行 / 语句 |
| 丢了会怎样 | 提交成功也可能丢（看刷盘） | 长事务 / 读旧版本失败 | 主从断层 |

隔离级别上，RC 每条语句新建 Read View，能看到语句开始前已经提交的更新，所以仍有不可重复读。RR 在事务第一次读时建 View，之后一直用它，配合 MVCC 解决大部分不可重复读。RR 下的幻读要靠 **next-key 锁**（记录锁 + 间隙锁）堵住写入，间隙锁锁的是索引记录之间的空隙，防的就是幻插入。面试里说「RR 防幻读全靠 MVCC」会扣分。

刷盘参数也要讲。`innodb_flush_log_at_trx_commit=1` 每次提交刷 redo，`sync_binlog=1` 每次提交刷 binlog，双 $1$ 最安全，也最慢。双十一有人会改成 $2$ 换吞吐，代价是宕机可能丢最后一秒。口述时要把性能和会丢多少一起说出来。

## 放到阿里的场景里

比如在 RR 下开一个事务导出订单列表，期间别的事务不断插入新单。导出事务的 Read View 看不到这些新单，这是 MVCC 的预期行为，没有丢单。可如果导出用的是 `SELECT ... FOR UPDATE` 扫一个范围，就会加上间隙锁，下单插入被堵住，大促时这就是事故。只读报表用普通一致读，要锁库存行才用当前读。

主从延迟也要和日志串起来讲：binlog 没及时送到从库，读从库就会读到旧库存。交易里写完马上要读的，走主库，或者用「写后读自己的位点」。崩溃恢复的过程是：机器掉电，redo 重放把脏页补齐，undo 把未提交事务滚掉，binlog 位点决定从库从哪里接着同步。对账发现主库有单、从库没有，先查提交时 binlog 有没有刷盘、中途有没有切主。

长事务的运维风险很大。一个没提交的后台任务拿着旧 Read View，undo 就清不掉，ibd 膨胀、purge 落后，最后把磁盘打满；它还会带来锁等待、主从延迟，把 DDL 堵住。下单链路的事务要短：算出价、写行、提交，别在事务里调 HTTP。

## 追问

**当前读和快照读差在哪？**
普通 `SELECT` 是快照读，走 MVCC；`SELECT FOR UPDATE` / `UPDATE` 是当前读，读最新版本并加锁。

**redo 和 binlog 谁先落盘？**
prepare redo → 写 binlog → commit redo，靠内部 XA 串起来。

**`trx_id` 是主键吗？**
不是。它是事务号，和行主键没关系。

**更新时不改索引列，会不会加 next-key 锁？**
主要加行锁，范围条件才容易加上间隙锁。

**怎么看一个事务持有什么锁？**
查 `performance_schema` / `information_schema.innodb_trx`，再对一下死锁日志。
