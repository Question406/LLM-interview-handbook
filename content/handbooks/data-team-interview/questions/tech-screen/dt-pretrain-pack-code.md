---
id: dt-pretrain-pack-code
section: tech-screen
order: 21
level: A
title: CoderPad：预训练怎么把文档拼进固定长度，边界要不要断因果？
quick: "把文档贪心装进长度为 `seq_len` 的序列，文档之间插 BOS/EOS，在文档边界切断注意力，padding 不算 loss。这样算力不浪费在 pad 上，模型也不会跨篇续写。预训练一般监督文档里的大部分 token，SFT 还要按角色限制监督范围，见 `dt-packed-sft-code`。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Packing
  - Pretraining
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Efficient Sequence Packing without Cross-contamination"
    url: https://arxiv.org/abs/2107.02027
    type: primary
  - title: "LLaMA: Open and Efficient Foundation Language Models"
    url: https://arxiv.org/abs/2302.13971
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

将按给定顺序到来的文档 token 列表打包成固定长度的预训练序列，同时记录哪些位置参与损失及其文档来源。不能丢弃原文 token，也不能把文档边界伪装成同一文档。

### 输入与接口

- 实现 `pack_docs(docs,L,bos_id,eos_id,pad_id)`。docs 是 `list[list[int]]`，L 至少为 3。BOS、EOS、PAD 为互不相同且不与正文冲突的特殊 ID。
- 每篇文档或文档分片需要包上一个 BOS 和一个 EOS；正文超过 L-2 时按原顺序切成至多 L-2 的连续分片。

### 输出与约束

返回若干 `(input_ids,loss_mask,doc_ids)`，三者长度均为 L。正文和 BOS/EOS 的 `loss_mask` 为 1，padding 为 0；真实 token 的 `doc_ids` 为原文档下标，padding 为 -1。

按输入文档和分片顺序连续装入当前序列；下一个完整分片装不下时才开启新序列，不为了利用尾部空间再次拆分该分片。空文档仍贡献 BOS/EOS。每条序列的剩余位置补 PAD，输入列表不被修改。

### 示例

```text
pack_docs([[10,11],[20]],L=8,bos_id=1,eos_id=2,pad_id=0)
-> [([1,10,11,2,1,20,2,0],
     [1,1,1,1,1,1,1,0],
     [0,0,0,0,1,1,1,-1])]
```

## 解题思路与参考答案

我会把文档贪心装进长度为 `seq_len` 的序列，文档之间插 BOS/EOS，padding 不算 loss，同时记下每个 token 属于哪篇文档，用来在边界切断注意力。

为什么要 pack：短文档直接 pad 到 `seq_len` 会浪费 50% 的算力。为什么要切注意力：拼进同一个序列的文档仍然是各自独立的文章，比如一篇菜谱后面接一篇球赛新闻，注意力不断开，模型就会拿菜谱当球赛的上文。Efficient Sequence Packing without Cross-contamination 的结论是长度可以拼，注意力要在文档边界断掉，不然不同文档能相互读取，等于造了假的长上下文。

预训练一般对文档里的大部分 token 算交叉熵；哪些角色进 loss 是 SFT 的问题，见 `dt-packed-sft-code`。

## 贪心装箱，记下边界

输入的文档已经是 token id，目标长度是 $L$，当前桶装不下就封桶。超长文档切成长度 $L$ 的块，块之间仍插 EOS，免得一本技术手册变成没有句号的超长句。

```python
def pack_docs(docs, L, bos_id, eos_id, pad_id):
    """贪心把文档装进长度为 L 的序列。

    docs: list[list[int]]，每篇文档的 token id。
    返回 list[(input_ids, loss_mask, doc_ids)]，三者长度都是 L：
    loss_mask=1 的位置进 CE（含 BOS/EOS），pad 为 0；
    doc_ids 标出每个 token 属于第几篇文档，pad 为 -1，用来构造块对角 attention。
    超过 L-2 个 token 的文档切成多块，每块各自带 BOS/EOS。
    """
    if L < 3:
        raise ValueError("L must leave room for BOS, EOS and at least one token")
    sequences = []
    cur_ids, cur_mask, cur_doc = [], [], []

    def flush():
        nonlocal cur_ids, cur_mask, cur_doc
        if not cur_ids:
            return
        pad_n = L - len(cur_ids)
        cur_ids += [pad_id] * pad_n
        cur_mask += [0] * pad_n
        cur_doc += [-1] * pad_n
        sequences.append((cur_ids, cur_mask, cur_doc))
        cur_ids, cur_mask, cur_doc = [], [], []

    chunk_len = L - 2
    for doc_index, tokens in enumerate(docs):
        for start in range(0, max(len(tokens), 1), chunk_len):
            piece = [bos_id] + tokens[start:start + chunk_len] + [eos_id]
            if len(cur_ids) + len(piece) > L:
                flush()
            cur_ids.extend(piece)
            cur_mask.extend([1] * len(piece))
            cur_doc.extend([doc_index] * len(piece))
    flush()
    return sequences
```

