import ipaddress


def ip_to_int(text):
    """'10.0.0.1' -> 167772161；格式非法（段越界、前导 0 等）时抛 ValueError。"""
    return int(ipaddress.IPv4Address(text))


def int_to_ip(value):
    return str(ipaddress.IPv4Address(value))


class CIDR:
    """CIDR 范围上的双向迭代器。

    状态 pos 是「下一个要由 next 返回的地址偏移」，取值 0..size：
    next 返回 pos 再加一，prev 先减一再返回，两者用同一个位置定义。
    """

    def __init__(self, text):
        network = ipaddress.IPv4Network(text, strict=False)  # 主机位清零，规范化成网络地址
        self.start = int(network.network_address)
        self.size = network.num_addresses  # 2 ** (32 - prefix)，/0 也只存一个整数
        self.pos = 0

    def next(self):
        if self.pos >= self.size:
            raise StopIteration
        address = int_to_ip(self.start + self.pos)
        self.pos += 1
        return address

    def prev(self):
        if self.pos == 0:
            raise StopIteration
        self.pos -= 1
        return int_to_ip(self.start + self.pos)

    def contains(self, address):
        return self.start <= ip_to_int(address) < self.start + self.size

    def get_state(self):
        return self.pos

    def set_state(self, pos):
        if type(pos) is not int or not 0 <= pos <= self.size:
            raise ValueError(f"invalid state: {pos!r}")
        self.pos = pos


def test():
    def expect_error(error, fn, *args):
        try:
            fn(*args)
        except error:
            return
        raise AssertionError(f"{fn.__name__} should raise {error.__name__}")

    # 地址与整数互转
    assert ip_to_int("10.0.0.1") == 10 * 2 ** 24 + 1
    assert int_to_ip(2 ** 32 - 1) == "255.255.255.255"
    expect_error(ValueError, ip_to_int, "256.0.0.1")
    expect_error(ValueError, ip_to_int, "01.2.3.4")

    # 10.0.0.1/30 规范化为 10.0.0.0 - 10.0.0.3，含网络地址和广播地址
    cidr = CIDR("10.0.0.1/30")
    assert cidr.next() == "10.0.0.0"
    assert cidr.next() == "10.0.0.1"
    assert cidr.prev() == "10.0.0.1"
    assert cidr.contains("10.0.0.3")
    assert not cidr.contains("10.0.0.4")

    # 保存状态后前进，再恢复，能重放同一项
    state = cidr.get_state()
    assert cidr.next() == "10.0.0.1"
    cidr.set_state(state)
    assert cidr.next() == "10.0.0.1"

    # /0 不枚举，直接跳到最后一个地址
    everything = CIDR("0.0.0.0/0")
    everything.set_state(everything.size - 1)
    assert everything.next() == "255.255.255.255"

    # /32 只有一个地址，取完后 next 耗尽；回到起点后 prev 耗尽
    single = CIDR("1.2.3.4/32")
    assert single.next() == "1.2.3.4"
    expect_error(StopIteration, single.next)
    assert single.prev() == "1.2.3.4"
    expect_error(StopIteration, single.prev)

    # 非法状态
    expect_error(ValueError, single.set_state, 2)


if __name__ == "__main__":
    test()
