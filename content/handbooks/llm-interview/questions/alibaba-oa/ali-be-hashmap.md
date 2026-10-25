---
id: ali-be-hashmap
section: alibaba-oa
order: 52
level: A
title: 阿里研发面：HashMap 和 ConcurrentHashMap 的结构差异？
quick: "HashMap 是数组加链表或红黑树，扩容翻倍，JDK 8 改成尾插。ConcurrentHashMap 在桶上用 CAS 和 synchronized 支持并发写，不锁整表，计数用 CounterCell 分散累加。单次操作线程安全，先 get 再 put 这样的组合操作仍然不是原子的，要用 computeIfAbsent 这类方法。"
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

两者底层都是数组上的哈希表，冲突用链表串、链太长转红黑树，差别在并发。`HashMap` 不做任何同步，多线程扩容会出问题；`ConcurrentHashMap`（JDK 8）写的时候在桶头用 CAS 或 `synchronized`，只锁一个桶。这道是阿里校招 Java 面的题。

先说 `HashMap` 的下标怎么算。先扰动再掩码：`(h ^ (h >>> 16)) & (n - 1)`，让高位也参与，所以容量必须是 $2$ 的幂。冲突后同一桶用链表串起来；JDK 8 在链长超过树化阈值、并且容量达到最小树化容量时，把链表升级成红黑树，最坏查找从 $O(n)$ 压到 $O(\log n)$。负载因子默认 $0.75$，超过就扩容到两倍。扩容时看原哈希的「更高一位」：这一位为 $0$ 留在原下标，为 $1$ 搬到 `i + oldCap`，不用重算完整哈希。

树化也解决不了所有问题，哈希分布差、容量太小，冲突照样多，所以扰动函数和容量幂次都重要。`key` 的 `hashCode` / `equals` 必须稳定；用可变对象当 key，改了字段以后映射就丢了，表现为「明明 put 过却 get 不到」。JDK 7 头插在并发扩容时可能成环，JDK 8 改成尾插是正确性修复，和性能无关。

`ConcurrentHashMap` 读基本无锁。写的时候桶为空就用 CAS 占位，桶上已有节点再用 `synchronized` 锁住桶头。它没有 Hashtable 那种整表锁，也没有 JDK 7 那种 Segment 数组。`size` 用 `CounterCell` 做分核累加，不用每次遍历全表，也减少了热点。它保证单次 `put/get` 线程安全，复合操作（先 get 再 put）不保证原子，要外层同步，或者用 `putIfAbsent` / `computeIfAbsent`，别自己先 `containsKey`。`Hashtable` 是方法级的整表锁，读也会被挡住，现代代码都用 CHM 替换它。

| | HashMap | ConcurrentHashMap | Hashtable |
| --- | --- | --- | --- |
| 并发 | 无，多线程扩容会坏 | 桶级 CAS + 锁 | 方法级整表锁 |
| 空键空值 | 允许一个 `null` key | 不允许 `null` | 不允许 `null` |
| 扩容 | 单线程 rehash | 多线程协助迁移 | 整表锁住扩 |
| 迭代 | fail-fast | 弱一致，不抛 CME | 枚举偏老 |
| 选用 | 单线程、请求内局部 Map | 共享缓存、计数、去重 | 基本不推荐 |

`LinkedHashMap` 在 HashMap 上加了访问顺序，可以拿来做 LRU；`TreeMap` 是红黑树有序表，属于另一类东西，被追问「有序 Map」时再展开。

## 放到阿里的场景里

请求内组装订单明细、优惠计算结果，用普通 `HashMap` 就够，没有锁争用就别上 CHM，它更重。跨请求共享的本地缓存，比如一个商家的运费模板、一个会场的活动规则，用 CHM。统计「这个 SKU 被浏览了多少次」可以用 `CHM.compute` 或 `LongAdder`；`get` 出来 `+1` 再 `put` 会丢计数。

常见的事故形态有两种。一种是有人用 HashMap 做「用户 ID → 会话」的全局表，大促一来偶发 CPU 打满，堆里能看到环形链表，这是典型的 JDK 7 死循环；升级到 8 以后更多表现为数据错乱。另一种是把实体对象当 key，中间被 ORM 改了字段，缓存就「消失」了。商品 ID、订单号这类不可变的字符串或 Long 才适合当 key。

容量也要提前想：预估会场商品量，构造时就指定容量，避免活动开始那一刻连续扩容。CHM 扩容时其他线程会帮忙搬桶，所以高峰写入会看到短暂的 CPU 抬升，这是协助迁移，和泄漏无关。

## 追问

**为什么容量是 2 的幂？**
可以用位运算代替取模，扩容时按一位决定去留也简单。

**树化阈值为什么是 8，退化是 6？**
中间留出空档，避免在 $7/8$ 附近来回树化、退化。

**CHM 的 `get` 要不要加锁？**
不加。它依赖 volatile 和有序写入，读到的是某次完成写入后的值。

**`size()` 精确吗？**
不精确，是近似、最终一致的计数，不适合当精确库存。

**哈希冲突被恶意打满怎么办？**
键可控时限制输入空间；不可控时考虑带随机种子的哈希，或者改用带扰动的实现。
