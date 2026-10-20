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


def test():
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


if __name__ == "__main__":
    test()
