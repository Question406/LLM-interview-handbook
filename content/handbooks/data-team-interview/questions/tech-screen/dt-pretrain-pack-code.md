---
id: dt-pretrain-pack-code
section: tech-screen
order: 21
level: A
title: CoderPad：预训练怎么把文档拼进固定长度，边界要不要断因果？
quick: "把文档装入长度为 `seq_len` 的序列，插入 BOS/EOS 标记，并在文档边界切断注意力。padding 不计算 loss。预训练通常监督文档中的大部分 token，SFT 则还要按角色限制监督范围，见 `dt-packed-sft-code`。"
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

把文档贪心装入长度为 `seq_len` 的序列，文档之间插入 BOS/EOS，边界处切断 attention，padding 不计算 loss。预训练一般计算文档中大部分 token 的交叉熵，但不同文档不能相互读取。`dt-packed-sft-code` 问哪些角色进 loss。短文档直接 pad 会浪费 50% 算力；别把两篇文章拼成一篇新文章让模型跨篇续写。

Efficient Sequence Packing without Cross-contamination：拼长度可以，注意力要在文档边界断掉，否则等于造假长上下文。

## 贪心装箱，记下边界

文档已经是 token id。目标长度 $L$。当前桶装不下就封桶。超长文档切成 $L$ 块，块间仍插 EOS，避免一本技术手册变成没有句号的超长句。

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

### 可执行测试

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

Attention：同一位置只看见 `doc_ids` 相同且时间步更早的 token。实现可以是块对角因果 mask，或在边界把 KV 清掉。漏了这一步，模型会用上一篇的结尾当下一篇的上文，短网页被错误拼接成「假长上下文」。长上下文能力另用专门数据造，见 `dt-longctx-data`。

BOS/EOS 进不进 loss：进。它们是文档边界的监督。Pad 不进。

## 长度分布

只贪心会把长文档剩下一截短尾巴，尾巴再和其他短文拼。按长度降序 pack 能提高占用，但会改变每个 batch 的域混合。配额采样要在 pack 之前做完，见 `dt-temp-mix-code`。pack 只是把已抽中的文档塞进 $L$，不要在这里再按长度偏置一次。

占用率当场报：目标 >90%。低于 80% 说明短文档太多或 $L$ 选错。

## 追问

- **监督微调（SFT） 能不能同一套 pack？** 能拼长度，mask 完全不同。SFT 还要断 user/tool，见 `dt-packed-sft-code`。
- **跨文档可见有人故意开？** 当数据增强要显式声明，默认关。评测泄漏也会跨拼进来。
- **EOS 和 pad 同一个 id？** 不要。否则边界和空白分不开。
