---
id: p3a-anthropic-oa-bank-system
section: anthropic
order: 610
level: A
title: "Anthropic：银行 OA：转账冻结、接收与账号合并"
quick: "我会在发起转账时冻结资金，并让每笔转账只能结算一次。账户内部用独立实例 id 识别，避免同名重建接走旧转账；合并时先取消并退回涉及被合并账户的待接收转账，再合并余额。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · oa-bank-system"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/oa-bank-system
    type: secondary
---

## 题目描述

实现带账户合并、待接受转账和超时退款的银行系统。每次操作都必须遵守下述账户身份和资金规则。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `Bank` 的每个操作都带 `now`，时间单调不减。每次操作先处理到期的转账。
- `create(name, now)`：开户，同名账户已存在时抛 `ValueError`。账户被合并删除后，名字可以重新创建，新账户是一个新实例。
- `deposit(name, amount, now)`、`withdraw(name, amount, now) -> bool`：金额是非负整数；余额不足时取款返回 `False`，不改动余额。
- `transfer(source, target, amount, now, ttl) -> int | None`：立即从发起方冻结 `amount`，返回转账 id；余额不足返回 `None`。`ttl` 必须为正，到 `now + ttl` 时还没被接收就退回。
- `accept(target, transfer_id, now) -> bool`：只有转账指向的那个账户实例能接收，且转账必须还在 pending；恰好到期的时刻已经退回，接收失败。
- `merge(target, source, now)`：先取消并退回所有涉及 `source` 的 pending 转账，再把 `source` 的余额并入 `target`，删除 `source` 这个名字。这是练习自己定的规则，不是在猜原题的合并语义。
- 余额始终是非负整数，操作数不超过 $10^4$。

### 输入输出示例

```text
create a, b, c;  deposit("a", 10, 0)
transfer("a", "b", 4, now=1, ttl=2)  -> 1      # a 的可用余额变成 6
accept("b", 1, 3)                    -> False  # 时刻 3 已到期，4 退回 a
transfer("a", "b", 4, now=4, ttl=10) -> 2
merge("c", "b", 5);  create("b", 6)            # 转账 2 被取消并退回
accept("b", 2, 6)                    -> False  # 新的 b 不是转账 2 的接收方
```

## 解题思路与参考答案

## 题目

实现一个银行系统：开户、存款、取款，然后加入两步转账（发起方先发起，接收方在期限内接收），最后加入账户合并，并处理合并后同名账户被重新创建的情况。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会把转账写成一次性的状态转换：发起时先从余额中冻结资金，之后只能被接收、到期退回，或者因合并取消。每笔转账只能离开 pending 状态一次，才能避免重复结算或资金丢失。

账户要有独立于名字的身份。账户名在合并后可以被重新创建，如果转账只记账户名，一笔发给旧账户的转账就可能被同名的新账户收走。所以内部给每个账户实例分配一个自增 id，转账记录的是 id。

合并的规则题卡没有说清，要先和面试官确认：被合并账户的历史怎么处理，它发出的、冻结中的转账怎么办，发给它、还没被接收的转账又怎么办。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Bank` 的每个操作都带 `now`，时间单调不减，倒退时抛 `ValueError`。每次操作先处理到期的转账。
- `create(name, now)`：开户，同名账户已存在时抛 `ValueError`。账户被合并删除后，名字可以重新创建，新账户是一个新实例。
- `deposit(name, amount, now)`、`withdraw(name, amount, now) -> bool`：金额是非负整数；余额不足时取款返回 `False`，不改动余额。
- `transfer(source, target, amount, now, ttl) -> int | None`：立即从发起方冻结 `amount`，返回转账 id；余额不足返回 `None`。`ttl` 必须为正，到 `now + ttl` 时还没被接收就退回。
- `accept(target, transfer_id, now) -> bool`：只有转账指向的那个账户实例能接收，且转账必须还在 pending；恰好到期的时刻已经退回，接收失败。
- `merge(target, source, now)`：先取消并退回所有涉及 `source` 的 pending 转账，再把 `source` 的余额并入 `target`，删除 `source` 这个名字。这是练习自己定的规则，不是在猜原题的合并语义。
- 余额始终是非负整数，操作数不超过 $10^4$。

### 输入输出示例

```text
create a, b, c;  deposit("a", 10, 0)
transfer("a", "b", 4, now=1, ttl=2)  -> 1      # a 的可用余额变成 6
accept("b", 1, 3)                    -> False  # 时刻 3 已到期，4 退回 a
transfer("a", "b", 4, now=4, ttl=10) -> 2
merge("c", "b", 5);  create("b", 6)            # 转账 2 被取消并退回
accept("b", 2, 6)                    -> False  # 新的 b 不是转账 2 的接收方
```

### 解题思路与正确性

转账状态只能从 `pending` 变一次，变成 `accepted`、`expired` 或 `cancelled`。冻结时钱从发起方余额扣掉，三种结局里恰好有一种把钱加回某个账户（接收方或发起方），所以任何操作序列下总金额都守恒。

账户名映射到当前的实例 id，转账里存的也是实例 id。同名重建会拿到新 id，`accept` 比较的是 id，旧转账自然对不上。

`merge` 先退回所有涉及 `source` 的 pending 转账，再合并余额。如果反过来，先把余额并进 `target`、再退回 `source` 发出的冻结款，这笔钱就会落到一个已经被删除的账户上；不取消发给 `source` 的转账，它就再也没人能接收，只能等到期。

### 完整参考实现（Python 3）

```python
from dataclasses import dataclass


@dataclass
class Transfer:
    source: int       # 账户实例 id，不是账户名
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
        self.balances = {}     # 实例 id -> 可用余额（不含冻结中的转账）
        self.transfers = {}    # 转账 id -> Transfer
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
        self.transfers[self.next_transfer_id] = Transfer(source_id, target_id, amount, now + ttl)
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
            if transfer.state == "pending" and source_id in (transfer.source, transfer.target):
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

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def balance(bank, name):
    return bank.balances[bank.account_ids[name]]

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

# 余额不足：转账返回 None，取款返回 False
assert bank.transfer("b", "a", 100, 10, 5) is None
assert bank.withdraw("b", 100, 10) is False
assert bank.withdraw("b", 3, 10) is True
assert balance(bank, "b") == 0
```

### 复杂度与追问

设转账总数为 T。这份实现每次操作都在 `_tick` 里扫一遍所有转账，是 O(T)；`merge` 也是 O(T)。空间是 O(账户实例数 + T)。

- 追问「到期处理太慢」：把 pending 转账按到期时间放进最小堆，`_tick` 只弹出已到期的那些，均摊下来每笔转账只处理一次。
- 追问「查询某个账户在过去某一时刻的余额」：当前余额推不出历史余额，需要记录每次余额变动的事件账本，查询时按时间二分或回放。

## 相关题

- [[anthropic-bank-oa]]：手册里已有的同类题；本条来源只用来补充对照，两份题面契约不一致时各按各的，不混用。
