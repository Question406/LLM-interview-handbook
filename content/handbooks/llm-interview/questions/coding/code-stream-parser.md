---
id: code-stream-parser
section: coding
order: 7
level: S
title: 真题：Streaming Parser 中 think/tool tag 可能跨 chunk，怎么写？
quick: >-
  用有限状态机记录当前在哪种内容里，再用一个 pending suffix buffer 暂存可能还没收完的标签。每次只输出确定不可能构成 tag 的前缀，把最长的「可能是 tag 前缀」的 suffix 留给下一个 chunk。对整个缓冲做一次 replace 或 regex，会被切成两半的 tag 骗过去。
tags:
  - Agent
  - Parser
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 智谱 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/24952c828c59435abd3c302c97fa358d'
    type: legacy-reference
---

## 题目描述

实现流式文本解析器 `StreamParser`，隐藏 `<think>` 与 `</think>` 之间的内容，同时保留标签之外的普通文本。输入可能在标签中间任意分块，标签本身也不应出现在可见输出中。

### 接口与约定

`feed(chunk) -> str` 接受下一个字符串块，返回这次已经能确定为可见内容的部分。多次调用共用解析状态；把所有返回值按顺序连接，就是目前已经确定的可见输出。可能是未完整标签前缀的末尾字符允许暂缓返回，等待后续块补全。

本练习处理大小写严格匹配、非嵌套且顺序合法的 think 标签；流中的真实标签会被完整提供。每条独立流使用新对象，不要求实现工具执行、JSON 校验或额外 flush 方法。

### 示例

```text
chunks=["A<th", "ink>secret</thi", "nk>B"]
依次feed返回["A", "", "B"]，拼接结果为"AB"

把完整字符串"A<think>secret</think>B"一次feed，返回"AB"
```

隐藏内容不得因跨块边界而泄漏到输出。

<!-- problem-statement:end -->

<h2>解题思路与参考答案</h2>

<div class="quick"><div class="mini-title">30 秒回答</div><p>用有限状态机记录当前在哪种内容里，再用一个 pending suffix buffer 暂存可能还没收完的标签。每次只输出确定不可能构成 tag 的前缀，把最长的「可能是 tag 前缀」的 suffix 留给下一个 chunk。对整个缓冲做一次 replace 或 regex，会被切成两半的 tag 骗过去。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>思路是状态机加一个待定缓冲。比如 <code>&lt;think&gt;</code> 被切成 <code>...&lt;thi</code> 和 <code>nk&gt;...</code> 两个 chunk 到达，第一个 chunk 末尾的 <code>&lt;thi</code> 有可能是标签开头，就先扣在 buf 里不输出，等下一个 chunk 拼上再判断。每次 feed 时，在 buf 里找当前状态在等的那个 tag：找到就切换状态；找不到就算出最长的「可能是 tag 前缀」的后缀留下，前面的部分在 NORMAL 状态下输出，在 IN_THINK 状态下丢掉。</p><pre><code data-lang="python">class StreamParser:
    def __init__(self):
        self.state = &quot;NORMAL&quot;
        self.buf = &quot;&quot;
        self.open_think = &quot;&lt;think&gt;&quot;
        self.close_think = &quot;&lt;/think&gt;&quot;

    def feed(self, chunk):
        self.buf += chunk
        out = []
        while self.buf:
            tag = self.open_think if self.state == &quot;NORMAL&quot; else self.close_think
            pos = self.buf.find(tag)
            if pos &gt;= 0:
                if self.state == &quot;NORMAL&quot;:
                    out.append(self.buf[:pos])
                    self.buf = self.buf[pos + len(tag):]
                    self.state = &quot;IN_THINK&quot;
                else:
                    self.buf = self.buf[pos + len(tag):]
                    self.state = &quot;NORMAL&quot;
                continue

            # keep the longest suffix that could be a prefix of the target tag
            keep = 0
            for k in range(1, min(len(tag), len(self.buf)) + 1):
                if tag.startswith(self.buf[-k:]):
                    keep = k
            safe = self.buf[:-keep] if keep else self.buf
            if self.state == &quot;NORMAL&quot;:
                out.append(safe)
            self.buf = self.buf[-keep:] if keep else &quot;&quot;
            break
        return &quot;&quot;.join(out)</code></pre><p>真实题往往还要求 tool-call payload 只展示某些字段。这时把 NORMAL / IN_THINK / IN_TOOL / TOOL_JSON 这些状态分开，JSON 部分交给 streaming JSON parser，别再对 JSON 字符串写一套脆弱的 regex。</p><p>如果底层网络传的是 bytes，还要先过一层 incremental UTF-8 decoder，免得一个中文字符的多字节序列被 chunk 切开。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么普通 regex 不够？</summary><div class="follow-answer"><p>因为 streaming 时 opening 或 closing tag 可能只到了半截。正则处理完整字符串没问题，跨 chunk 就得自己保留状态。</p></div></details><details class="followup"><summary>Tool JSON 中出现 &quot;&lt;/think&gt;&quot; 字符串怎么办？</summary><div class="follow-answer"><p>Parser 要知道自己在哪个语法层级。进了 JSON 或 tool payload 以后，字符串里的内容就不该再按顶层 tag 解释。更稳的做法是用协议级 framing，别把它混在文本 tag 里。</p></div></details></div>

          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/24952c828c59435abd3c302c97fa358d" target="_blank" rel="noopener noreferrer">↗ 智谱 Agent 面经</a></div>

<h2>简单测试怎么写</h2>
<p>把上面的实现保存为 solution.py，以下测试放在实现之后。运行 python3 solution.py，成功时输出 simple tests passed，失败时按断言报错行定位。不要加 -O，它会跳过 assert。</p>
<p>把同一段标签拆在不同 chunk 中，拼接每次 feed 的输出。完整输入和逐字符输入都应只留下 AB，专门检查跨块标签识别。</p>
<pre><code class="language-python">for chunks in [[&quot;A&lt;think&gt;secret&lt;/think&gt;B&quot;],
               [&quot;A&lt;th&quot;, &quot;ink&gt;secret&lt;/thi&quot;, &quot;nk&gt;B&quot;],
               list(&quot;A&lt;think&gt;secret&lt;/think&gt;B&quot;)]:
    parser = StreamParser()
    assert &quot;&quot;.join(parser.feed(chunk) for chunk in chunks) == &quot;AB&quot;
print(&quot;simple tests passed&quot;)
</code></pre>
