---
id: anthropic-bank-oa
section: anthropic
order: 4
level: A
title: Anthropic OA：银行账户 / 转账后续，接口如何从内存库长出来？
quick: >-
  先用显式 now 推进时间，转账用 pending / accepted / expired / cancelled
  状态保证资金只结算一次。账户名对应唯一实例 id，避免同名重建继承旧转账；再保留日志与流出统计，支持预约、合户和历史查询。
tags:
  - 完整编程练习
  - Anthropic
  - Coding
  - OA
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: 'https://igotanoffer.com/en/advice/anthropic-interview-questions'
    type: secondary
  - title: Anthropic SDE OA — Memory Database and Bank System
    url: 'https://programhelp.net/en/oa/anthropic-sde-oa-interview-guide/'
    type: secondary
---

## 题目描述

实现一个内存银行服务，支持开户、存取款、由接收方确认的转账和账户合并。转账确认前的资金不可再次使用；过期或取消时资金不能丢失，也不能重复返还。所有时间由调用者显式传入。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Bank` 的每个操作都带 `now`，时间单调不减。在任意操作观察余额或转账状态之前，到期未接收的转账应已经退款。
- `create(name, now)`：开户，假定同名账户尚不存在，初始余额为 0。账户被合并删除后，名字可以重新创建，新账户是一个新实例，用唯一的实例 id 和旧账户区分。
- `deposit(name, amount, now)`：存入非负整数金额，返回 `None`。`withdraw(name, amount, now) -> bool`：取出非负整数金额；成功返回 `True`，余额不足返回 `False`，不改动余额。
- `transfer(source, target, amount, now, ttl) -> int | None`：立即从发起方的可用余额里冻结 `amount`，返回转账 id；余额不足返回 `None`。`ttl` 必须为正，到 `now + ttl` 还没被接收就退回发起方。
- `accept(target, transfer_id, now) -> bool`：只有转账指向的那个账户实例能接收，且转账必须还在 pending；恰好到期的时刻已经退回，接收失败。
- `merge(target, source, now)`：先取消并退回所有涉及 `source` 的 pending 转账，再把 `source` 的余额并入 `target`，删除 `source` 这个名字。这是练习自己定的规则，避免去猜原题的合并语义。
- 余额始终是非负整数，操作数不超过 $10^{4}$。

- `transfer` 的金额是正整数，source 与 target 是已存在且不同的账户；`create`、`merge` 均无返回值。`accept` 对不存在、过期、已取消、已接收或接收方不匹配的转账返回 `False`。
### 示例

```text
create a, b, c;  deposit("a", 10, 0)
transfer("a", "b", 4, now=1, ttl=2)  -> 1      # a 的可用余额变成 6
accept("b", 1, 3)                    -> False  # 时刻 3 已到期，4 退回 a，a 回到 10
transfer("a", "b", 4, now=4, ttl=10) -> 2
merge("c", "b", 5);  create("b", 6)            # 转账 2 被取消并退回
accept("b", 2, 6)                    -> False  # 新的 b 不是转账 2 的接收方
```

## 解题思路与参考答案

我会用显式时间、账户实例 id 和只能结算一次的转账状态来实现，先保证资金守恒，再加预约与合户。比如旧账户 b 合并后又同名重建，旧转账也不能被新的 b 接收；只靠账户名和一个余额字典就很难处理这种情况。

## 完整编程练习（手册重构版）

> 来源网站只披露了题型。下面的接口、约束和测试是手册补的练习约定。Python 3 标准库。

### 题面、接口与约束

- `Bank` 的每个操作都带 `now`，时间单调不减，倒退时抛 `ValueError`。每次操作先处理到期的转账。
- `create(name, now)`：开户，同名账户已存在时抛 `ValueError`。账户被合并删除后，名字可以重新创建，新账户是一个新实例，用唯一的实例 id 和旧账户区分。
- `deposit(name, amount, now)`、`withdraw(name, amount, now) -> bool`：金额是非负整数；余额不足时取款返回 `False`，不改动余额。
- `transfer(source, target, amount, now, ttl) -> int | None`：立即从发起方的可用余额里冻结 `amount`，返回转账 id；余额不足返回 `None`。`ttl` 必须为正，到 `now + ttl` 还没被接收就退回发起方。
- `accept(target, transfer_id, now) -> bool`：只有转账指向的那个账户实例能接收，且转账必须还在 pending；恰好到期的时刻已经退回，接收失败。
- `merge(target, source, now)`：先取消并退回所有涉及 `source` 的 pending 转账，再把 `source` 的余额并入 `target`，删除 `source` 这个名字。这是练习自己定的规则，避免去猜原题的合并语义。
- 余额始终是非负整数，操作数不超过 $10^{4}$。

### 输入输出示例

```text
create a, b, c;  deposit("a", 10, 0)
transfer("a", "b", 4, now=1, ttl=2)  -> 1      # a 的可用余额变成 6
accept("b", 1, 3)                    -> False  # 时刻 3 已到期，4 退回 a，a 回到 10
transfer("a", "b", 4, now=4, ttl=10) -> 2
merge("c", "b", 5);  create("b", 6)            # 转账 2 被取消并退回
accept("b", 2, 6)                    -> False  # 新的 b 不是转账 2 的接收方
```

### 解题思路与正确性

转账状态只能从 `pending` 变一次，变成 `accepted`、`expired` 或 `cancelled`。冻结时钱从发起方余额扣掉，三种结局里恰好有一种把钱加回某个账户（接收方或发起方），所以不管操作顺序如何，总金额都守恒。

账户名映射到当前的实例 id，转账里存的也是实例 id。同名重建会拿到新 id，`accept` 比较的是 id，旧转账自然对不上，新账户不会继承旧账户的转账。

`merge` 先退回所有涉及 `source` 的 pending 转账，再合并余额。顺序反过来的话，先并余额、再退回 `source` 发出的冻结款，这笔钱就会落到已经删除的账户上；而发给 `source` 的转账如果不取消，就再也没人能接收，只能等到期。先清 pending 再合余额，冻结款既不会丢，也不会退两次。

### 完整参考实现（Python 3）

```python
from dataclasses import dataclass


