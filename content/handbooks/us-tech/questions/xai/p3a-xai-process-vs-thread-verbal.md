---
id: p3a-xai-process-vs-thread-verbal
section: xai
order: 623
level: A
title: "xAI：进程与线程：内存、调度与共享风险"
quick: "同一进程内的线程共享地址空间、各有自己的栈，进程之间默认隔离内存、要通过 IPC 协作；共享让传数据方便，但会带来竞态和死锁。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · process-vs-thread-verbal"
    url: https://www.1point3acres.com/interview/problems/company/xai/process-vs-thread-verbal
    type: secondary
---

## 题目

短筛中的口述题，考操作系统基础：进程和线程有什么区别，各自的内存模型、调度方式和共享数据的风险是什么。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。原题是口述题，下面的代码练习只是手册补的共享内存竞态演示，不代表原帖要求写代码。

## 思路

可以从内存讲起：

- 同一进程里的线程共享地址空间，也就是共享堆、全局变量和打开的文件，但每个线程有自己的栈和寄存器状态。
- 不同进程默认各有独立的地址空间，一个进程崩溃一般不会破坏另一个进程的内存；要交换数据得用管道、socket、共享内存等 IPC 机制。

调度上，操作系统调度的基本单位是线程。线程切换不用换页表，比进程切换便宜；创建线程也比创建进程开销小。

然后讲取舍：共享内存让线程之间传数据几乎没有成本，代价是要自己处理竞态和死锁；进程隔离更安全，代价是数据要复制或通过 IPC 传递。

如果面试官问到 Python，要把操作系统层面的原理和 GIL 分开说。CPython 的 GIL 让同一时刻只有一个线程执行 Python 字节码，所以 CPU 密集任务用多线程加速不了，通常改用多进程；I/O 密集任务在等待时会释放 GIL，多线程仍然有用。GIL 也不能替代锁，下面的练习就是一个例子。

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

`self.balance += amount` 在 Python 里是读取、相加、写回三步，两个线程可能读到同一个旧值，各自加完再写回，其中一次存款就丢了。`withdraw` 的「先检查余额够不够，再扣减」也是同样的问题：两个线程都检查通过，最后会透支。所以锁要把整段读改写（包括检查）包进去，而不是只锁赋值那一行。

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

- [[p3a-xai-multithreaded-bank-account-bug-hunt]]：同一份练习代码，那道题要求实际修复竞态。
