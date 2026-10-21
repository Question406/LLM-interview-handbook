---
id: dt-substr-dedup-code
section: tech-screen
order: 19
level: A
title: CoderPad：精确子串去重怎么写，滚动哈希怎么扫评测泄漏？
quick: "把评测内容切成固定长度的字符或 token 窗口，用滚动哈希扫训练文档，命中后再比原文，排除哈希碰撞。它能发现整篇哈希漏掉的局部片段复制。窗口太短会误杀常见代码，太长会漏掉变体，规范化按域选；训练内部的子串去重和评测隔离用不同的表和阈值。"
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

整篇精确哈希只能查出全文相同的文档，代码和数学里常见的是连续片段被复制进别的文件。这题的做法是把评测内容切成固定长度的窗口，存下滚动哈希；训练文档按同样的窗口扫描，命中后再比较原字符串，确认真的重叠才隔离。CoderPad 上写滚动哈希就够，不必实现 DC3 后缀数组。

Lee et al. 2021 用后缀数组找精确重复子串，现场用滚动哈希扫冻结的评测集就可以。它和 `dt-ngram-contam-code` 是叠加关系：那边用词级 13-gram，这边用字符或 token 窗口。

## Rabin-Karp 滚评测窗口

窗口 $L=50$ 个字符（或 50 个 token）。评测的量级允许把哈希放进 `set`。哈希命中后再比一次原字符串，排除碰撞。

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

$L$ 的取舍：太短会误杀 `for (int i = 0;` 这种常见片段，太长又会漏掉改了空白的变体。代码评测用 token 窗口更稳，先 `tokenize` 再滚。

规范化也要按数据类型选。滚之前先过 `dt-unicode-canon-code` 处理空白和大小写，但代码不能 `lower`，否则会抹掉标识符的差异。

训练集内部的精确子串去重（丢掉彼此重复的 50-token 片段）是另一件事，那是 Lee 论文的主结果，要用后缀数组或大规模哈希表。现场可以这样分：对评测用这份扫描；训练内部去重按域做，许可证和常见头文件放白名单。

## 查到泄漏之后

命中的训练文档进 quarantine，评测题留下。代码题还要查同一仓库里的测试文件和 issue 正文，见 `dt-code-bench-bleed`。要确认旧题分数高是不是因为泄漏，可以用按时间切的新题（LiveCodeBench）对照。

## 追问

- **模数碰撞怎么办？** 用双哈希，或者命中后比原文。评测集小，复核很便宜。
- **训练集内部也滚 50-gram？** 可以，但要用另一张表、另一个阈值，不要和评测指纹混用。
- **窗口重叠会不会把同一题重复报很多次？** 先按 `eval_id` 对 hits 去重，再做决策。同一题连续 20 个窗口命中，比只命中 1 次更像整段抄袭。