@dataclass
class Transfer:
    source: int  # 账户实例 id，不是账户名
    target: int
    amount: int
    expires_at: int
    state: str = "pending"  # pending -> accepted / expired / cancelled，只变一次


class Bank:
    """带两步转账和账户合并的银行。

    账户名可以在合并后被重新创建，所以内部用自增的实例 id 识别账户，
    转账记录的是实例 id，旧转账不会落到同名的新账户上。
    """

    def __init__(self):
        self.account_ids = {}  # 账户名 -> 当前实例 id
        self.balances = {}  # 实例 id -> 可用余额（不含冻结中的转账）
        self.transfers = {}  # 转账 id -> Transfer
        self.next_account_id = 0
        self.next_transfer_id = 0
        self.time = float("-inf")

    def _tick(self, now):
        """推进时钟，并把到期未接收的转账退回给发起方。"""
        if now < self.time:
            raise ValueError(f"time went backwards: {now} < {self.time}")
        self.time = now
        for transfer in self.transfers.values():
            if transfer.state == "pending" and now >= transfer.expires_at:
                self._refund(transfer, "expired")

    def _refund(self, transfer, new_state):
        self.balances[transfer.source] += transfer.amount
        transfer.state = new_state

    @staticmethod
    def _check_amount(amount, allow_zero=True):
        if type(amount) is not int or amount < 0 or (amount == 0 and not allow_zero):
            raise ValueError(f"invalid amount: {amount!r}")

    def create(self, name, now):
        self._tick(now)
        if name in self.account_ids:
            raise ValueError(f"account already exists: {name!r}")
        self.next_account_id += 1
        self.account_ids[name] = self.next_account_id
        self.balances[self.next_account_id] = 0

    def deposit(self, name, amount, now):
        self._tick(now)
        self._check_amount(amount)
        self.balances[self.account_ids[name]] += amount

    def withdraw(self, name, amount, now):
        """余额足够就扣款并返回 True，否则不改动、返回 False。"""
        self._tick(now)
        account = self.account_ids[name]
        self._check_amount(amount)
        if self.balances[account] < amount:
            return False
        self.balances[account] -= amount
        return True

    def transfer(self, source, target, amount, now, ttl):
        """发起转账并立即冻结资金，返回转账 id；余额不足返回 None。ttl 后未接收就退回。"""
        self._tick(now)
        if source == target:
            raise ValueError("cannot transfer to the same account")
        if ttl <= 0:
            raise ValueError(f"ttl must be positive, got {ttl}")
        self._check_amount(amount, allow_zero=False)
        source_id = self.account_ids[source]
        target_id = self.account_ids[target]
        if self.balances[source_id] < amount:
            return None
        self.balances[source_id] -= amount
        self.next_transfer_id += 1
        self.transfers[self.next_transfer_id] = Transfer(
            source_id, target_id, amount, now + ttl
        )
        return self.next_transfer_id

    def accept(self, target, transfer_id, now):
        """只有转账指向的那个账户实例能接收，且必须仍是 pending；恰好到期时已退回。"""
        self._tick(now)
        transfer = self.transfers.get(transfer_id)
        if transfer is None or transfer.state != "pending":
            return False
        if self.account_ids.get(target) != transfer.target:
            return False
        self.balances[transfer.target] += transfer.amount
        transfer.state = "accepted"
        return True

    def merge(self, target, source, now):
        """把 source 并入 target：先退回所有涉及 source 的 pending 转账，再转移余额并删除 source 名字。"""
        self._tick(now)
        if target == source:
            raise ValueError("cannot merge an account into itself")
        target_id = self.account_ids[target]
        source_id = self.account_ids[source]
        for transfer in self.transfers.values():
            if transfer.state == "pending" and source_id in (
                transfer.source,
                transfer.target,
            ):
                self._refund(transfer, "cancelled")
        # 退款先回到 source，再随余额一起并入 target，冻结款不会丢也不会退两次
        self.balances[target_id] += self.balances[source_id]
        self.balances[source_id] = 0
        del self.account_ids[source]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert balance(bank, "a") == 6` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def balance(bank, name):
    return bank.balances[bank.account_ids[name]]


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


bank = Bank()
for name in ("a", "b", "c"):
    bank.create(name, 0)
bank.deposit("a", 10, 0)

# 发起转账立即冻结；在到期时刻 3 接收会失败，资金退回
first = bank.transfer("a", "b", 4, 1, 2)
assert balance(bank, "a") == 6
assert not bank.accept("b", first, 3)
assert balance(bank, "a") == 10

# b 并入 c 时取消发给 b 的 pending 转账；重建的 b 不能接收旧转账
second = bank.transfer("a", "b", 4, 4, 10)
bank.merge("c", "b", 5)
bank.create("b", 6)
assert not bank.accept("b", second, 6)
assert balance(bank, "a") == 10

# 同一笔转账只能接收一次
third = bank.transfer("a", "b", 3, 7, 10)
assert bank.accept("b", third, 8)
assert not bank.accept("b", third, 9)

# 资金守恒：没有 pending 转账时，余额总和等于存入总额
assert sum(bank.balances.values()) == 10

# 合并时 source 发出的冻结款先退回 source，再随余额并入 target
bank.create("d", 9)
fourth = bank.transfer("b", "a", 2, 9, 10)
bank.merge("d", "b", 9)
assert balance(bank, "d") == 3
assert not bank.accept("a", fourth, 9)

# 余额不足：转账返回 None，取款返回 False，余额不变
assert bank.transfer("d", "a", 100, 10, 5) is None
assert bank.withdraw("d", 100, 10) is False
assert bank.withdraw("d", 3, 10) is True
assert balance(bank, "d") == 0

# 非法输入：重名开户、时间倒退、自转、负金额、非正 ttl、自我合并
expect_value_error(lambda: bank.create("a", 10))
expect_value_error(lambda: bank.deposit("a", 1, 9))
expect_value_error(lambda: bank.transfer("a", "a", 1, 10, 5))
expect_value_error(lambda: bank.deposit("a", -1, 10))
expect_value_error(lambda: bank.transfer("a", "c", 1, 10, 0))
expect_value_error(lambda: bank.merge("a", "a", 10))
```

