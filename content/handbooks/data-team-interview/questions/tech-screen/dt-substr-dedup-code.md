---
id: dt-substr-dedup-code
section: tech-screen
order: 19
level: A
title: CoderPad：精确子串去重怎么写，滚动哈希怎么扫评测泄漏？
quick: "固定评测的字符或 token 窗口，用滚动哈希扫描训练文档，命中后比较原文以排除碰撞。窗口太短会误删常用代码，太长会漏变体；按域规范化。训练内部子串去重与评测隔离使用不同表和阈值。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Dedup
  - Rolling Hash
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: "The Pile: An 800GB Dataset of Diverse Text"
    url: https://arxiv.org/abs/2101.00027
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
---

把评测内容切成固定长度窗口，保存滚动哈希；训练文档也按相同窗口扫描，命中后比较原字符串，确认重叠再隔离。它能发现代码和数学的连续片段复制，弥补整篇精确哈希只能查全文相同的问题。CoderPad 可写滚动哈希，不必实现 DC3 后缀数组。

Lee et al. 2021 的精确子串用后缀数组找重复片段。现场滚动哈希扫冻结评测就够。和 `dt-ngram-contam-code` 叠：那边是词 13-gram，这边是字符或 token 窗口。

## Rabin-Karp 滚评测窗口

窗口 $L=50$ 字符（或 50 个 token）。评测量级允许把哈希放进 `set`。碰撞用「再比字符串」复核，不要只信哈希。

```python
def rolling_hashes(text, L=50, base=911382323, mod=10**18 + 3):
    """Rabin-Karp：返回每个长度 L 窗口的哈希，第 i 个对应 text[i:i + L]。"""
    if L <= 0:
        raise ValueError("L must be positive")
    if len(text) < L:
        return []
    h = 0
    high = 1  # base ** (L - 1) % mod，用来移出窗口最左边的字符
    for i in range(L):
        h = (h * base + ord(text[i])) % mod
        if i < L - 1:
            high = (high * base) % mod
    hashes = [h]
    for i in range(L, len(text)):
        h = (h - ord(text[i - L]) * high) % mod
        h = (h * base + ord(text[i])) % mod
        hashes.append(h)
    return hashes


def eval_windows(eval_items, L=50):
    """eval_items: list[(eval_id, text)]。返回 hash -> [(eval_id, 起点, 原文片段)]，片段用于碰撞复核。"""
    table = {}
    for eval_id, text in eval_items:
        for i, h in enumerate(rolling_hashes(text, L)):
            table.setdefault(h, []).append((eval_id, i, text[i:i + L]))
    return table


def scan(text, table, L=50):
    """返回 [(eval_id, 训练文本起点, 评测文本起点)]；哈希命中后再比原文。"""
    hits = []
    for i, h in enumerate(rolling_hashes(text, L)):
        for eval_id, j, fragment in table.get(h, ()):
            if text[i:i + L] == fragment:
                hits.append((eval_id, i, j))
                break
    return hits
```

### 可执行测试

```python
# 滚动哈希和逐窗口重算的结果一致
sample = "def add(a, b):\n    return a + b\n"
recomputed = [rolling_hashes(sample[i:i + 8], L=8)[0] for i in range(len(sample) - 7)]
assert rolling_hashes(sample, L=8) == recomputed

# 短于窗口的文本没有窗口
assert rolling_hashes("short", L=50) == []

# 训练文档里嵌了一段评测代码：命中位置对得上
eval_code = "def two_sum(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n"
table = eval_windows([("he-1", eval_code)], L=20)
train_doc = "# copied from somewhere\n" + eval_code + "# end"
hits = scan(train_doc, table, L=20)
assert hits[0] == ("he-1", len("# copied from somewhere\n"), 0)
assert len(hits) == len(eval_code) - 20 + 1

# 无关文档不命中
assert scan("print('hello world, this is unrelated code')", table, L=20) == []

# 哈希碰撞会被原文复核挡掉：人为塞一个错误片段
fake_table = {h: [("fake", 0, "x" * 20)] for h in rolling_hashes(train_doc, L=20)}
assert scan(train_doc, fake_table, L=20) == []
```

$L$ 太短误杀 `for (int i = 0;`。太长漏改空白。代码评测 $L$ 用 token 窗口更稳，先 `tokenize` 再滚。

训练内部精确子串去重（丢掉彼此重复的 50-token 片段）是另一件事：后缀数组 / 大规模哈希表，Lee 的论文主结果。现场说：对评测用这份扫描；对训练内部去重，按域做，许可证和常见头文件白名单。

## 泄漏之后

命中的训练文档进 quarantine。评测题留下。代码题还要查同仓库的测试文件、issue 正文，见 `dt-code-bench-bleed`。时间切的新题（LiveCodeBench）用来确认旧题高是不是泄漏。

空白和大小写：滚之前走 `dt-unicode-canon-code`，但代码不要 `lower` 掉标识符差异。按数据类型选择规范化（canon）规则。

## 追问

- **模数碰撞？** 双哈希或命中后比原文。评测集合小，复核便宜。
- **训练内部也滚 50-gram？** 可以，但是另一张表、另一个阈值。别和评测指纹混用。
- **窗口重叠会重复报同一题？** 按 `eval_id` 去重 hits 再决策。连续 20 个窗口命中同一题，比命中 1 次更像整段抄。
