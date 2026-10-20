---
id: code-stream-parser
section: coding
order: 7
level: S
title: 真题：Streaming Parser 中 think/tool tag 可能跨 chunk，怎么写？
quick: >-
  不能对整个缓冲做一次 replace 或 regex。需要用有限状态机记录当前处于哪种内容，再用 pending suffix buffer 暂存可能尚未接收完整的标签。只消费已经确定不可能构成 tag
  的前缀，把最长「可能是 tag 前缀」的 suffix 留给下一个 chunk。
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>不能对整个缓冲做一次 replace 或 regex。需要用有限状态机记录当前处于哪种内容，再用 pending suffix buffer 暂存可能尚未接收完整的标签。只消费已经确定不可能构成 tag 的前缀，把最长「可能是 tag 前缀」的 suffix 留给下一个 chunk。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><pre><code data-lang="python">class StreamParser:
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
        return &quot;&quot;.join(out)</code></pre><p>真实题往往还要求 tool-call payload 只展示某些字段。这时应把 NORMAL / IN_THINK / IN_TOOL / TOOL_JSON 这些状态分开，并用 streaming JSON parser，别对 JSON 字符串再写一套脆弱 regex。</p><p>如果底层网络传的是 bytes，要先用 incremental UTF-8 decoder，避免一个中文字符的多字节序列被 chunk 切开。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么普通 regex 不够？</summary><div class="follow-answer"><p>正则可以处理完整字符串，但 streaming 时 closing 或 opening tag 可能只出现半截，必须保留跨 chunk 的状态。</p></div></details><details class="followup"><summary>Tool JSON 中出现 &quot;&lt;/think&gt;&quot; 字符串怎么办？</summary><div class="follow-answer"><p>Parser 必须知道当前语法层级。进了 JSON 或 tool payload 之后，不该把普通字符串内容按顶层 tag 解释。最好用协议级 framing，别混在文本 tag 里。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/24952c828c59435abd3c302c97fa358d" target="_blank" rel="noopener noreferrer">↗ 智谱 Agent 面经</a></div>