### 复杂度与追问

设转账总数为 T。这份实现每次操作都在 `_tick` 里扫一遍所有转账，是 O(T)；`merge` 也是 O(T)。空间是 O(账户实例数 + T)。

- 追问「到期处理太慢」：把 pending 转账按到期时间放进最小堆，`_tick` 只弹出已到期的那些，均摊下来每笔转账只处理一次。
- 追问「查询某个账户在过去某一时刻的余额」：当前余额推不出历史余额，需要记录每次余额变动的事件账本，查询时按时间二分或回放。

## 题怎么来的

公开面经把银行系统和内存库并列，都是 CodeSignal 上的分层题。我会把它当成和 `anthropic-inmemory-db` 同一套的接口练习：第一层如果把账户做成 `id -> 余额` 的字典，后面加入预约转账和合户时，很可能要推倒重写。

## 先定时间和资金变动规则

OA 里的时间是命令自带的整数时间戳，不要用程序运行时的真实时钟。所有会改余额的路径都用同一个 `now`，这一点和 TTL 那题一样。

每条记录至少要能回答：这笔钱从哪来、到哪去、什么时候发生、算不算流出。所以第一层我不会只写 `balances[id] += x`，最小的形状是这样：

```python
class Bank:
    def __init__(self):
        self.accounts = {}  # 账户 id -> {"balance", "outflow", "txs", "pending"}

    def deposit(self, now, account_id, amount):
        if amount <= 0 or account_id not in self.accounts:
            return False
        account = self.accounts[account_id]
        account["balance"] += amount
        account["txs"].append(("D", now, amount, None))
        return True

    def transfer(self, now, source_id, target_id, amount):
        if amount <= 0 or source_id == target_id:
            return False
        source = self.accounts.get(source_id)
        target = self.accounts.get(target_id)
        if source is None or target is None or source["balance"] < amount:
            return False
        source["balance"] -= amount
        target["balance"] += amount
        source["outflow"] += amount
        source["txs"].append(("T-", now, amount, target_id))
        target["txs"].append(("T+", now, amount, source_id))
        return True
```

