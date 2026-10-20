def truncate_at_first_stop(text, stops):
    """离线版：返回所有 stop 中起点最早的那一处之前的文本；没有命中就返回原文。"""
    if not stops or any(not stop for stop in stops):
        raise ValueError("stops must be non-empty strings")
    starts = [text.find(stop) for stop in stops]
    hits = [start for start in starts if start != -1]
    return text[:min(hits)] if hits else text


class Stopper:
    """流式版：按字符处理，最先「完成」的 stop 触发停止；同一结束位置有多个 stop 时按最长的截断。

    pending 只保存「可能是某个 stop 前缀」的最长后缀，它前面的字符已经不可能属于任何 stop，可以安全发出。
    """

    def __init__(self, stops):
        if not stops or any(not stop for stop in stops):
            raise ValueError("stops must be non-empty strings")
        self.stops = tuple(stops)
        self.prefixes = {stop[:i] for stop in stops for i in range(1, len(stop) + 1)}
        self.pending = ""
        self.done = False

    def _held_suffix_length(self):
        """pending 中仍可能长成 stop 的最长后缀长度。"""
        for length in range(len(self.pending), 0, -1):
            if self.pending[-length:] in self.prefixes:
                return length
        return 0

    def feed(self, chunk):
        """返回这次可以安全发给客户端的文本。"""
        output = []
        for char in chunk:
            if self.done:
                break
            self.pending += char
            matches = [stop for stop in self.stops if self.pending.endswith(stop)]
            if matches:
                longest = max(matches, key=len)
                output.append(self.pending[:-len(longest)])
                self.pending = ""
                self.done = True
                break
            hold = self._held_suffix_length()
            output.append(self.pending[:len(self.pending) - hold])
            self.pending = self.pending[len(self.pending) - hold:]
        return "".join(output)

    def finish(self):
        """流结束：没凑成 stop 的缓冲是正常文本，原样发出。"""
        if self.done:
            return ""
        self.done = True
        tail = self.pending
        self.pending = ""
        return tail


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # stop 跨 chunk：前缀先扣住，凑齐后丢弃并停止
    stopper = Stopper(["STOP"])
    assert stopper.feed("hello ST") == "hello "
    assert stopper.feed("OPtail") == ""
    assert stopper.finish() == ""

    # 任意切分位置结果都一样
    text = "abcSTOPtail"
    for cut in range(len(text) + 1):
        stopper = Stopper(["STOP"])
        emitted = stopper.feed(text[:cut]) + stopper.feed(text[cut:]) + stopper.finish()
        assert emitted == "abc"

    # 流结束时未完成的前缀是正常文本
    stopper = Stopper(["abcd"])
    assert stopper.feed("ab") == ""
    assert stopper.finish() == "ab"

    # 同一结束位置，按最长的 stop 截断
    stopper = Stopper(["abc", "bc"])
    assert stopper.feed("abc") == ""

    # 两种契约的差别：流式版先完成的 bc 触发，离线版按起点最早的 abcd 截断
    stopper = Stopper(["abcd", "bc"])
    assert stopper.feed("xabcd") + stopper.finish() == "xa"
    assert truncate_at_first_stop("xabcd", ["abcd", "bc"]) == "x"
    assert truncate_at_first_stop("no stop here", ["STOP"]) == "no stop here"

    # 空 stop 列表或空 stop 非法
    expect_value_error(Stopper, [])
    expect_value_error(Stopper, ["ok", ""])
    expect_value_error(truncate_at_first_stop, "text", [""])


if __name__ == "__main__":
    test()
