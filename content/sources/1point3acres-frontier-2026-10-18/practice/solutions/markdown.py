import html

PLAIN, INLINE, BLOCK = "plain", "inline", "block"


class Markdown:
    """流式解析 `inline code` 和 ```fenced code```，feed 返回这一段已经能确定的 HTML。"""

    def __init__(self):
        self.mode = PLAIN
        self.pending_ticks = 0  # 还没结束的连续反引号个数，可能跨 chunk
        self.finished = False

    def _flush_ticks(self):
        """反引号 run 已经结束：按当前模式决定它是开/闭标记，还是字面量。"""
        run = self.pending_ticks
        self.pending_ticks = 0
        if run == 0:
            return ""
        if self.mode == PLAIN and run == 1:
            self.mode = INLINE
            return "<code>"
        if self.mode == PLAIN and run == 3:
            self.mode = BLOCK
            return "<pre><code>"
        if self.mode == INLINE and run == 1:
            self.mode = PLAIN
            return "</code>"
        if self.mode == BLOCK and run == 3:
            self.mode = PLAIN
            return "</code></pre>"
        return "`" * run  # 其他长度（以及代码块里的单个反引号）原样输出

    def feed(self, chunk):
        if self.finished:
            raise ValueError("feed() called after finish()")
        out = []
        for char in chunk:
            if char == "`":
                # 先攒着：只有看到下一个非反引号字符，才知道这个 run 有多长
                self.pending_ticks += 1
                continue
            out.append(self._flush_ticks())
            out.append(html.escape(char, quote=False))
        return "".join(out)

    def finish(self):
        """结束输入：确定最后一个反引号 run，并自动闭合未闭合的代码。可重复调用。"""
        if self.finished:
            return ""
        out = self._flush_ticks()
        if self.mode == INLINE:
            out += "</code>"
        elif self.mode == BLOCK:
            out += "</code></pre>"
        self.mode = PLAIN
        self.finished = True
        return out


def test():
    def parse(chunks):
        parser = Markdown()
        return "".join(parser.feed(chunk) for chunk in chunks) + parser.finish()

    # 行内代码：在每个位置切成两块，结果都一样
    text = "a`<x>`b"
    expected = "a<code>&lt;x&gt;</code>b"
    for cut in range(len(text) + 1):
        assert parse([text[:cut], text[cut:]]) == expected

    # 代码块：逐字符喂入，块内的单个反引号是普通字符
    text = "```x`y```"
    assert parse(list(text)) == "<pre><code>x`y</code></pre>"

    # 未闭合的代码在结束时自动闭合
    assert parse(["`unclosed"]) == "<code>unclosed</code>"

    # 普通文本也要转义
    assert parse(["<script>&"]) == "&lt;script&gt;&amp;"

    # 两个反引号不是标记，原样输出；空 chunk 无影响
    assert parse(["a``b", ""]) == "a``b"

    # finish 可重复调用，之后不能再 feed
    parser = Markdown()
    parser.feed("x")
    assert parser.finish() == ""
    assert parser.finish() == ""
    try:
        parser.feed("y")
    except ValueError:
        pass
    else:
        raise AssertionError("feed after finish should raise ValueError")


if __name__ == "__main__":
    test()