测试覆盖同序列拼两篇、封桶、超长切块、长度和配置错误：

```python
BOS, EOS, PAD = 1, 2, 0

# 两篇短文档装进同一条序列，剩余位置 pad，pad 不进 loss
sequences = pack_docs([[10, 11], [20]], L=8, bos_id=BOS, eos_id=EOS, pad_id=PAD)
assert len(sequences) == 1
ids, mask, doc_ids = sequences[0]
assert ids == [BOS, 10, 11, EOS, BOS, 20, EOS, PAD]
assert mask == [1, 1, 1, 1, 1, 1, 1, 0]
assert doc_ids == [0, 0, 0, 0, 1, 1, 1, -1]

# 装不下时封桶，开新序列
sequences = pack_docs([[10, 11, 12], [20, 21, 22]], L=6, bos_id=BOS, eos_id=EOS, pad_id=PAD)
assert [seq[0] for seq in sequences] == [[BOS, 10, 11, 12, EOS, PAD], [BOS, 20, 21, 22, EOS, PAD]]

# 超长文档切成多块，不丢 token，每块都有 BOS/EOS
long_doc = list(range(100, 110))
sequences = pack_docs([long_doc], L=6, bos_id=BOS, eos_id=EOS, pad_id=PAD)
body = [t for ids, _, _ in sequences for t in ids if t not in (BOS, EOS, PAD)]
assert body == long_doc
assert all(ids[0] == BOS for ids, _, _ in sequences)

# 每条序列长度都是 L
assert all(len(ids) == len(mask) == len(doc) == 6 for ids, mask, doc in sequences)

# L 太小装不下 BOS/EOS 是配置错误
try:
    pack_docs([[1]], L=2, bos_id=BOS, eos_id=EOS, pad_id=PAD)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

装箱是一遍线性扫描。注意力的规则是每个位置只看得见 `doc_ids` 相同、时间步更早的 token，实现上可以用块对角的因果 mask，或者在边界把 KV 清掉。漏了这一步，模型会拿上一篇的结尾当下一篇的上文，短网页被拼成「假长上下文」；长上下文能力要用专门的数据来造，见 `dt-longctx-data`。BOS/EOS 进 loss，因为它们是文档边界的监督信号，pad 不进。

## 长度分布和占用率

只做贪心的话，长文档会剩下一截短尾巴，再和其他短文拼在一起。按长度降序 pack 能提高占用率，但会改变每个 batch 的域混合，所以配额采样要在 pack 之前做完（见 `dt-temp-mix-code`），pack 只负责把已经抽中的文档塞进 $L$，别在这里再按长度偏置一次。占用率要当场报出来，目标是 90% 以上，低于 80% 说明短文档太多，或者 $L$ 选错了。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert len(sequences) == 1` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**SFT 能用同一套 pack 吗？**
拼长度的逻辑可以复用，mask 完全不同，SFT 还要屏蔽 user 和 tool，见 `dt-packed-sft-code`。

**能不能故意打开跨文档可见？**
默认关。真要打开，必须当成一种显式声明的数据增强；跨文档拼接也会把评测泄漏一起带进来。

**EOS 和 pad 能用同一个 id 吗？**
不要，否则文档边界和空白就分不开了。

**占用率多少算正常？**
目标 90% 以上。低于 80% 说明短文档太多，或者 $L$ 选错了。

相关：`dt-packed-sft-code`、`dt-longctx-data`、`dt-temp-mix-code`
