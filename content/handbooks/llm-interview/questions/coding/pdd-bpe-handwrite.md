---
id: pdd-bpe-handwrite
section: coding
order: 182
level: A
title: 拼多多暑期实习：如何模拟 BPE，暴力实现之后还能怎么优化？
quick: >-
  先按字符切分，反复统计相邻 pair 频次，合并最高频 pair 直到词表预算。暴力每轮扫全语料；优化用 pair
  优先队列、倒排到出现位置，以及预分词 / 缓存 merge 规则。
tags:
  - PDD
  - BPE
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多暑期实习二面
    url: https://www.nowcoder.com/feed/main/detail/6052afa2fbd54b0f997385e8e0ae4dcc
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：算法工程师；暑期实习
- 届别 / 流程：二面
- 面试时间：原帖未披露；帖子发布于 2026-03-25
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“算法题：模拟BPE的实现。追问有没有优化的方法（我写的太暴力了）。”**

错法：把 BPE 讲成语言学切词，或每轮对整语料 $O(n)$ 扫却说不出优化。BPE 是数据驱动的相邻合并：训练产出有序 merge 表，编码时套同一张表。中英混合先走 byte 级，避免未知字符把序列打散。原帖明确追问暴力之后怎么快。
## 暴力训练：统计 pair → 合并最高频

语料预分成字符（或 byte）序列，词尾可加结束标记 `EOW`（文献里常写成斜杠 w）。每轮数相邻 pair，合并全局最高频，更新词表与所有序列，重复直到 merge 次数或词表预算。平手时规定打破规则（字典序），否则不稳定。

```python
from collections import Counter

def bpe_train(words, num_merges):
    corpus = [list(w) + ["EOW"] for w in words]
    merges = []
    for _ in range(num_merges):
        pairs = Counter()
        for seq in corpus:
            pairs.update(zip(seq, seq[1:]))
        if not pairs:
            break
        a, b = max(pairs, key=lambda p: (pairs[p], p))
        merges.append((a, b))
        nxt = []
        for seq in corpus:
            i, out = 0, []
            while i < len(seq):
                if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
                    out.append(a + b)
                    i += 2
                else:
                    out.append(seq[i])
                    i += 1
            nxt.append(out)
        corpus = nxt
    return merges
```

编码：对输入按 merge 学到的顺序反复合并，直到不能再合。不要每步重新数全局频次，那是训练，不是 encode。复杂度训练约 $O(\text{rounds}\times\text{tokens})$。

## 优化：堆、局部更新、rank 扫描

- 堆维护 pair 频次：不要每轮全表 `max`。合并后只改被触及的相邻 pair。
- 倒排到出现位置：pair → 在哪些词、哪些下标出现；只重写那些词。
- 词频压缩：相同词只存一份乘次数，语料去重后快一个数量级。
- encode：把 merge 做成 rank 数组，对 token 序列线性扫描（类似 HuggingFace tokenizers），不要每步 $O(\text{merges})$ 暴力找。

面试补：BPE 不是 WordPiece 的「整词表 softmax 切」，也不是 Unigram 的损失最小化。生产用预分词（空格）再 BPE。优化说清「只更新邻居 + 堆」，比改写成 C++ 更对题。

## 追问

- **频次并列选谁？** 必须固定 tie-break，否则词表不可复现。
- **为什么 encode 不用频次？** 频次只指导训练时的合并顺序；推理只回放该顺序。
- **byte 级解决什么？** 任意 Unicode 可切，无 UNK；中英混合不会因单字不在词表而碎成未知。
- **和 SentencePiece？** SP 常用 Unigram；BPE 是 merge 过程。不要混实现。
- **堆的懒删除？** pair 频次过期时不立刻删堆，弹出时若 count 对不上就跳过。这是常见实现。
