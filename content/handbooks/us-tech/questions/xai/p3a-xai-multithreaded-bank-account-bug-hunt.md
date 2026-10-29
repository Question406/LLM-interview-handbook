---
id: p3a-xai-multithreaded-bank-account-bug-hunt
section: xai
order: 615
level: A
title: xAI：BankAccount 并发调试与包装修复
quick: >-
  我会用同一把锁覆盖所有余额方法的完整检查、读取和更新，deposit、withdraw 和 balance
  都不能绕开它。不改原类时用包装类，并避免暴露内部对象；GIL 不能代替业务临界区，多进程或多机要换相应同步方式。
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · xAI · multithreaded-bank-account-bug-hunt
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/multithreaded-bank-account-bug-hunt
    type: secondary
---

## 题目描述

给一个没有同步措施的账户类编写线程安全包装，使并发存取款不会丢失更新或造成透支。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `UnsafeAccount(balance=0)`：原始类，只有一个 `balance` 字段，没有同步。练习要求不修改它。
- `Account(inner)`：线程安全的包装类，所有对余额的访问都必须经过它。
  - `deposit(amount)`：存入非负整数金额。
  - `withdraw(amount) -> bool`：余额足够就扣减并返回 `True`，不够返回 `False` 且余额不变。
  - `balance() -> int`：返回一个一致的余额快照。
- 所有金额均为非负整数。所有操作必须具有与某个串行执行顺序一致的效果，账户操作总数不超过 $10^5$。

### 输入输出示例

```text
account = Account(UnsafeAccount(0))
使用 8 个线程，总计执行 1000 次 deposit(1)，等待全部完成。
account.balance() -> 1000
account.withdraw(1001) -> False，余额仍为 1000
account.withdraw(1000) -> True，余额变为 0
```

## 解题思路与参考答案

我会锁住余额的整个读改写过程，取款还要把余额检查一起放进去。例如两个线程同时读到旧余额，各加一次再写回，就会丢一次存款；只锁最后赋值不能解决。不能改原类时，用同一把锁保护包装类的所有访问。

## 题目

短筛题：一个 `BankAccount` 类的 `deposit` 在多线程下会丢更新，要求找出竞态并修复。追问是如果不允许改原类，怎样通过继承或包装来修。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

竞态的根源是 `balance += amount` 不是原子操作。修复时锁要覆盖整个读改写过程，`withdraw` 里「检查余额是否足够」也要放在锁内，否则检查和扣减之间仍会插进别的线程。

包装类里的每个余额方法，包括只读的 `balance()`，都用同一把锁。内部对象也不能让调用方绕过包装直接修改，否则这些方法即使各自加锁，整体仍不一致。

面试中常被追问 GIL。GIL 不会让「读、加、写」这样跨多条字节码的序列自动变成原子操作，更不会保护跨多个方法调用的业务流程。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `UnsafeAccount(balance=0)`：原始类，只有一个 `balance` 字段，没有同步。练习要求不修改它。
- `Account(inner)`：线程安全的包装类，所有对余额的访问都必须经过它。
  - `deposit(amount)`：存入非负整数金额。
  - `withdraw(amount) -> bool`：余额足够就扣减并返回 `True`，不够返回 `False` 且余额不变。
  - `balance() -> int`：返回一个一致的余额快照。
- 金额不是非负整数时抛 `ValueError`。所有操作按获得锁的先后线性化，账户操作总数不超过 $10^5$。

### 输入输出示例

```text
account = Account(UnsafeAccount())
8 个线程并发调用 1000 次 account.deposit(1)
account.balance()        -> 1000
account.withdraw(1001)   -> False   # 余额仍为 1000
account.withdraw(1000)   -> True    # 余额变为 0
```

### 解题思路与正确性

`self.balance += amount` 在 Python 里是读取、相加、写回三步，两个线程可能读到同一个旧值，各自加完再写回，其中一次存款就丢了。`withdraw` 的「先检查余额够不够，再扣减」也是同样的问题：两个线程都检查通过，最后会透支。所以检查和读改写必须作为一个临界区整体加锁。