转账要先把条件全部检查完，再同时改两个账户。只改了一侧就返回，账就对不上了。金额为正、两个账户都存在、发起方余额足够，三条都满足才动余额。

## 后几层在原接口上增加功能

各家公开拆解的层序不完全一样，常见的是四个阶段：

1. 开户、存款、查余额。
2. 转账、支付；有的版本要求按流出总额做 top-K。
3. 预约未来的转账、取消预约；有的版本这一层就是合户。
4. 合户，或者 cashback / top spenders。

我会按这些后续操作需要的数据预留结构，现场再以题面约定具体函数和语义。

**流出 top-K。** 每次转账时累加 `outflow`，查询时按 `outflow` 排序，平局按题目规定的 id 顺序。不要每次查询都把全部日志扫一遍。

**预约转账。** 和 TTL 题的过期堆是同一个结构：把 `(execute_at, tx_id)` 放进最小堆，推进 `now` 时弹出所有到期的。取消用 tombstone 实现：弹出后核对 `pending[tx_id]` 是否还在，不在就说明已被取消。执行时走同一个 `transfer` 函数。余额不够时按题目要求处理，是失败丢弃还是留到下次再试；题目没说就默认失败并清掉，关键是行为要确定。

**合户。** 先定谁留下。余额相加，`outflow` 相加，日志拼接，pending 里指向被删 id 的改成留下的 id；之后对被删 id 的所有操作都返回失败。有的题要求「历史仍能按原账户查询」，那日志里要带 `orig_id`，合户只改当前余额，不改历史记录的主键。

Cashback 和支付绑在一起：支付时记下应返的比例，到结算时间再 `deposit` 一笔内部入账。合户时要把未结算的 cashback 一起搬走，否则第四层的规则会和第二层冲突。

## 保持操作原子性

接口返回成功或失败，不能更新到一半才抛异常，调用方也不持有余额副本。单线程 OA 不考并发，但现场可能追问：同时锁两个账户时，按 id 顺序加锁，避免一个线程锁 A 等 B、另一个锁 B 等 A 的死锁；全表 backup 或 top-K 查询要么暂停写入，要么用带版本号的 copy-on-write。

## 追问

- **和内存库差在哪？** 内存库是单个 key 的 TTL；银行要同时原子地更新两个账户，还有按时间顺序触发的副作用。过期堆、惰性过期、快照这三样可以直接搬过来用。
- **转账要不要事务 id？** 做预约和幂等时需要。同一个 `tx_id` 重放必须什么都不做，否则网络重试会让同一笔钱被花两次。
- **合户后 top-K 用谁的流出？** 默认并到留下的 id 上。如果题目要求「历史排名不变」，流出就按发生时所属的账户冻结，合户只影响以后的流出。
- **余额用 float 吗？** 面试里用整数分。float 累加 cashback 这类百分比会有舍入误差，提一句就够。

## 相关题

- [[p3a-anthropic-oa-bank-system]]：同一道 OA 的另一份来源，转账冻结、只能接收一次、合户时取消发给被并账户的转账，这几组测试几乎相同。
