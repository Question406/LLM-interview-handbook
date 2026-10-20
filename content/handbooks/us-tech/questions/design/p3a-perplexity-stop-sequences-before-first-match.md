---
id: p3a-perplexity-stop-sequences-before-first-match
section: design
order: 602
level: A
title: "Perplexity：第一处 stop 前截断与流式扩展"
quick: "离线版在所有 stop 的出现位置里取起点最早的一处截断；流式版扣住可能长成 stop 的后缀，只发出安全的字符，并要说明它按最先完成还是最早起点停止。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · stop-sequences-before-first-match"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/stop-sequences-before-first-match
    type: secondary
---

## 题目

给一段文本和若干 stop 序列，返回第一处 stop 之前的内容。先写离线版，再扩展成流式版：文本按 chunk 到达，边收边输出，遇到 stop 就截断。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

离线版很直接：对每个 stop 找它在文本里第一次出现的起点，取所有起点里最小的那个截断。

流式版的难点在于已经发出的字符收不回来，所以不能先输出整个 chunk 再检查。做法是维护输出末尾里「还可能长成某个 stop」的后缀，把它扣住，只发它前面的部分。chunk 到达时更新这段后缀；某个 stop 完整出现就截断停止；流结束时扣住的部分没凑成 stop，就当普通文本发出。

要覆盖的边界有：空 stop（这份练习直接拒绝，否则每个位置都算命中）、互相重叠的 stop、跨 chunk 的 stop、流结束时未完成的前缀。

还要注意两种语义会给出不同结果。stops 为 `["abcd", "bc"]`、文本为 `"xabcd"` 时，离线版按起点最早截在 `"x"`；流式版如果要求立刻停止，读到 `c` 时 `bc` 已经完成，会截在 `"xa"`。面试时要说明你实现的是哪一种。

相关题：[[p3a-microsoft-streaming-stop-token-detection]]（同一份实现，那题更强调流式检测不泄露前缀）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Stopper(stops)`：`stops` 是非空字符串组成的非空列表，否则抛 `ValueError`。stop 之间可以互相重叠，也可以跨 chunk 出现。
- `feed(chunk) -> str`：返回这次可以安全发给客户端的文本。一旦某个 stop 完整出现，就丢掉它和它之后的所有内容，之后的 `feed` 都返回空串。
- `finish() -> str`：流结束时调用，把缓冲里没凑成 stop 的尾巴原样发出。
- 流式版的匹配规则：按字符处理，最先完成的 stop 触发；同一结束位置有多个 stop 时按最长的截断。
- `truncate_at_first_stop(text, stops) -> str`：离线版，返回所有 stop 中起点最早那一处之前的文本，没有命中就返回原文。
- 总字符数不超过 $10^5$，最长 stop 不超过 100。

### 输入输出示例

```text
s = Stopper(["STOP"])
s.feed("hello ST")   -> "hello "      # "ST" 可能是 STOP 的开头，先扣住
s.feed("OPtail")     -> ""            # 凑成 STOP，丢弃并停止
s.finish()           -> ""

s = Stopper(["abcd", "bc"]); s.feed("xabcd") + s.finish()   -> "xa"
truncate_at_first_stop("xabcd", ["abcd", "bc"])             -> "x"
```

最后两行展示两种契约的差别：流式版读到 `c` 时 `bc` 已经完成，立即停止；离线版能看到全文，选起点最早的 `abcd`。

### 解题思路与正确性

`pending` 始终是当前输出里「可能是某个 stop 前缀」的最长后缀。比它更靠前的字符不管后面来什么，都不可能成为任何 stop 的一部分，所以可以安全发出。每来一个字符先检查有没有 stop 以 `pending` 结尾：有就发出 stop 之前的部分并停止；没有就重新计算要扣住的最长后缀，把其余部分发出。

命中时 stop 一定完整地落在 `pending` 里，因为 stop 的每个前缀在出现时都被扣住了。流结束时 `pending` 里的东西没能凑成 stop，就是普通文本，由 `finish` 发出。

流式版选「最先完成」而不是「起点最早」，是因为要按起点最早来决定，就得等所有更长的 stop 都确定不会完成才能停，输出延迟会变大。这份练习先固定了可以立即停止的契约；离线场景用 `truncate_at_first_stop`。

### 完整参考实现（Python 3）

```python
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
```

### 可执行测试

```python
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
```

### 复杂度与追问

设总字符数为 T、stop 个数为 S、最长 stop 长度为 L。每个字符要做 S 次 `endswith`（O(S·L)）和最多 L 次后缀查集合（每次切片和哈希 O(L)），总时间最坏 O(T·L² + T·S·L)。缓冲最多 L 个字符；前缀集合存 O(S·L) 个字符串，共 O(S·L²) 个字符。

- 想把扫描降到线性：用 Aho–Corasick 自动机。当前状态的深度就是要扣住的长度，命中时由输出链给出完成的 stop，总时间 O(T + 匹配数)。
- 想要「起点最早」的流式语义：命中较短的 stop 后不能马上停，要继续扣住，直到所有起点更早的候选都确定不会完成，再决定截断位置。这时要说清楚最坏输出延迟是 L 个字符。