`balance()` 也拿同一把锁，这样读到的值一定是某次完整操作之后的状态。因为每个方法都在锁内完成全部工作，所有操作等价于按拿锁顺序串行执行，测试里并发存款和并发取款的结果都可以精确断言。

这个包装有两个限制要说清：调用方如果还持有 `inner` 的引用并直接改 `balance`，锁就被绕过了；`threading.Lock` 只在一个进程内有效，多个进程或多台机器共享同一个余额（比如在数据库里）时，需要数据库事务、行锁或分布式锁。

### 完整参考实现（Python 3）

```python
from threading import Lock


class UnsafeAccount:
    """原始类：余额读改写没有任何同步，练习中不允许修改它。"""

    def __init__(self, balance=0):
        self.balance = balance


def check_amount(amount):
    if type(amount) is not int or amount < 0:
        raise ValueError(f"amount must be a non-negative int, got {amount!r}")


class Account:
    """包装 UnsafeAccount：所有读写余额的操作都持有同一把锁。"""

    def __init__(self, inner):
        self._inner = inner
        self._lock = Lock()

    def deposit(self, amount):
        check_amount(amount)
        with self._lock:
            # balance += amount 是「读、加、写」三步，必须整体放进临界区
            self._inner.balance += amount

    def withdraw(self, amount):
        """余额不足返回 False 且不改余额；检查和扣减在同一次加锁内完成。"""
        check_amount(amount)
        with self._lock:
            if self._inner.balance < amount:
                return False
            self._inner.balance -= amount
            return True

    def balance(self):
        with self._lock:
            return self._inner.balance
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert account.balance() == 1000` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
from concurrent.futures import ThreadPoolExecutor


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# 8 个线程并发存 1000 次，结果不能丢更新
account = Account(UnsafeAccount())
with ThreadPoolExecutor(8) as pool:
    list(pool.map(account.deposit, [1] * 1000))
assert account.balance() == 1000

# 余额不足时拒绝且余额不变，刚好够时成功
assert not account.withdraw(1001)
assert account.balance() == 1000
assert account.withdraw(1000)
assert account.balance() == 0

# 并发取款不会透支：余额 50 时并发取 100 次 1，恰好 50 次成功
account.deposit(50)
with ThreadPoolExecutor(8) as pool:
    results = list(pool.map(account.withdraw, [1] * 100))
assert sum(results) == 50
assert account.balance() == 0

# 非法金额
expect_value_error(account.deposit, -1)
expect_value_error(account.withdraw, 1.5)
```

### 复杂度与追问

每个操作在锁内只做 $O(1)$ 的工作，但可能要等待其他线程释放锁；额外空间是一把锁，$O(1)$。

- GIL 能不能代替这把锁？不能。GIL 只保证单条字节码不被打断，`+=` 由多条字节码组成，线程可以在中间被切换。跨多个操作的业务逻辑（比如转账要同时改两个账户）更需要应用层自己加锁。
- 换成多进程怎么办？进程之间默认不共享内存，`threading.Lock` 管不到其他进程。可以用 `multiprocessing` 的共享内存加进程锁，或者把余额放进数据库，用事务保证原子性。
- 转账涉及两个账户时，两把锁要按固定顺序（比如账户 id 从小到大）获取，否则两个方向相反的转账可能互相等待，形成死锁。

## 相关题

- [[p3a-xai-process-vs-thread-verbal]]：同一份练习代码，那道题侧重口述进程与线程的区别。
- [[xai-me-live-debug]]：同一道题的个人面经版，记录了 15 分钟屏幕面被拖成 30–45 分钟 CoderPad 调试的节奏。
- [[xai-kv-txn]]：xAI 内存 KV 事务题，里面专门有一节讲 15 分钟 BankAccount race。
