import ipaddress


def normalize(name):
    """域名不区分大小写，末尾的 "." 可有可无。"""
    return name.casefold().rstrip(".")


def parse_ipv4(text):
    return str(ipaddress.IPv4Address(text))  # 非法地址会抛 ValueError


class Resolver:
    """简化的 DNS 解析器：支持 A 和 CNAME 记录、TTL 缓存和 fallback 查询。

    records[name] = (kind, value, ttl)，kind 是 "A" 或 "CNAME"。
    fallback(name) 在本地没有记录时调用，返回 (ip, ttl)，返回 None 表示域名不存在。
    """

    def __init__(self, records, fallback=None):
        self.records = {normalize(name): record for name, record in records.items()}
        self.fallback = fallback
        self.cache = {}  # 原始查询名 -> (ip, 过期时刻)
        self.last_now = float("-inf")

    def resolve(self, name, now):
        """返回 name 的 IPv4 地址。不存在时抛 KeyError，CNAME 成环或数据非法时抛 ValueError。"""
        if now < self.last_now:
            raise ValueError(f"time went backwards: {now} < {self.last_now}")
        self.last_now = now
        query = normalize(name)

        cached = self.cache.get(query)
        if cached is not None:
            ip, expires_at = cached
            if now < expires_at:
                return ip

        ip, ttl = self._follow_chain(query)
        # 只缓存成功结果；失败不写缓存，暂时的网络错误不会变成长期的「不存在」
        self.cache[query] = (ip, now + ttl)
        return ip

    def _follow_chain(self, query):
        """沿 CNAME 链走到 A 记录，返回 (ip, 整条链上最小的 TTL)。"""
        seen = set()
        current = query
        ttl = float("inf")
        while True:
            if current in seen:
                raise ValueError(f"CNAME cycle at {current!r}")
            seen.add(current)

            record = self.records.get(current)
            if record is None:
                return self._ask_fallback(current, ttl)

            kind, value, record_ttl = record
            if record_ttl < 0:
                raise ValueError(f"negative TTL for {current!r}")
            ttl = min(ttl, record_ttl)
            if kind == "A":
                return parse_ipv4(value), ttl
            if kind != "CNAME":
                raise ValueError(f"unsupported record type: {kind!r}")
            current = normalize(value)

    def _ask_fallback(self, name, ttl_so_far):
        answer = self.fallback(name) if self.fallback else None
        if answer is None:
            raise KeyError(name)
        ip, fallback_ttl = answer
        if fallback_ttl < 0:
            raise ValueError(f"negative TTL from fallback for {name!r}")
        return parse_ipv4(ip), min(ttl_so_far, fallback_ttl)


def test():
    def expect_error(error, fn, *args):
        try:
            fn(*args)
        except error:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise {error.__name__}")

    # 缓存 TTL 取整条链的最小值：CNAME 的 5，而不是 A 记录的 10
    resolver = Resolver({"a": ("CNAME", "b", 5), "b": ("A", "1.2.3.4", 10)})
    assert resolver.resolve("A.", 0) == "1.2.3.4"
    assert resolver.cache["a"][1] == 5

    # 缓存期内看不到记录变化，到期后重新查链
    resolver.records["b"] = ("A", "5.6.7.8", 10)
    assert resolver.resolve("a", 4) == "1.2.3.4"
    assert resolver.resolve("a", 5) == "5.6.7.8"

    # CNAME 指向自己
    expect_error(ValueError, Resolver({"a": ("CNAME", "a", 1)}).resolve, "a", 0)

    # 本地没有记录时走 fallback；fallback 返回 None 表示不存在，且失败不缓存
    answers = {"ext": ("9.9.9.9", 3)}
    with_fallback = Resolver({"x": ("CNAME", "ext", 7)}, fallback=answers.get)
    assert with_fallback.resolve("x", 0) == "9.9.9.9"
    assert with_fallback.cache["x"][1] == 3
    expect_error(KeyError, with_fallback.resolve, "missing", 1)
    assert "missing" not in with_fallback.cache

    expect_error(ValueError, resolver.resolve, "a", 4)  # 时钟倒退


if __name__ == "__main__":
    test()
