---
id: dt-ngram-contam-code
section: tech-screen
order: 8
level: S
title: CoderPad：对着冻结评测建 13-gram 倒排，训练文档怎么 quarantine？
quick: >-
  把评测题面切成 13-gram 建倒排索引，训练文档逐个 gram 查表，命中数过阈值的训练文档进 quarantine，评测题留着不删。改写数字或翻译会让
  n-gram false negative，所以还要配合 URL 检查和 embedding nearest neighbors，见
  `dt-contamination`。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Contamination
  - N-gram
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'The Pile: An 800GB Dataset of Diverse Text'
    url: 'https://arxiv.org/abs/2101.00027'
    type: primary
  - title: Language Models are Few-Shot Learners
    url: 'https://arxiv.org/abs/2005.14165'
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

给定一份冻结评测题目集合和待进入训练的文档，检测训练文档是否包含评测的连续词片段，输出应隔离的文档及命中题目。这是精确文本重合检测，不做语义相似度推断。

### 输入与接口

- `grams(text,n=13)` 将文本转小写后按空白切词，返回所有连续 n 词片段列表；非空且短于 n 词时整句作为一个片段。
- `build_eval_index(eval_items,n=13)` 接受 `(eval_id,text)` 列表。
- `scan_doc(doc_id,text,index,n=13,min_hits=1)` 扫描一篇训练文档，n 与建索引时一致。

### 输出与约束

索引为 `gram -> eval_id集合`。扫描结果为 `{"doc_id":ID,"quarantine":bool,"hits":[(eval_id,count),...]}`；只列出 count 达到 `min_hits` 的题，按 count 降序、同分按 `eval_id` 升序排序。

同一 gram 可以属于多道评测题。训练文档中重复出现同一 gram 时按出现次数累计命中；一旦存在达到 threshold 的题，quarantine 为 True。空文本没有片段。

### 示例

```text
index=build_eval_index([("q1","A B C D")],n=2)
scan_doc("d1","x a b c y",index,n=2)
-> {"doc_id":"d1","quarantine":True,"hits":[("q1",2)]}
scan_doc("d2","x y",index,n=2)
-> {"doc_id":"d2","quarantine":False,"hits":[]}
```

## 解题思路与参考答案

我会把评测题面切成连续 13 个词的片段建倒排索引，训练文档逐个片段查表，命中次数超过阈值就把这篇训练文档隔离检查。整题做 `if text in train` 太容易漏，当场从评测里删题也不对。`dt-contamination` 是 Panel 版，问的是查到之后怎么办；这里要把「查」写成函数。

比如有篇博客原样抄了一道题「a train leaves the station at noon traveling at sixty miles per hour toward the city」，后面跟着答案。它的每个 13-gram 都会命中这道题，这篇博客就该进 quarantine。

倒排建在评测侧，因为评测是千到万的量级，训练是十亿级，反过来建不动。$n=13$ 是 GPT-3 和 The Pile 公开用过的重叠长度，现场用它就够。单位是词；代码和数学可以改用 token 或字符 n-gram，不然 `i+1` 和 `i + 1` 对不上。

## 先冻评测，再扫训练

```python
from collections import defaultdict


def grams(text, n=13):
    """连续 n 个词的片段。短于 n 个词的文本整体当一个 gram。"""
    tokens = text.lower().split()
    if len(tokens) < n:
        return [" ".join(tokens)] if tokens else []
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def build_eval_index(eval_items, n=13):
    """eval_items: list[(eval_id, text)]。返回 gram -> {eval_id}，一个 gram 可能属于多题。"""
    index = defaultdict(set)
    for eval_id, text in eval_items:
        for gram in grams(text, n):
            index[gram].add(eval_id)
    return index


def scan_doc(doc_id, text, index, n=13, min_hits=1):
    """统计训练文档命中每道评测题的 gram 数，达到 min_hits 的题按命中数降序列出。"""
    hits = defaultdict(int)
    for gram in grams(text, n):
        for eval_id in index.get(gram, ()):
            hits[eval_id] += 1
    flagged = sorted(
        ((eval_id, count) for eval_id, count in hits.items() if count >= min_hits),
        key=lambda item: (-item[1], item[0]),
    )
    return {"doc_id": doc_id, "quarantine": bool(flagged), "hits": flagged}
```

测试覆盖原样 leakage、无关文档、大小写、`min_hits` 和短题：

```python
question = "a train leaves the station at noon traveling at sixty miles per hour toward the city"
other_question = (
    "what is the capital of france and why did it become the capital so long ago"
)
index = build_eval_index([("q1", question), ("q2", other_question)])

# 训练文档原样包含评测题面：命中并进 quarantine
leaked = "blog post: " + question + " the answer is two hours"
result = scan_doc("doc-1", leaked, index)
assert result["quarantine"]
assert result["hits"][0][0] == "q1"
assert result["hits"][0][1] == len(grams(question))

# 无关文档不命中
clean = scan_doc("doc-2", "completely unrelated text about cooking pasta " * 3, index)
assert clean == {"doc_id": "doc-2", "quarantine": False, "hits": []}

# 大小写不影响匹配
assert scan_doc("doc-3", question.upper(), index)["quarantine"]

# min_hits 提高后，只命中一个 gram 的文档不再被标记
one_gram = " ".join(question.split()[:13])
assert scan_doc("doc-4", one_gram, index, min_hits=1)["quarantine"]
assert not scan_doc("doc-4", one_gram, index, min_hits=2)["quarantine"]

# 短评测题退化成整句一个 gram
assert grams("short question", n=13) == ["short question"]
```

写完我会接着讲阈值、规模和命中后怎么处理。短题总共不到 13 个词，`grams` 会退化成整句，这类题改用 $n=8$ 或字符 50-gram；`min_hits=1` 在长网页上会 false rejection 题面里的习语，高价值评测可以用 1，bulk crawl 可以要求连续命中。规模上，评测 1 万题、每题 200 个 gram，倒排大约百万个键，放内存没问题；训练侧做成 map，每个 shard 只读这份倒排，命中写进 quarantine 表，别先把训练侧的 gram 收集齐再 join。命中之后进 quarantine 的是**训练文档**，评测题留在 evaluation gate 里，把题删了，你只是看不见 leakage。

它和 exact deduplication 是两件事。training set 内部用 `dt-exact-dedup-code` 去复制，这个函数只针对冻结评测，两套指纹表别混成一张 `seen`。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert result["quarantine"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条 assertion 都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**为什么是 13？**
这是公开惯例。更短会 false rejection 习语，更长会漏掉改写。可以按域扫 $n\in\{8,13,50\}$，抽查结果再定。

**命中 1 个 gram 就扔？**
许可证、公式、`for i in range` 都会被 false rejection。按评测 id 聚合，再人工看命中最多的那些。代码评测用 `dt-substr-dedup-code` 更稳。

**改了数字或者翻译过的题怎么办？**
词级 13-gram 会漏。还要检查 URL 和仓库路径，再用题面 embedding nearest neighbors 补一层，见 `dt-contamination`。同一个 teacher model 既出训练数据又出评测时，n-gram 可能一个都不命中，那属于 `dt-self-improve` 讲的自 contamination。

**查到 leakage 了，还在旧题上做 SFT 怎么办？**
旧题不能再当独立的发布检查。可以降为 development set，发布检查改用按时间隔离的新题，见 `dt-contamination`。

相关：`dt-contamination`、`dt-exact-dedup-code`、`dt-substr-dedup-code`、`dt-self-improve`
