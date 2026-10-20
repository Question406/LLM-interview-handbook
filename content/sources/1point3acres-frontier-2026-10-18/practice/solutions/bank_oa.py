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


def test():
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


if __name__ == "__main__":
    test()
