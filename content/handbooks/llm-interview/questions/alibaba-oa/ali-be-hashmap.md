---
id: ali-be-hashmap
section: alibaba-oa
order: 52
level: A
title: 阿里研发面：HashMap 和 ConcurrentHashMap 的结构差异？
quick: "HashMap 使用数组加链表或红黑树，扩容通常翻倍，JDK 8 改为尾插。ConcurrentHashMap 用桶级 CAS 与 synchronized 支持并发写，不锁整个表；计数通过 CounterCell 分散累加。单次操作线程安全，不代表先 get 再 put 这样的组合操作也是原子的。"
tags:
  - Alibaba
  - HashMap
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

## 真题记录

- 岗位：阿里校招 Java

## 定义

`HashMap` 是数组上的哈希表。下标我一般这么算：先扰动再掩码，`(h ^ (h >>> 16)) & (n - 1)`，高位也参与，容量必须是 $2$ 的幂。冲突后同一桶用链表串起来；JDK 8 在链长超过树化阈值、且容量达到最小树化容量时，把链表升级成红黑树，最坏查找从 $O(n)$ 压到 $O(\log n)$。负载因子默认 $0.75$，超过就扩容到两倍。扩容时按原哈希的「更高一位」决定去留：该位为 $0$ 留在原下标，为 $1$ 搬到 `i + oldCap`，不必重算完整哈希。

`ConcurrentHashMap` 对外是「分段并发的哈希表」：读基本无锁，写在桶头用 CAS 占位，桶上已有节点再用 `synchronized` 锁住桶头（JDK 8）。没有 Hashtable 那种整表锁，也没有 JDK 7 那种 Segment 数组。`size` 不是每次遍历全表，而是用 `CounterCell` 做分核累加，减少热点。它保证单次 `put/get` 的线程安全，不保证复合操作（先 get 再 put）的原子性，复合仍要外层同步或用 `computeIfAbsent`。

## 对比 / 分层

| | HashMap | ConcurrentHashMap | Hashtable |
| --- | --- | --- | --- |
| 并发 | 无，多线程扩容会坏 | 桶级 CAS + 锁 | 方法级整表锁 |
| 空键空值 | 允许一个 `null` key | 不允许 `null` | 不允许 `null` |
| 扩容 | 单线程 rehash | 多线程协助迁移 | 整表锁住扩 |
| 迭代 | fail-fast | 弱一致，不抛 CME | 枚举偏老 |
| 选用 | 单线程、请求内局部 Map | 共享缓存、计数、去重 | 基本不推荐 |

我记三件事。JDK 7 头插在并发扩容时可能成环，JDK 8 改尾插是正确性修复，不是性能炫技。树化不能解决所有问题：哈希分布差、容量太小仍会增加冲突，所以扰动函数和容量幂次都重要。`key` 的 `hashCode` / `equals` 必须稳定；用可变对象当 key，改字段后会丢映射，表现为「明明 put 过却 get 不到」。

`LinkedHashMap` 在 HashMap 上加访问顺序，可做 LRU；`TreeMap` 是红黑树有序表，不是同一条赛道。面试只在被追问「有序 Map」时展开。

## 阿里场景

请求内组装订单明细、优惠计算结果，用普通 `HashMap` 即可；无锁争用时别上 CHM，更重。跨请求共享的本地缓存，例如一个商家的运费模板、一个会场的活动规则，用 CHM。统计「这个 SKU 被浏览了多少次」可以用 `CHM.compute` 或 `LongAdder`，不要 `get` 出来 `+1` 再 `put`，那会丢计数。

真实事故形态：有人用 HashMap 做「用户 ID → 会话」的全局表，大促一来偶发 CPU 打满，堆里能看到环形链表，典型 JDK 7 死循环；升级到 8 后更多是数据错乱而不是死循环。另一个阿里味很浓的坑是把实体对象当 key，中间被 ORM 改了字段，缓存「消失」。商品 ID、订单号这类不可变字符串或 Long 才适合当 key。

扩容时机也要讲：预估会场商品量就在构造时指定容量，避免活动开始瞬间连续扩容。CHM 扩容时其他线程会帮忙搬桶，所以高峰写入会看到短暂 CPU 抬升，这是协助迁移，不是泄漏。

## 追问

- 为什么容量是 $2$ 的幂？用位运算代替取模，扩容位移也简单。
- 树化阈值为什么是 $8$、退化是 $6$？避免在 $7/8$ 附近来回抖动。
- CHM 的 `get` 要不要加锁？不锁，依赖 volatile / 有序写入，读到的是某次完成写入后的值。
- `size()` 精确吗？是近似到最终一致的计数，不适合当精确库存。
- 如何实现「不存在才放入」？`putIfAbsent` 或 `computeIfAbsent`，不要自己先 `containsKey`。
- 哈希冲突被恶意打满怎么办？键可控时限制输入空间；不可控时考虑随机种子的哈希或改用带扰动的实现。
- `Hashtable` 为什么慢？整表锁，读也被挡住，现代代码用 CHM 替换。
