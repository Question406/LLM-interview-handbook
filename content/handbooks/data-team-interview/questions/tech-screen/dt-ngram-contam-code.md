---
id: dt-ngram-contam-code
section: tech-screen
order: 8
level: S
title: CoderPad：对着冻结评测建 13-gram 倒排，训练文档怎么 quarantine？
quick: >-
  我会把评测题面切 13-gram 进倒排。训练文档每个 gram 查表，命中数过阈值就进 quarantine，不要当场从评测里删题。
  口播要能说改写数字会漏，所以还要 URL 和嵌入近邻，见 `dt-contamination`。
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
updatedAt: 2026-10-12
sources:
  - title: "The Pile: An 800GB Dataset of Diverse Text"
    url: https://arxiv.org/abs/2101.00027
    type: primary
  - title: Language Models are Few-Shot Learners
    url: https://arxiv.org/abs/2005.14165
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
---

把评测题面拆成连续 13 个词的片段，建立倒排索引。训练文档逐个片段查表，命中次数超过阈值就隔离检查。不要当场从评测里删题，也别对整题 `if text in train`。Panel 的 `dt-contamination` 问查到了怎么办；这里把「查」落成函数。

GPT-3 / The Pile 公开用过 13-gram 重叠。现场 $n=13$ 够用。单位是词，代码和数学可以改用 token 或字符 n-gram，否则 `i+1` 和 `i + 1` 对不上。倒排建在评测上，因为评测量级是千到万，训练是十亿。反过来建不动。

## 先冻评测，再扫训练

```python
from collections import defaultdict


def grams(text, n=13):
    """连续 n 个词的片段。短于 n 个词的文本整体当一个 gram。"""
    tokens = text.lower().split()
    if len(tokens) < n:
        return [" ".join(tokens)] if tokens else []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


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

### 可执行测试

```python
question = "a train leaves the station at noon traveling at sixty miles per hour toward the city"
other_question = "what is the capital of france and why did it become the capital so long ago"
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

代码之外，还要说明阈值、规模和命中后的处理：

1. 阈值。短评测题总共没有 13 个词，`grams` 会退成整句。这种题改用 $n=8$ 或字符 50-gram。`min_hits=1` 对长网页会误杀（题面里的习语），高价值评测可以 1，bulk crawl 可以要求连续命中。
2. 规模。评测 1 万题、每题 200 gram，倒排大约百万键，内存里扛得住。训练侧是 map：每份 shard 只读这份倒排，命中写 quarantine 表。不要把训练 gram 收集齐再 join。
3. 处理。命中的是**训练文档**进 quarantine。评测题留在门禁。把题删了，你只是看不见泄漏。

## 哪些泄漏可能漏检

改数字、换变量名、翻译成另一语，词 13-gram 会漏。还需要检查 URL 和仓库路径，再用题面 embedding 近邻补充检查，见 `dt-contamination`。合成数据用同一教师出训练和评测，n-gram 可能全空，那是 `dt-self-improve` 的自污染。

和精确去重的顺序：训练内部 `dt-exact-dedup-code` 去复制；本函数只对冻结评测。两套指纹表，别混成一张 `seen`。

## 追问

- **为什么是 13？** 公开惯例。更短误杀习语，更长漏改写。按域扫 $n\in\{8,13,50\}$，抽查看。
- **命中 1 个 gram 就扔？** 许可证、公式、`for i in range` 会误杀。按评测 id 聚合，再人工看 top 命中。代码评测用 `dt-substr-dedup-code` 更稳。
- **查到了还在旧题上 监督微调（SFT）？** 旧题不能再作为独立发布检查。可将其降为开发集，发布检查改用按时间隔离的新题，见 `dt-contamination`。
